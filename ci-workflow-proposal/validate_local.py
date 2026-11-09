#!/usr/bin/env python3
"""Exercise the observer against local Git trees; perform no network operations."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
VALIDATION = HERE / "validation"
VALIDATION.mkdir(exist_ok=True)
OUTPUT = Path(tempfile.mkdtemp(prefix="run-", dir=VALIDATION))
REPO = OUTPUT / "repo"
REPO.mkdir()
TRAILER = "Agent-authored-by: AI agent acting on joshlf's behalf"


def git(*args):
    return subprocess.check_output([
        "git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
        "-c", "user.name=Josh Liebow-Feeser", "-c", "user.email=hello@joshlf.com",
        *args,
    ], cwd=REPO, text=True).strip()


git("init", "--quiet")
git("commit", "--quiet", "--allow-empty", "-m", "Record local queue observer baseline", "-m", TRAILER)
shutil.copytree(HERE / ".github", REPO / ".github")
(REPO / ".queue-experiment").mkdir()
checks = []


def run_case(label, event_name, expected, *, bad_context_sha=False, bad_group_sha=False):
    head = git("rev-parse", "HEAD")
    event = {"action": "checks_requested" if event_name == "merge_group" else "synchronize"}
    if event_name == "merge_group":
        event["merge_group"] = {
            "head_sha": "0" * 40 if bad_group_sha else head,
            "head_ref": "refs/heads/gh-readonly-queue/synthetic/local",
            "base_sha": git("rev-parse", "HEAD^"),
            "base_ref": "refs/heads/exp/queue/local/trunk",
        }
    else:
        event["pull_request"] = {"number": 1, "head": {"sha": head}}
    destination = OUTPUT / label
    destination.mkdir()
    event_path = destination / "input-event.json"
    event_bytes = (json.dumps(event, indent=2) + "\n").encode()
    event_path.write_bytes(event_bytes)
    env = {**os.environ, "GITHUB_EVENT_PATH": str(event_path), "GITHUB_EVENT_NAME": event_name,
           "GITHUB_SHA": "0" * 40 if bad_context_sha else head, "GITHUB_REF": "refs/local/experiment",
           "GITHUB_RUN_ID": "local-" + label, "GITHUB_RUN_ATTEMPT": "1"}
    result = subprocess.run(["python3", ".github/scripts/queue_observe.py"], cwd=REPO,
                            env=env, text=True, capture_output=True)
    (destination / "stdout.txt").write_text(result.stdout)
    (destination / "stderr.txt").write_text(result.stderr)
    shutil.copytree(REPO / "queue-evidence", destination / "queue-evidence")
    record = json.loads((destination / "queue-evidence/context.json").read_text())
    check = {"case": label, "expected_exit": expected, "actual_exit": result.returncode,
             "head": head, "tree": record["tree"], "reasons": record["reasons"],
             "exact_event_copy": (destination / "queue-evidence/event.json").read_bytes() == event_bytes,
             "head_captured": record["head"] == head,
             "external_release_not_posted": record["release_status"]["posted_by_workflow"] is False}
    assert result.returncode == expected, check
    assert all(check[k] for k in ("exact_event_copy", "head_captured", "external_release_not_posted")), check
    checks.append(check)


for label, markers in [("none", []), ("pr", ["FAIL_PR"]), ("group", ["FAIL_MERGE_GROUP"]),
                       ("both", ["FAIL_PR", "FAIL_MERGE_GROUP"]), ("guards", [])]:
    for path in (REPO / ".queue-experiment").iterdir():
        path.unlink()
    for marker in markers:
        (REPO / ".queue-experiment" / marker).write_text("Synthetic local observer control.\n")
    git("add", "--all", "--", ".github", ".queue-experiment")
    git("commit", "--quiet", "--allow-empty", "-m", f"Record local queue observer fixture {label}", "-m", TRAILER)
    if label == "guards":
        run_case("wrong-github-sha", "pull_request", 1, bad_context_sha=True)
        run_case("wrong-group-sha", "merge_group", 1, bad_group_sha=True)
    else:
        run_case(label + "-pr", "pull_request", int("FAIL_PR" in markers))
        run_case(label + "-group", "merge_group", int("FAIL_MERGE_GROUP" in markers))

(OUTPUT / "results.json").write_text(json.dumps({"scope": "local real-Git execution only; no GitHub queue tested",
    "fixture_repo": str(REPO), "checks": checks}, indent=2) + "\n")
(VALIDATION / "latest.json").write_text(json.dumps({"results": str(OUTPUT / "results.json")}, indent=2) + "\n")
print(json.dumps({"local_cases_passed": len(checks), "provider_behavior_tested": False}, indent=2))
