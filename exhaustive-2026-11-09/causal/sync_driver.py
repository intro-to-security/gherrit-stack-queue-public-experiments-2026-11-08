"""One separately granted official sync control in an isolated synthetic checkout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import harness as h
from unix_api_recorder import Recorder


NAME = "ordinary-sync-3"
BINARY = h.ROOT.parents[1] / "native-stacks-2026-11-08" / "cli-history" / "bin" / "darwin-arm64"
BINARY_SHA = "70c0cb11346ad5d4f97a02a5cf5242052254d1775d356dc0759f035457873850"
CHECKOUT = h.ROOT / (NAME + "-checkout")


def local_git(label, args):
    record = h.begin(NAME + "-local-" + label, {"kind": "local-git", "cwd": str(CHECKOUT), "args": args})
    result = subprocess.run(["/usr/bin/git", "-c", "core.hooksPath=" + str(h.HOOKS), *args], cwd=CHECKOUT, text=True, capture_output=True)
    record.update(end=h.stamp(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    h.save(h.EVIDENCE / (NAME + "-local-" + label + ".receipt.json"), record)
    if result.returncode:
        raise RuntimeError("Local checkout preparation failed: " + label)
    return result.stdout.strip()


def capture_catalog(label):
    result = {"local_refs": local_git(label + "-refs", ["show-ref"]), "catalog": {}}
    for path in (CHECKOUT / ".git").rglob("*"):
        if path.is_file() and ("stack" in str(path.relative_to(CHECKOUT / ".git"))):
            try:
                result["catalog"][str(path.relative_to(CHECKOUT / ".git"))] = path.read_text()
            except UnicodeDecodeError:
                pass
    h.save(h.EVIDENCE / (NAME + "-" + label + "-catalog.json"), result)
    return result


def cli(label, args, env):
    intent = h.begin(NAME + "-cli-" + label, {"kind": "official-cli", "binary": str(BINARY), "sha256": BINARY_SHA, "cwd": str(CHECKOUT), "args": args, "stdin": "EOF", "effect_scope": NAME, "catalog_and_refs": capture_catalog(label + "-input")})
    result = subprocess.run([str(BINARY), *args], cwd=CHECKOUT, env=env, input="", text=True, capture_output=True)
    intent.update(end=h.stamp(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    h.save(h.EVIDENCE / (NAME + "-cli-" + label + ".receipt.json"), intent)
    if result.returncode:
        raise RuntimeError("CLI did not complete successfully; no retry: " + label)
    return intent


def execute():
    if hashlib.sha256(BINARY.read_bytes()).hexdigest() != BINARY_SHA:
        raise RuntimeError("Pinned official CLI binary hash does not match")
    case = h.fixture(NAME)
    CHECKOUT.mkdir()
    local_git("init", ["init"])
    local_git("hooks", ["config", "core.hooksPath", str(h.HOOKS)])
    local_git("name", ["config", "user.name", "Josh Liebow-Feeser"])
    local_git("email", ["config", "user.email", "hello@joshlf.com"])
    local_git("remote", ["remote", "add", "origin", "https://github.com/" + h.REPO + ".git"])
    for letter, head in case["heads"].items():
        local_git("create-" + letter, ["fetch", "--no-tags", "origin", "refs/heads/" + head["ref"] + ":refs/heads/" + head["ref"], "refs/heads/" + head["ref"] + ":refs/remotes/origin/" + head["ref"]])
        if local_git("verify-" + letter, ["rev-parse", "refs/heads/" + head["ref"]]) != head["sha"]:
            raise RuntimeError("Local pre-adoption head mismatch")
    local_git("create-trunk", ["fetch", "--no-tags", "origin", "refs/heads/" + case["trunk"] + ":refs/heads/" + case["trunk"], "refs/heads/" + case["trunk"] + ":refs/remotes/origin/" + case["trunk"]])
    local_git("checkout-trunk", ["checkout", case["trunk"]])
    gate = h.ROOT / "git-gate-bin"
    gate.mkdir(exist_ok=True)
    (h.ROOT / "git_gate.py").chmod(0o755)
    if not (gate / "git").exists():
        (gate / "git").symlink_to(h.ROOT / "git_gate.py")
    env = dict(os.environ, PATH=str(gate) + os.pathsep + os.environ["PATH"], CAUSAL_SYNC_CASE=NAME, CAUSAL_SYNC_ALLOWED_REFS=json.dumps(["refs/heads/" + head["ref"] for letter, head in case["heads"].items() if letter != "A"]))
    credential = subprocess.run([h.GH, "auth", "token", "--hostname", "github.com"], capture_output=True, text=True)
    if credential.returncode or not credential.stdout.strip():
        raise RuntimeError("Credential unavailable for isolated CLI process")
    recorder = Recorder(NAME, h.ROOT / (NAME + "-api-config"))
    try:
        env.update(recorder.start(), GH_TOKEN=credential.stdout.strip())
        cli("adopt", ["init", "--base", case["trunk"], *[head["ref"] for head in case["heads"].values()]], env)
        h.observe(case, NAME + "-before")
        accepted = h.api(NAME + "-merge", "PUT", "repos/" + h.REPO + "/pulls/" + str(case["prs"]["A"]) + "/merge-async", {"merge_method": "squash", "merge_action": "direct_merge", "sha": case["heads"]["A"]["sha"]}, case=case)
        h.require_status(accepted, 202)
        terminal = h.poll(case, accepted)
        if terminal["data"].get("status") != "merged":
            raise RuntimeError("Native prefix did not land; no sync")
        h.await_rewrite(case)
        h.observe(case, NAME + "-pre-cli-sync")
        cli("sync", ["sync", "--remote", "origin", "--no-atomic=false"], env)
        capture_catalog("output")
        http_receipts = [json.loads(path.read_text()) for path in h.EVIDENCE.glob(NAME + "-cli-http-*.receipt.json")]
        if not http_receipts or any(not receipt["permitted"] for receipt in http_receipts):
            raise RuntimeError("CLI attempted blocked/out-of-scope API work or lacked recorded reads; reconcile")
        if not (h.EVIDENCE / (NAME + "-cli-push-single-dispatch.intent.json")).exists():
            raise RuntimeError("CLI's expected Git push was not recorded; no success claim")
        h.sample_window(case)
    finally:
        recorder.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grant", type=Path, required=True)
    args = parser.parse_args()
    grant = json.loads(args.grant.read_text())
    if grant.get("coordinator") != "root" or grant.get("repository") != h.REPO or NAME not in grant.get("cases", []):
        parser.error("Root's exact ordinary-sync-3 grant is required")
    try:
        execute()
    except Exception as error:
        if h.case_path(NAME).exists():
            case = json.loads(h.case_path(NAME).read_text())
            case.update(phase="frozen-requires-reconciliation", stop_reason=str(error))
            h.save(h.case_path(NAME), case)
        h.save(h.ROOT / (NAME + ".STOP.json"), {"at": h.stamp(), "error": str(error), "policy": "No automatic retry; reconcile read-only."})
        raise
