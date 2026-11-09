"""Root-only collection of nine fresh trials; failures remain failed results."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import time

ROOT = Path("/lab/protocol-guest")
OUT = ROOT / "actual-results-continuation-001"
GRANT = ROOT / "CONTINUATION-GRANT.json"
CASES = ("marked", "request_logged", "provider_head", "provider_archive",
         "provider_receipt", "acknowledged", "result_ref", "result_checkpoint",
         "complete")
DISK_BYTES = 32 * 1024 * 1024
SOURCE_PINS = {
    "root_controller.py": "876b7b223a87c714d1e86e161d07995e7c5ec0880e74da4d3348e2a2452c9f74",
    "oracle.py": "d877a1a218e0585fdf0630003dd69054b3bb5dd4c4ef8a4947043dc24cbe1e07",
    "guest.py": "7893c80b62f0a7ce6854665443fb1a99c6c5fc1ee7ec7f2505f40fccc2254214",
    "source/protocol.py": "73994fcb9747b4461bc90b17f0ae1b12e4a064eaabc862d840938e984133a7de",
    "source/run.py": "42d87bcde806f3418b8658e76e5ea37900914fd4c8600fcf6271970e25f8f4a8",
    "init": "ac2af0c5da7837477cce22c87ad60e6adeb72ff0f80bf3d60b2aa23102fe799b",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_grant(grant):
    if (Path(__file__).resolve() != ROOT / "continuation-prep/continuation_controller.py"
            or grant.get("coordinator") != "root"
            or grant.get("grant_path") != str(GRANT)
            or grant.get("root") != str(ROOT) or grant.get("out") != str(OUT)
            or grant.get("cases") != list(CASES)
            or grant.get("disk_bytes") != DISK_BYTES):
        raise RuntimeError("Exact new continuation scope/grant required")
    hashes = dict(SOURCE_PINS, **{"continuation-prep/continuation_controller.py": sha(__file__)})
    if grant.get("source_hashes") != hashes:
        raise RuntimeError("Exact complete reviewed source vector required")
    for name, expected in hashes.items():
        if sha(ROOT / name) != expected:
            raise RuntimeError("Reviewed source changed:" + name)
    if (sha(ROOT / "test-initramfs.gz") != grant.get("initramfs_sha256")
            or sha(Path("/lab/boot/Image-virt")) != grant.get("kernel_sha256")
            or not isinstance(grant.get("runtime_python"), str)
            or len(grant.get("runtime_git_stdout_sha256", "")) != 64):
        raise RuntimeError("Exact runtime identity grant required")


def reviewed_modules():
    sys.path.insert(0, str(ROOT))
    import oracle
    if Path(oracle.__file__).resolve() != ROOT / "oracle.py":
        raise RuntimeError("Unexpected oracle module identity")
    spec = importlib.util.spec_from_file_location("reviewed_root_controller", ROOT / "root_controller.py")
    reviewed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reviewed)
    reviewed.ROOT, reviewed.OUT = ROOT, OUT
    if reviewed.oracle is not oracle or reviewed.DISK_BYTES != DISK_BYTES:
        raise RuntimeError("Reviewed primitive identity mismatch")
    return reviewed, oracle


def parse_records(data, oracle):
    records, counts, errors = {}, {}, []
    for number, line in enumerate(data.decode(errors="replace").splitlines(), 1):
        if not line.startswith("PROTOCOL {"):
            continue
        try:
            parsed = oracle.parse_serial(line)
            for kind, value in parsed.items():
                counts[kind] = counts.get(kind, 0) + 1
                if counts[kind] != 1:
                    errors.append({"line": number, "error": "duplicate_kind:" + kind})
                else:
                    records[kind] = value
        except (ValueError, KeyError, TypeError) as error:
            errors.append({"line": number, "error": str(error)})
    return {"records": records, "counts": counts, "errors": errors}


def runtime_matches(record, prefix, phase, grant):
    if not isinstance(record, dict):
        return False
    git = record.get("git")
    try:
        return (record.get("phase") == phase and record.get("prefix") == prefix
                and record.get("python") == grant["runtime_python"]
                and record.get("source_sha256") == {name: SOURCE_PINS["source/" + name] for name in ("protocol.py", "run.py")}
                and git["exit"] == 0
                and git["argv"] == ["git", "-C", "/", "version", "--build-options"]
                and hashlib.sha256(bytes.fromhex(git["stdout_hex"])).hexdigest() == grant["runtime_git_stdout_sha256"])
    except (KeyError, TypeError, ValueError):
        return False


def known_result(value):
    if not isinstance(value, dict):
        return False
    status = value.get("status")
    return (status in ("complete", "blocked_unknown_no_resend")
            or status == "refused" and isinstance(value.get("reason"), str) and bool(value["reason"]))


def boot(disk, prefix, phase, reviewed, oracle):
    """Return evidence only after bounded cleanup of the exact spawned child."""
    log = OUT / (prefix + "-" + phase + ".log")
    command = ["qemu-system-aarch64", "-machine", "virt", "-cpu", "cortex-a57",
               "-accel", "tcg", "-smp", "1", "-m", "256M", "-nographic",
               "-no-reboot", "-nic", "none", "-kernel", "/lab/boot/Image-virt",
               "-initrd", str(ROOT / "test-initramfs.gz"), "-append",
               "console=ttyAMA0 panic=-1 phase=" + phase + " prefix=" + prefix,
               "-drive", "if=none,file=" + str(disk) + ",format=raw,cache=writeback,id=d0",
               "-device", "virtio-blk-device,drive=d0"]
    reviewed.save(log.with_suffix(".intent.json"), {"command": command,
                  "phase": phase, "prefix": prefix, "state": "may be started", "utc_seconds": time.time()})
    target = ("BARRIER PROTOCOL " + (prefix if phase == "cut" else "CLEAN_RECOVERY_UNMOUNTED")).encode()
    process, data, reached, killed, exit_code = None, b"", False, False, None
    errors, eof = [], False
    with log.open("xb") as stream:
        stream.flush()
        os.fsync(stream.fileno())
        reviewed.sync_directory(OUT)
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                ready, _, _ = select.select([process.stdout], [], [], 1)
                if ready:
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        eof = True
                        break
                    stream.write(chunk)
                    stream.flush()
                    data += chunk
                    if target in data.splitlines():
                        reached = True
                        os.fsync(stream.fileno())
                        break
                if process.poll() is not None:
                    break
        except Exception as error:
            errors.append("capture:" + repr(error))
        finally:
            if process is not None:
                try:
                    if phase == "recover" and reached:
                        try:
                            exit_code = process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            pass
                    if process.poll() is None:
                        process.kill()
                        killed = True
                    exit_code = process.wait(timeout=10)
                except Exception as error:
                    errors.append("ownership_cleanup:" + repr(error))
                if exit_code is not None:
                    try:
                        drain_deadline = time.monotonic() + 2
                        while not eof and time.monotonic() < drain_deadline:
                            ready, _, _ = select.select([process.stdout], [], [], 0.1)
                            if ready:
                                chunk = os.read(process.stdout.fileno(), 65536)
                                if not chunk:
                                    eof = True
                                    break
                                stream.write(chunk)
                                data += chunk
                        if not eof:
                            errors.append("serial_drain_deadline")
                    except Exception as error:
                        errors.append("serial_drain:" + repr(error))
                try:
                    process.stdout.close()
                except Exception as error:
                    errors.append("serial_close:" + repr(error))
            stream.flush()
            os.fsync(stream.fileno())
    parsed = parse_records(data, oracle)
    receipt = {"pid": process.pid if process else None, "exit": exit_code,
               "process_started": process is not None, "known_stopped": process is not None and exit_code is not None,
               "target": target.decode(), "reached": reached, "kill_issued": killed,
               "natural_shutdown": phase == "recover" and reached and not killed and exit_code == 0,
               "exact_abrupt_cut": phase == "cut" and reached and killed and exit_code == -9 and not errors,
               "bytes": len(data), "errors": errors, "parse_errors": parsed["errors"], "utc_seconds": time.time()}
    reviewed.save(log.with_suffix(".receipt.json"), receipt)
    return {"receipt": receipt, "parsed": parsed}


def cut_premise(prefix, outcome, grant, oracle):
    parsed = outcome["parsed"]
    records = parsed["records"]
    if (not outcome["receipt"]["exact_abrupt_cut"] or parsed["errors"]
            or not runtime_matches(records.get("runtime"), prefix, "cut", grant)):
        return {"exact": False, "reason": "cut_process_serial_or_runtime_premise"}
    try:
        baseline = records["baseline"]
        directory = "/state/scope/case-" + prefix
        operation = oracle.document(baseline, "operation.json")
        intent = operation["intent"]
        local, objects = oracle.repository(baseline, "local")
        remote, remote_objects = oracle.repository(baseline, "provider")
        valid = (baseline["directory"] == directory and operation["state"] == "planned"
                 and baseline["repos"]["local"]["path"] == directory + "/repo"
                 and baseline["repos"]["provider"]["path"] == directory + "/provider/repo"
                 and intent["id"] == "op-case-" + prefix
                 and intent["provider"] == directory + "/provider"
                 and intent["continuation"] == "refs/retained/completed-case-" + prefix
                 and intent["expected"] == intent["input"]
                 and intent["captured_checkpoint"] == {"incorporated": intent["input"], "accepted_local": intent["result"]}
                 and intent["scope"] == ["head:A", "archive:case-" + prefix]
                 and intent["binding"] == {"repository": "local-fixture", "change": "A", "head": "A", "review": 1}
                 and oracle.document(baseline, "bindings.json") == intent["binding"]
                 and oracle.document(baseline, "original-checkpoint.json") == intent["captured_checkpoint"]
                 and oracle.document(baseline, "authority.json") == {"owner": directory, "token": "epoch-1", "mode": "native"}
                 and oracle.document(baseline, "authority-link.json") == {"path": directory + "/authority.json"}
                 and oracle.document(baseline, "manifest.json") == {"id": intent["id"], "digest": oracle.digest(intent)}
                 and oracle.document(baseline, "provider/state.json") == {"requests": [], "receipts": []}
                 and local.get("refs/retained/input") == intent["input"]
                 and local.get("refs/retained/result") == intent["result"]
                 and remote.get("refs/heads/A") == intent["input"]
                 and objects == remote_objects)
        return {"exact": bool(valid), "reason": None if valid else "baseline_identity_or_retained_input_mismatch"}
    except (KeyError, ValueError, TypeError) as error:
        return {"exact": False, "reason": "baseline_diagnostic:" + str(error)}


def recovery_disposition(prefix, outcome, grant):
    parsed, receipt = outcome["parsed"], outcome["receipt"]
    records = parsed["records"]
    known = (receipt["known_stopped"]
             and not receipt.get("errors")
             and not parsed["errors"]
             and {"before_recovery", "after_recovery"} <= records.keys()
             and parsed["counts"].get("runtime") == 1
             and parsed["counts"].get("recovery_result") == 1
             and runtime_matches(records.get("runtime"), prefix, "recover", grant)
             and known_result(records.get("recovery_result")))
    return {"known": bool(known), "worker_result": records.get("recovery_result"),
            "clean_unmount": receipt["natural_shutdown"],
            "boundary": "clean recovery unmount" if receipt["natural_shutdown"] else "known stopped recovery guest; may include a second emulator cut"}


def budget(reviewed, extra):
    if (reviewed.bytes_under(ROOT) + extra > 384 * 1024 * 1024
            or reviewed.bytes_under(Path("/lab")) + extra > 2 * 1024 * 1024 * 1024):
        raise RuntimeError("Owned storage envelope would be exceeded")


def collect_case(prefix, base, grant, reviewed, oracle):
    disk = OUT / (prefix + ".raw")
    if disk.exists():
        raise RuntimeError("Fresh case only; no same-case retry")
    budget(reviewed, 3 * DISK_BYTES + 1024 * 1024)
    shutil.copyfile(base, disk)
    cut = boot(disk, prefix, "cut", reviewed, oracle)
    row = {"prefix": prefix, "cut": cut["receipt"], "matrix_continue_allowed": False}
    if not cut["receipt"]["known_stopped"]:
        row["diagnostic"] = "unknown_or_alive_cut_process; disk not read or archived"
        reviewed.save(OUT / (prefix + "-result.json"), row)
        return row
    row["pre_recovery"] = reviewed.archive(disk, OUT / (prefix + "-pre-recovery.raw.gz"))
    row["cut_premise"] = cut_premise(prefix, cut, grant, oracle)
    if not row["cut_premise"]["exact"]:
        row["diagnostic"] = "cut premise failed; no recovery, retry or matrix continuation"
        reviewed.save(OUT / (prefix + "-result.json"), row)
        return row
    recovered = boot(disk, prefix, "recover", reviewed, oracle)
    row["recovery"] = recovered["receipt"]
    if not recovered["receipt"]["known_stopped"]:
        row["diagnostic"] = "unknown_or_alive_recovery_process; disk not read or archived"
        reviewed.save(OUT / (prefix + "-result.json"), row)
        return row
    # Preserve a stopped recovery disk even when result parsing or unmount fails.
    row["post_recovery"] = reviewed.archive(disk, OUT / (prefix + "-post-recovery.raw.gz"))
    fsck = subprocess.run(["e2fsck", "-fn", str(disk)], capture_output=True, text=True)
    row["fsck"] = {"exit": fsck.returncode, "stdout": fsck.stdout, "stderr": fsck.stderr, "repair": False}
    row["disposition"] = recovery_disposition(prefix, recovered, grant)
    records = recovered["parsed"]["records"]
    required = {"before_recovery", "after_recovery", "recovery_result"}
    if recovered["receipt"].get("errors") or recovered["parsed"]["errors"] or not required <= records.keys() or not known_result(records.get("recovery_result")):
        row["verdict"] = {"passed": False, "classification": "recovery_collection_diagnostic",
                          "missing": sorted(required - records.keys()), "parse_errors": recovered["parsed"]["errors"],
                          "capture_errors": recovered["receipt"].get("errors", [])}
    else:
        row["verdict"] = oracle.check(prefix, cut["parsed"]["records"]["baseline"],
                                      records["before_recovery"], records["after_recovery"], records["recovery_result"])
    row["matrix_continue_allowed"] = row["disposition"]["known"]
    reviewed.save(OUT / (prefix + "-result.json"), row)
    if row["matrix_continue_allowed"]:
        disk.unlink()
        reviewed.sync_directory(OUT)
    return row


def main():
    grant = json.loads(GRANT.read_text())
    check_grant(grant)
    reviewed, oracle = reviewed_modules()
    budget(reviewed, 2 * DISK_BYTES)
    OUT.mkdir(exist_ok=False)
    reviewed.sync_directory(OUT.parent)
    reviewed.save(OUT / "run-intent.json", grant)
    rows = []
    try:
        base = OUT / "base.raw"
        with base.open("xb") as stream:
            stream.truncate(DISK_BYTES)
        make = subprocess.run(["mkfs.ext4", "-F", "-b", "4096", str(base)], capture_output=True, text=True)
        reviewed.save(OUT / "mkfs.json", {"exit": make.returncode, "stdout": make.stdout, "stderr": make.stderr})
        make.check_returncode()
        with base.open("rb") as stream:
            os.fsync(stream.fileno())
        reviewed.sync_directory(OUT)
        for prefix in CASES:
            row = collect_case(prefix, base, grant, reviewed, oracle)
            rows.append(row)
            print(json.dumps({"prefix": prefix, "verdict": row.get("verdict"),
                              "matrix_continue_allowed": row["matrix_continue_allowed"]}), flush=True)
            if not row["matrix_continue_allowed"]:
                break
        reviewed.save(OUT / "RESULTS.json", {"cases": rows, "not_run": list(CASES[len(rows):]),
                      "all_passed": len(rows) == len(CASES) and all(row.get("verdict", {}).get("passed", False) for row in rows),
                      "limits": "Nine fresh local prototype/Git2.34/ext4 cases; unchanged oracle; outer caches survive; no native or production guarantee"})
        if len(rows) != len(CASES) or not rows[-1]["matrix_continue_allowed"]:
            reviewed.save(OUT / "STOP.json", {"state": "Unknown disposition or failed cut premise; no retry",
                          "rows_retained": len(rows), "not_run": list(CASES[len(rows):])})
    except Exception as error:
        reviewed.save(OUT / "STOP.json", {"state": "Collector failure; retain owned disk/evidence; no retry",
                      "error": repr(error), "rows_retained": len(rows), "not_run": list(CASES[len(rows):])})
        raise


if __name__ == "__main__":
    main()
