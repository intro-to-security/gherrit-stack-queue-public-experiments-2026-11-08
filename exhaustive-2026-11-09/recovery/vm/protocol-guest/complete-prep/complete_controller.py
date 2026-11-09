"""Root-only fresh complete-prefix trial using the unchanged reviewed collector."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path("/lab/protocol-guest")
OUT = ROOT / "actual-results-complete-001"
GRANT = ROOT / "COMPLETE-GRANT.json"
CASES = ("complete",)
COLLECTOR = "continuation-prep/continuation_controller.py"
COLLECTOR_SHA256 = "867796c89ff237a496735e582f311396b7be79428ce5e527130b880cb9186ced"
SELF = "complete-prep/complete_controller.py"


def load_collector():
    path = ROOT / COLLECTOR
    import hashlib
    if hashlib.sha256(path.read_bytes()).hexdigest() != COLLECTOR_SHA256:
        raise RuntimeError("Reviewed collector changed")
    spec = importlib.util.spec_from_file_location("reviewed_continuation", path)
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    if collector.ROOT != ROOT or collector.DISK_BYTES != 33554432:
        raise RuntimeError("Reviewed collector scope changed")
    return collector


def check_grant(grant, collector):
    if (Path(__file__).resolve() != ROOT / SELF
            or grant.get("coordinator") != "root"
            or grant.get("grant_path") != str(GRANT)
            or grant.get("root") != str(ROOT) or grant.get("out") != str(OUT)
            or grant.get("cases") != list(CASES)
            or grant.get("disk_bytes") != collector.DISK_BYTES):
        raise RuntimeError("Exact new complete-only grant required")
    hashes = dict(collector.SOURCE_PINS)
    hashes.update({COLLECTOR: COLLECTOR_SHA256, SELF: collector.sha(__file__)})
    if grant.get("source_hashes") != hashes:
        raise RuntimeError("Exact wrapper and reviewed dependency hashes required")
    for name, expected in hashes.items():
        if collector.sha(ROOT / name) != expected:
            raise RuntimeError("Reviewed source changed:" + name)
    if (collector.sha(ROOT / "test-initramfs.gz") != grant.get("initramfs_sha256")
            or collector.sha(Path("/lab/boot/Image-virt")) != grant.get("kernel_sha256")
            or not isinstance(grant.get("runtime_python"), str)
            or len(grant.get("runtime_git_stdout_sha256", "")) != 64):
        raise RuntimeError("Exact runtime identity grant required")


def main():
    collector = load_collector()
    grant = json.loads(GRANT.read_text())
    check_grant(grant, collector)
    collector.OUT = OUT
    reviewed, oracle = collector.reviewed_modules()
    collector.budget(reviewed, 2 * collector.DISK_BYTES)
    OUT.mkdir(exist_ok=False)
    reviewed.sync_directory(OUT.parent)
    reviewed.save(OUT / "run-intent.json", grant)
    try:
        base = OUT / "base.raw"
        with base.open("xb") as stream:
            stream.truncate(collector.DISK_BYTES)
        make = subprocess.run(["mkfs.ext4", "-F", "-b", "4096", str(base)], capture_output=True, text=True)
        reviewed.save(OUT / "mkfs.json", {"exit": make.returncode, "stdout": make.stdout, "stderr": make.stderr})
        make.check_returncode()
        with base.open("rb") as stream:
            os.fsync(stream.fileno())
        reviewed.sync_directory(OUT)
        row = collector.collect_case("complete", base, grant, reviewed, oracle)
        reviewed.save(OUT / "RESULTS.json", {"cases": [row], "requested_cases": list(CASES),
                      "all_passed": row["matrix_continue_allowed"] and row.get("verdict", {}).get("passed", False),
                      "basis": "Fresh fixture for previously NOT RUN complete; no retry or repair",
                      "limits": "Unchanged experimental Python/Git2.34/ext4 collector and oracle; no provider or production guarantee"})
        if not row["matrix_continue_allowed"]:
            reviewed.save(OUT / "STOP.json", {"state": "Known collection diagnostic or unknown disposition; no retry"})
    except Exception as error:
        reviewed.save(OUT / "STOP.json", {"state": "Collector failure; retain owned disk/evidence; no retry", "error": repr(error)})
        raise


if __name__ == "__main__":
    main()
