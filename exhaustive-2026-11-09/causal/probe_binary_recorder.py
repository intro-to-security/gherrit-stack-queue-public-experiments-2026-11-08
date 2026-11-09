"""Read-only actual-binary recorder probe; init only changes a private local catalog."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

import harness as h
from sync_driver import BINARY, BINARY_SHA
from unix_api_recorder import Recorder


NAME = "binary-recorder-read-probe"
CHECKOUT = h.ROOT / (NAME + "-checkout")


def git(*args):
    result = subprocess.run(["/usr/bin/git", "-c", "core.hooksPath=" + str(h.HOOKS), *args], cwd=CHECKOUT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Read-probe local Git preparation failed")
    return result.stdout.strip()


def main():
    if hashlib.sha256(BINARY.read_bytes()).hexdigest() != BINARY_SHA:
        raise RuntimeError("Pinned binary hash mismatch")
    CHECKOUT.mkdir()
    git("init")
    git("config", "core.hooksPath", str(h.HOOKS))
    git("remote", "add", "origin", "https://github.com/" + h.REPO + ".git")
    case = json.loads(h.case_path("force-control").read_text())
    for key, destination in (("trunk", case["trunk"]), ("A", case["heads"]["A"]["ref"]), ("B", case["heads"]["B"]["ref"])):
        git("fetch", "--no-tags", str(h.GIT), "refs/inputs/force-control-" + key + ":refs/heads/" + destination)
    git("checkout", case["trunk"])
    credential = subprocess.run([h.GH, "auth", "token", "--hostname", "github.com"], capture_output=True, text=True)
    if credential.returncode or not credential.stdout.strip():
        raise RuntimeError("Credential unavailable for isolated read probe")
    recorder = Recorder(NAME, h.ROOT / (NAME + "-config"))
    try:
        env = dict(os.environ, **recorder.start(), GH_TOKEN=credential.stdout.strip())
        args = ["init", "--base", case["trunk"], case["heads"]["A"]["ref"], case["heads"]["B"]["ref"]]
        intent = h.begin(NAME + "-cli", {"kind": "read-only-binary-probe", "binary_sha256": BINARY_SHA, "cwd": str(CHECKOUT), "args": args, "effects": "Local catalog adoption/checkout; every HTTP write refused by isolated Unix recorder."})
        result = subprocess.run([str(BINARY), *args], cwd=CHECKOUT, env=env, input="", capture_output=True, text=True)
        intent.update(end=h.stamp(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
        h.save(h.EVIDENCE / (NAME + "-cli.receipt.json"), intent)
    finally:
        recorder.close()
    receipts = [json.loads(path.read_text()) for path in h.EVIDENCE.glob(NAME + "-cli-http-*.receipt.json")]
    passed = result.returncode == 0 and receipts and all(item["permitted"] and item["forwarded"] and item["http"] == 200 for item in receipts)
    summary = {"binary_sha256": BINARY_SHA, "read_requests": len(receipts), "all_forwarded_reads_200": bool(passed), "cli_exit": result.returncode, "credential_retained": False, "upstream_tls_verification": "ssl.create_default_context()", "child_only_configuration": "GH_CONFIG_DIR http_unix_socket; GH_TOKEN in process memory only"}
    h.save(h.ROOT / (NAME + ".json"), summary)
    print(json.dumps(summary))
    if not passed:
        raise RuntimeError("Actual-binary recorder read-forwarding premise not met")


if __name__ == "__main__":
    main()
