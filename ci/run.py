#!/usr/bin/env python3
"""Recorded ordinary-PR queue controls confined to the CI lane."""

import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab import Lane, REPO, ROOT, now, save

lane = Lane("ci")
REST = "repos/" + REPO
RESULTS = lane.home / "results.json"


def require(response, statuses=(200,)):
    assert response["http"] in statuses, response
    if isinstance(response.get("data"), dict):
        assert not response["data"].get("errors"), response
    return response["data"]


def state():
    return json.loads(RESULTS.read_text()) if RESULTS.exists() else {}


def update(name, key, value):
    data = state()
    data.setdefault(name, {})[key] = value
    save(RESULTS, data)


def case(name):
    value = lane.get_fixture(name)
    assert value, "Create the fixture first"
    return value


def query(name, label):
    fixture = case(name)
    response = lane.graphql(label, """query($owner:String!,$repo:String!,$number:Int!) {
      repository(owner:$owner,name:$repo) { pullRequest(number:$number) {
        id number state merged mergedAt headRefOid baseRefName
        potentialMergeCommit { oid }
        mergeQueueEntry { id position state headCommit { oid } baseCommit { oid } }
      } }
    }""", {"owner": REPO.split("/")[0], "repo": REPO.split("/")[1],
             "number": fixture["prs"]["A"]}, fresh=True)
    result = require(response)["data"]["repository"]["pullRequest"]
    return result


def setup(name):
    assert name in ("single-held-release", "single-group-failure")
    files = {".queue-experiment/trial-id": name + "-2026-11-08\n"}
    if name == "single-group-failure":
        files[".queue-experiment/FAIL_MERGE_GROUP"] = "Synthetic merge-group failure control.\n"
    fixture = lane.fixture(name, count=1, native=False, files={"A": files})
    body = {"name": "ci-" + name, "target": "branch", "enforcement": "active", "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["refs/heads/" + fixture["trunk"]], "exclude": []}},
        "rules": [{"type": "merge_queue", "parameters": {
            "check_response_timeout_minutes": 5, "grouping_strategy": "ALLGREEN",
            "max_entries_to_build": 1, "max_entries_to_merge": 1, "merge_method": "SQUASH",
            "min_entries_to_merge": 1, "min_entries_to_merge_wait_minutes": 1}},
          {"type": "required_status_checks", "parameters": {
            "strict_required_status_checks_policy": False, "do_not_enforce_on_create": False,
            "required_status_checks": [{"context": "queue-observe", "integration_id": 15368},
                                       {"context": "experiment/queue-release"}]}}]}
    rule = require(lane.api(name + "-ruleset", "POST", REST + "/rulesets", body), (201,))
    update(name, "ruleset", {"id": rule["id"], "request": body})
    snapshot = lane.snapshot(fixture, name + "-created")
    assert snapshot["prs"]["A"]["data"].get("stack") is None
    print(json.dumps({"name": name, "pr": fixture["prs"]["A"], "trunk": fixture["trunk"], "ruleset": rule["id"]}))


def ready(name):
    fixture = case(name)
    pr = query(name, name + "-pre-admission")
    shas = {pr["headRefOid"], (pr.get("potentialMergeCommit") or {}).get("oid")}
    for sha in sorted(shas - {None}):
        require(lane.status(name + "-pr-release-" + sha, sha, "success"), (201,))
    for i in range(12):
        checks = require(lane.api(name + "-pr-checks", "GET", REST + "/commits/" + pr["headRefOid"] + "/check-runs", fresh=True))
        runs = [item for item in checks["check_runs"] if item["name"] == "queue-observe"]
        if runs and all(item["status"] == "completed" for item in runs):
            assert all(item["conclusion"] == "success" for item in runs), runs
            update(name, "pr_admission", {"pr": pr, "status_shas": sorted(shas - {None}), "checks": runs})
            print(json.dumps({"pr": pr["number"], "queue_observe": "success", "release_success_shas": sorted(shas - {None})}))
            return
        time.sleep(2)
    raise RuntimeError("PR check not yet complete; read again, without another status dispatch")


def enqueue(name):
    pr = query(name, name + "-pre-enqueue")
    assert not pr["merged"] and pr["mergeQueueEntry"] is None
    result = require(lane.graphql(name + "-enqueue", """mutation($input:EnqueuePullRequestInput!) {
      enqueuePullRequest(input:$input) { clientMutationId mergeQueueEntry { id position state
        headCommit { oid } baseCommit { oid } pullRequest { number } } }
    }""", {"input": {"pullRequestId": pr["id"], "expectedHeadOid": pr["headRefOid"],
                         "clientMutationId": "ci-" + name + "-enqueue"}}))
    update(name, "enqueue", result)
    print(json.dumps(result))


