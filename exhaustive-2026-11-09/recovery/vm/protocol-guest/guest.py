"""Guest entry point: exact prototype, serial evidence, one injected pause."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

PREFIXES = ("validated", "marked", "request_logged", "provider_head",
            "provider_archive", "provider_receipt", "acknowledged", "result_ref",
            "result_checkpoint", "complete", "after_return")
ROOT = Path(__file__).resolve().parent
PINS = {"protocol.py": "73994fcb9747b4461bc90b17f0ae1b12e4a064eaabc862d840938e984133a7de",
        "run.py": "42d87bcde806f3418b8658e76e5ea37900914fd4c8600fcf6271970e25f8f4a8"}


def emit(kind, value):
    print("PROTOCOL " + json.dumps({"kind": kind, "value": value}, sort_keys=True), flush=True)


def barrier(prefix):
    # Serial output changes no ext4 record; the controller must fsync its log.
    print("BARRIER PROTOCOL " + prefix, flush=True)
    while True:
        signal.pause()


def serial_pause(directory, prefix, selected):
    if prefix == selected:
        barrier(prefix)


def load_exact_sources():
    for name, expected in PINS.items():
        if hashlib.sha256((ROOT / "source" / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError("original_source_hash_changed:" + name)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / "source"))
    import protocol
    import run
    run.RUN = Path("/state/scope")
    return protocol, run


def command(repo, *args, env):
    process = subprocess.run(["git", "-C", str(repo), *args], env=env, capture_output=True)
    return {"argv": ["git", "-C", str(repo), *args], "exit": process.returncode,
            "stdout_hex": process.stdout.hex(), "stderr_hex": process.stderr.hex()}


def stdout(record):
    if record["exit"]:
        raise RuntimeError("independent_git_read_failed:" + json.dumps(record))
    return bytes.fromhex(record["stdout_hex"])


def inspect_repo(path, env):
    refs = command(path, "for-each-ref", "--format=%(refname) %(objectname)", env=env)
    inventory = command(path, "cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype) %(objectsize)", env=env)
    objects = []
    lines = bytes.fromhex(inventory["stdout_hex"]).decode().splitlines() if inventory["exit"] == 0 else []
    for line in lines:
        oid, kind, size = line.split()
        body = command(path, "cat-file", kind, oid, env=env)
        objects.append({"oid": oid, "type": kind, "size": int(size), "read": body})
    return {"path": str(path), "refs": refs, "inventory": inventory, "objects": objects,
            "fsck": command(path, "fsck", "--full", "--no-dangling", env=env),
            "config": command(path, "config", "--local", "--list", env=env)}


def snapshot(directory, env):
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix in (".json", ".jsonl"):
            data = path.read_bytes()
            if len(data) > 1024 * 1024:
                raise RuntimeError("unexpected_record_size:" + str(path))
            files[str(path.relative_to(directory))] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "hex": data.hex()}
    return {"directory": str(directory), "files": files,
            "repos": {"local": inspect_repo(directory / "repo", env),
                      "provider": inspect_repo(directory / "provider" / "repo", env)}}


def main(phase, prefix):
    if phase not in ("cut", "recover") or prefix not in PREFIXES:
        raise ValueError("exact phase and selected prefix required")
    p, fixture = load_exact_sources()
    directory = Path("/state/scope") / ("case-" + prefix)
    identity = "op-case-" + prefix
    emit("runtime", {"python": sys.version, "source_sha256": PINS,
                     "git": command(Path("/"), "version", "--build-options", env=p.ENV),
                     "phase": phase, "prefix": prefix,
                     "instrumentation": "Only protocol.pause is replaced, by serial-only output and signal.pause; no paused.json write/fsync."})
    if phase == "cut":
        if directory.parent.exists():
            raise RuntimeError("fresh_disk_scope_required")
        directory.parent.mkdir()
        made_directory, intent, _ = fixture.fixture("case-" + prefix)
        if made_directory != directory or intent["id"] != identity:
            raise RuntimeError("fixture_identity_mismatch")
        os.sync()  # Deliberately durable fixture baseline, before dispatch.
        emit("baseline", snapshot(directory, p.ENV))
        p.pause = serial_pause
        result = p.worker(directory, identity, "epoch-1", selected=prefix)
        emit("returned", result)
        if prefix != "after_return":
            raise RuntimeError("requested_prefix_was_not_reached")
        barrier("after_return")
    else:
        # Read after ext4 replay, before any logical recovery or worker Git log.
        emit("before_recovery", snapshot(directory, p.ENV))
        result = p.worker(directory, identity, "epoch-1", reconcile=True)
        emit("recovery_result", result)
        emit("after_recovery", snapshot(directory, p.ENV))
        print("PROTOCOL RECOVERY_READS_DONE", flush=True)


if __name__ == "__main__":
    try:
        main(*sys.argv[1:])
    except Exception as error:
        emit("harness_failure", {"type": type(error).__name__, "error": str(error)})
        raise
