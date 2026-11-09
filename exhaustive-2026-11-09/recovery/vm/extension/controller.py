import gzip
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import time
import oracle

ROOT = Path("/lab/extension")
OUT = ROOT / "results"
MAX_BYTES = 192 * 1024 * 1024


def sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(path.parent)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1048576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_disk(disk, target):
    expected = sha(disk)
    with disk.open("rb") as source, gzip.open(target, "xb", compresslevel=1) as archive:
        shutil.copyfileobj(source, archive, 1048576)
    digest = hashlib.sha256()
    with gzip.open(target, "rb") as archive:
        for chunk in iter(lambda:archive.read(1048576), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected:
        raise RuntimeError("disk_archive_verification_failed")
    with target.open("rb") as archive:
        os.fsync(archive.fileno())
    sync_directory(target.parent)
    return dict(raw_sha256=expected, gzip_sha256=sha(target), gzip_bytes=target.stat().st_size,
                lossless_verified=True, path=target.name)


def boot(disk, phase, log):
    command = ["qemu-system-aarch64", "-machine", "virt", "-cpu", "cortex-a57", "-accel", "tcg",
               "-smp", "1", "-m", "256M", "-nographic", "-no-reboot", "-nic", "none",
               "-kernel", "/lab/boot/Image-virt", "-initrd", str(ROOT / "test-initramfs.gz"),
               "-append", "console=ttyAMA0 panic=-1 phase=" + phase,
               "-drive", "if=none,file=" + str(disk) + ",format=raw,cache=writeback,id=d0",
               "-device", "virtio-blk-device,drive=d0"]
    save(log.with_suffix(".intent.json"), dict(command=command, phase=phase, utc_seconds=time.time()))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    clean = phase == "recover-clean"
    target = b"BARRIER " + (b"CLEAN_INSPECTOR_UNMOUNTED" if clean else b"RECOVERED" if phase == "recover" else b"CUT" + phase.encode())
    data, reached = b"", False
    deadline = time.monotonic() + 60
    with log.open("xb") as stream:
        try:
            while time.monotonic() < deadline:
                ready, _, _ = select.select([process.stdout], [], [], 1)
                if ready:
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        break
                    data += chunk
                    stream.write(chunk)
                    stream.flush()
                    if target + b"\r\n" in data or target + b"\n" in data:
                        reached = True
                        break
                if process.poll() is not None:
                    break
        finally:
            if clean and reached:
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
            elif process.poll() is None:
                process.kill()
            result = process.wait(timeout=10)
            rest = process.stdout.read()
            stream.write(rest)
            data += rest
            stream.flush()
            os.fsync(stream.fileno())
    save(log.with_suffix(".receipt.json"), dict(pid=process.pid, exit=result, barrier=target.decode(),
         reached=reached, bytes=len(data), natural_shutdown=clean and result==0,
         failure_boundary="Owned QEMU guest only; outer container/host/device caches survive"))
    if not reached:
        raise RuntimeError("guest_barrier_not_reached:" + log.name)
    if clean and result != 0:
        raise RuntimeError("clean_inspector_did_not_shutdown_normally")
    return data.decode(errors="replace")


def inspect_fs(disk, name):
    result = subprocess.run(["e2fsck", "-fn", str(disk)], capture_output=True, text=True)
    raw = dict(exit=result.returncode, stdout=result.stdout, stderr=result.stderr, repair=False)
    raw["diagnostics"] = oracle.fsck_diagnostics(raw)
    save(OUT / (name + "-fsck.json"), raw)
    return raw


def main():
    OUT.mkdir(exist_ok=False)
    sync_directory(OUT.parent)
    base = OUT / "base.raw"
    with base.open("xb") as stream:
        stream.truncate(32 * 1024 * 1024)
    make = subprocess.run(["mkfs.ext4", "-F", "-b", "4096", str(base)], capture_output=True, text=True)
    save(OUT / "filesystem-creation.json", dict(exit=make.returncode, stdout=make.stdout, stderr=make.stderr))
    make.check_returncode()
    cases = []
    for stage in range(1,13):
        total = sum(path.stat().st_size for path in ROOT.rglob("*") if path.is_file() and not path.is_symlink())
        if total + 32 * 1024 * 1024 > MAX_BYTES:
            raise RuntimeError("extension_storage_budget_would_be_exceeded")
        name = "case-" + str(stage)
        disk = OUT / (name + ".raw")
        shutil.copyfile(base, disk)
        boot(disk, str(stage), OUT / (name + "-cut.log"))
        before = archive_disk(disk, OUT / (name + "-pre-inspection.raw.gz"))
        recovered = boot(disk, "recover", OUT / (name + "-recover.log"))
        records = oracle.parse(recovered)
        verdict = oracle.check_case(stage, records)
        fsck = inspect_fs(disk, name + "-after-rw-replay-and-second-cut")
        after = archive_disk(disk, OUT / (name + "-post-inspection.raw.gz"))
        row = dict(stage=stage, verdict=verdict, pre_inspection=before, post_inspection=after,
                   files={key:None if value is None else dict(bytes=len(value),sha256=hashlib.sha256(value).hexdigest()) for key,value in records.items()},
                   fsck=fsck, injected_bad_control=stage in (5,6,11,12),
                   inspector="rw mount/journal replay, read records, second emulator SIGKILL; fsck afterward")
        save(OUT / (name + "-result.json"), row)
        cases.append(row)
        disk.unlink()
        print(json.dumps(dict(stage=stage,kind=verdict["verdict"]["kind"],expected=verdict["expected"],fsck_diagnostics=fsck["diagnostics"])),flush=True)
    clean_disk = OUT / "clean-inspector-control.raw"
    with gzip.open(OUT / "case-4-pre-inspection.raw.gz", "rb") as source, clean_disk.open("xb") as destination:
        shutil.copyfileobj(source,destination,1048576)
    clean_records = oracle.parse(boot(clean_disk,"recover-clean",OUT / "clean-inspector-control.log"))
    clean_fsck = inspect_fs(clean_disk,"clean-inspector-control")
    control = dict(records=oracle.check_case(4,clean_records),fsck=clean_fsck,
                   archive=archive_disk(clean_disk,OUT / "clean-inspector-post.raw.gz"),
                   boundary="rw journal replay then successful guest umount and poweroff; no inspector SIGKILL")
    clean_disk.unlink()
    save(OUT / "clean-inspector-control.json",control)
    report = dict(cases=cases, clean_inspector_control=control,
                  all_expected=all(case["verdict"]["expected"] for case in cases),
                  clean_inspector_expected=control["records"]["expected"] and clean_fsck["diagnostics"]["clean_diagnostics"],
                  planned_boots=25, payload_bytes=oracle.SIZE,
                  limits="Twelve single trials; file/JSON proxy protocol, not Git or production GHerrit; guest emulator cut only; outer caches survive")
    save(OUT / "RESULTS.json",report)
    if not report["all_expected"] or not report["clean_inspector_expected"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