def collect(name):
    fixture = case(name)
    runs = require(lane.api(name + "-runs", "GET", REST + "/actions/runs?per_page=100", fresh=True))["workflow_runs"]
    selected = [run for run in runs if run["head_branch"] == fixture["heads"]["A"]["ref"] or
                (run["event"] == "merge_group" and ("gh-readonly-queue/" + fixture["trunk"] + "/") in run["head_branch"])]
    summaries = []
    for run in selected:
        rid = run["id"]
        require(lane.api(name + "-run-" + str(rid), "GET", REST + "/actions/runs/" + str(rid), fresh=True))
        require(lane.api(name + "-jobs-" + str(rid), "GET", REST + "/actions/runs/" + str(rid) + "/jobs", fresh=True))
        target = lane.evidence / "actions" / str(rid)
        if run["status"] == "completed" and not target.exists():
            started = now()
            args = ["gh", "run", "download", str(rid), "--repo", REPO, "--dir", str(target)]
            result = subprocess.run(args, text=True, capture_output=True)
            save(lane.evidence / (str(rid) + "-download.json"), {"start": started, "end": now(), "args": args,
                "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
            assert result.returncode == 0, result.stderr
        summaries.append({k: run[k] for k in ("id", "event", "head_branch", "head_sha", "status", "conclusion")})
    update(name, "runs", summaries)
    print(json.dumps(summaries, indent=2))
    return summaries


def group(name):
    fixture = case(name)
    runs = collect(name)
    group_runs = [item for item in runs if item["event"] == "merge_group"]
    assert group_runs, "No group event observed yet; read again without re-enqueueing"
    assert len(group_runs) == 1, "Rebuilt groups need separate explicit reconciliation"
    run = group_runs[0]
    assert run["status"] == "completed", "Group workflow not completed yet; collect again"
    artifact = lane.evidence / "actions" / str(run["id"])
    events = list(artifact.glob("*/event.json"))
    assert len(events) == 1
    event = json.loads(events[0].read_text())
    context = json.loads(events[0].with_name("context.json").read_text())
    value = event["merge_group"]
    assert value["head_sha"] == run["head_sha"] == context["head"] == context["env"]["GITHUB_SHA"]
    assert value["base_ref"] == "refs/heads/" + fixture["trunk"]
    sha = value["head_sha"]
    statuses = require(lane.api(name + "-group-statuses", "GET", REST + "/commits/" + sha + "/status", fresh=True))
    prior = [item for item in statuses["statuses"] if item["context"] == "experiment/queue-release"]
    assert not any(item["state"] == "success" for item in prior), "A reused SHA already has successful release"
    pr = query(name, name + "-group-observed")
    if name == "single-held-release":
        assert run["conclusion"] == "success" and not pr["merged"] and pr["mergeQueueEntry"] is not None
        require(lane.status(name + "-group-held-" + sha, sha, "pending"), (201,))
    else:
        assert run["conclusion"] == "failure" and context["decision"] == "failure"
        assert "Synthetic failure marker present: .queue-experiment/FAIL_MERGE_GROUP" in context["reasons"]
    update(name, "group", {"event": value, "context": context, "run": run, "prior_release_statuses": prior,
                            "pr_at_observation": pr, "observed": now()})
    lane.snapshot(fixture, name + "-group-recorded")
    print(json.dumps({"group_sha": sha, "workflow": run["conclusion"], "entry": pr["mergeQueueEntry"], "merged": pr["merged"]}))


def release(name):
    assert name == "single-held-release"
    pr = query(name, name + "-held-before-release")
    group = state()[name]["group"]
    assert pr["mergeQueueEntry"] is not None and not pr["merged"]
    assert pr["mergeQueueEntry"]["headCommit"]["oid"] == group["event"]["head_sha"]
    lane.snapshot(case(name), name + "-held-before-release")
    require(lane.status(name + "-group-release-" + group["event"]["head_sha"], group["event"]["head_sha"], "success"), (201,))
    update(name, "release", {"at": now(), "sha": group["event"]["head_sha"], "pr_before": pr})
    print(json.dumps({"released_group_sha": group["event"]["head_sha"]}))


def observe(name, label):
    pr = query(name, name + "-" + label)
    timeline = require(lane.api(name + "-" + label + "-timeline", "GET", REST + "/issues/" + str(pr["number"]) + "/timeline?per_page=100", fresh=True))
    snapshot = lane.snapshot(case(name), name + "-" + label + "-observed")
    update(name, label, {"at": now(), "pr": pr, "timeline": timeline, "snapshot": snapshot})
    print(json.dumps(pr, indent=2))


if __name__ == "__main__":
    operation, name, *rest = sys.argv[1:]
    if operation == "observe":
        observe(name, *rest)
    else:
        {"setup": setup, "ready": ready, "enqueue": enqueue, "collect": collect,
         "group": group, "release": release}[operation](name)
