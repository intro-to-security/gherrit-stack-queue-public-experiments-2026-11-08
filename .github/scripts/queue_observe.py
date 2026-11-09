#!/usr/bin/env python3
"""Capture synthetic queue evidence without credentials or external writes."""

import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def main():
    output = Path("queue-evidence")
    output.mkdir(exist_ok=True)
    event_path = Path(os.environ["GITHUB_EVENT_PATH"])
    shutil.copyfile(event_path, output / "event.json")
    event = json.loads(event_path.read_text())
    keys = [
        "GITHUB_EVENT_NAME", "GITHUB_SHA", "GITHUB_REF", "GITHUB_HEAD_REF",
        "GITHUB_BASE_REF", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_JOB",
        "GITHUB_WORKFLOW", "GITHUB_WORKFLOW_REF", "GITHUB_WORKFLOW_SHA",
        "GITHUB_REPOSITORY", "GITHUB_ACTOR", "GITHUB_TRIGGERING_ACTOR",
        "RUNNER_OS", "RUNNER_ARCH",
    ]
    env = {key: os.environ.get(key) for key in keys}
    head = git("rev-parse", "HEAD")
    event_name = env["GITHUB_EVENT_NAME"]
    marker_paths = {
        "pull_request": ".queue-experiment/FAIL_PR",
        "merge_group": ".queue-experiment/FAIL_MERGE_GROUP",
    }
    tracked_markers = {
        name: git("ls-tree", "HEAD", "--", path)
        for name, path in marker_paths.items()
    }
    problems = []
    if head != env["GITHUB_SHA"]:
        problems.append("Checkout HEAD differs from GITHUB_SHA")
    if event_name not in marker_paths:
        problems.append("Unsupported experiment event")
    if event_name == "merge_group":
        if event.get("action") != "checks_requested":
            problems.append("Unexpected merge_group action")
        if event.get("merge_group", {}).get("head_sha") != head:
            problems.append("Merge-group head SHA differs from checkout HEAD")
    if tracked_markers.get(event_name):
        problems.append(f"Synthetic failure marker present: {marker_paths[event_name]}")
    record = {
        "env": env,
        "python": sys.version,
        "platform": platform.platform(),
        "head": head,
        "tree": git("rev-parse", "HEAD^{tree}"),
        "parents": git("rev-list", "--parents", "-n", "1", "HEAD"),
        "graph": git("log", "--all", "--format=%H %P %s", "-n", "60"),
        "workflow_blob": git("rev-parse", "HEAD:.github/workflows/queue-observe.yml"),
        "observer_blob": git("rev-parse", "HEAD:.github/scripts/queue_observe.py"),
        "tracked_markers": tracked_markers,
        "decision": "failure" if problems else "success",
        "reasons": problems,
        "release_status": {
            "context": "experiment/queue-release",
            "merge_group_target_sha": head if event_name == "merge_group" else None,
            "posted_by_workflow": False,
        },
    }
    (output / "context.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
