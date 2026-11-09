"""ROOT-ONLY recipe. No install, download, compiler, VM or guest disk effects."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import sysconfig

ROOT = Path("/lab/protocol-guest")
STAGE_LIMIT = 96 * 1024 * 1024
INITRD_LIMIT = 48 * 1024 * 1024
LAB_LIMIT = 2 * 1024 * 1024 * 1024


def file_bytes(root):
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file() and not path.is_symlink())


def ldd_paths(text):
    if "not found" in text:
        raise RuntimeError("unresolved_ldd_dependency")
    return {Path(path) for path in re.findall(r"(?:=>\s+|^\s*)(/[^\s()]+)", text, re.MULTILINE)}


def copy_absolute(source, stage):
    source = Path(source)
    target = stage / source.relative_to("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target, follow_symlinks=True)


def main():
    if Path(__file__).resolve().parent != ROOT or sys.platform != "linux" or sys.version_info[:2] != (3, 10):
        raise RuntimeError("root_owned_Linux_Python3.10_build_location_required")
    stage = ROOT / "initramfs"
    archive = ROOT / "test-initramfs.gz"
    if stage.exists() or archive.exists():
        raise RuntimeError("fresh_build_outputs_required")
    python = Path(sys.executable).resolve()
    git = Path(shutil.which("git") or "/missing-installed-git").resolve(strict=True)
    stdlib = Path(sysconfig.get_path("stdlib"))
    if file_bytes(Path("/lab")) + 2 * STAGE_LIMIT > LAB_LIMIT:
        raise RuntimeError("root_total_storage_preflight_refused")
    shutil.copytree("/lab/initramfs", stage, symlinks=True)
    (stage / "probe").unlink(missing_ok=True)
    runtime = stage / "opt/protocol"
    runtime.mkdir(parents=True, exist_ok=False)
    shutil.copytree(ROOT / "source", runtime / "source")
    shutil.copy2(ROOT / "guest.py", runtime / "guest.py")
    shutil.copy2(ROOT / "init", stage / "init")
    (stage / "init").chmod(0o755)
    target_stdlib = stage / stdlib.relative_to("/")
    shutil.copytree(stdlib, target_stdlib, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", "test", "tests", "idlelib", "tkinter",
        "ensurepip", "site-packages", "dist-packages", "_tkinter*.so"))
    copy_absolute(python, stage)
    copy_absolute(git, stage)
    entry = stage / "usr/bin/python3"
    entry.parent.mkdir(parents=True, exist_ok=True)
    if entry.exists() or entry.is_symlink():
        entry.unlink()
    entry.symlink_to(os.path.relpath(stage / python.relative_to("/"), entry.parent))
    if git != Path("/usr/bin/git"):
        raise RuntimeError("review_required_for_nonstandard_installed_git_path")
    pending = {python, git, *[stdlib / path.relative_to(target_stdlib) for path in target_stdlib.rglob("*.so")]}
    seen, dependencies = set(), set()
    while pending:
        binary = pending.pop()
        if binary in seen:
            continue
        seen.add(binary)
        result = subprocess.run(["ldd", str(binary)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError("ldd_failed:" + str(binary) + ":" + result.stderr)
        discovered = ldd_paths(result.stdout)
        dependencies.update(discovered)
        pending.update(discovered - seen)
    for dependency in sorted(dependencies):
        copy_absolute(dependency, stage)
    if file_bytes(stage) > STAGE_LIMIT or file_bytes(Path("/lab")) > LAB_LIMIT:
        raise RuntimeError("staging_or_root_storage_bound_exceeded")
    # Trusted installed executables and their closure only; no compilation.
    listing = subprocess.run(["find", ".", "-print0"], cwd=stage, capture_output=True, check=True)
    packed = subprocess.run(["cpio", "--null", "-o", "-H", "newc"], cwd=stage, input=listing.stdout, capture_output=True, check=True)
    with archive.open("xb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", compresslevel=1, mtime=0) as output:
            output.write(packed.stdout)
        target.flush()
        os.fsync(target.fileno())
    if archive.stat().st_size > INITRD_LIMIT or file_bytes(Path("/lab")) > LAB_LIMIT:
        raise RuntimeError("compressed_or_root_storage_bound_exceeded")
    closure = [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size} for path in sorted({python, git, *dependencies})]
    record = {"installed_python": sys.version, "git": subprocess.run([str(git), "version", "--build-options"], capture_output=True, text=True, check=True).stdout,
              "installed_packages": subprocess.run(["dpkg-query", "-W"], capture_output=True, text=True, check=True).stdout,
              "ldd_closure": closure, "stage_bytes": file_bytes(stage), "initrd_bytes": archive.stat().st_size,
              "initrd_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "cpio_stderr": packed.stderr.decode(),
              "kernel_sha256": hashlib.sha256(Path("/lab/boot/Image-virt").read_bytes()).hexdigest(),
              "stage_files": [{"path": str(path.relative_to(stage)), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(stage.rglob("*")) if path.is_file()],
              "limits": {"stage": STAGE_LIMIT, "compressed": INITRD_LIMIT, "root_total": LAB_LIMIT},
              "source_scope": "Copies trusted already-installed Python/Git/stdlib/ELF closure and existing kernel modules; executes no compiler or guest."}
    with (ROOT / "BUILD-RECEIPT.json").open("x") as output:
        json.dump(record, output, indent=2)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    descriptor = os.open(ROOT, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


if __name__ == "__main__":
    main()
