#!/usr/bin/env python3
"""Native queue discriminator with real Actions checks and no status writes."""

import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab import Lane, REPO, now, save

L = Lane("ci")
METHODS = {"native-no-manual-gate": "SQUASH", "native-no-manual-gate-merge": "MERGE",
           "native-no-manual-gate-rebase": "REBASE"}
NAME = sys.argv[sys.argv.index("--case") + 1] if "--case" in sys.argv else "native-no-manual-gate"
METHOD = METHODS[NAME]
LABEL = "nmg" if METHOD == "SQUASH" else "nmg-" + METHOD.lower()
HOME = L.home / NAME
HOME.mkdir(exist_ok=True)
STATE = HOME / "state.json"
API = "repos/" + REPO
QUERY = """query($owner:String!,$repo:String!,$branch:String!,$a:Int!,$b:Int!) {
 repository(owner:$owner,name:$repo) {
  mergeQueue(branch:$branch) { id entries(first:100) { pageInfo {hasNextPage} nodes {
   id position state enqueuedAt headCommit {oid} baseCommit {oid} pullRequest {number headRefOid}
  } } }
  a:pullRequest(number:$a) { id number state merged mergedAt headRefOid baseRefName baseRefOid mergeStateStatus
   mergeQueueEntry {id position state headCommit {oid} baseCommit {oid}}
   commits(last:1) {nodes {commit {oid statusCheckRollup {state contexts(first:100) {nodes {
    __typename ... on CheckRun {name status conclusion detailsUrl} ... on StatusContext {context state}
   } } } } } }
  }
  b:pullRequest(number:$b) { id number state merged mergedAt headRefOid baseRefName baseRefOid mergeStateStatus
   mergeQueueEntry {id position state headCommit {oid} baseCommit {oid}}
   commits(last:1) {nodes {commit {oid statusCheckRollup {state contexts(first:100) {nodes {
    __typename ... on CheckRun {name status conclusion detailsUrl} ... on StatusContext {context state}
   } } } } } }
  }
 }
}"""


def good(receipt, statuses=(200,)):
    assert receipt["http"] in statuses and not receipt.get("parse_error"), receipt
    if isinstance(receipt.get("data"), dict):
        assert not receipt["data"].get("errors"), receipt
    return receipt["data"]


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {"observations": []}


def query(label):
    c = L.get_fixture(NAME)
    receipt = L.graphql(label, QUERY, {"owner": REPO.split("/")[0], "repo": REPO.split("/")[1],
        "branch": c["trunk"], "a": c["prs"]["A"], "b": c["prs"]["B"]}, fresh=True)
    value = good(receipt)["data"]["repository"]
    if value["mergeQueue"]:
        assert not value["mergeQueue"]["entries"]["pageInfo"]["hasNextPage"]
    return {"started": receipt["start"], "finished": receipt["end"], "data": value}


def setup():
    c = L.fixture(NAME, count=2, native=True)
    for h in c["heads"].values():
        assert not L.git("ls-tree", "--name-only", h["sha"], "--", ".queue-experiment")
    body = {"name": "ci-" + NAME, "target": "branch", "enforcement": "active", "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["refs/heads/" + c["trunk"]], "exclude": []}},
        "rules": [{"type": "merge_queue", "parameters": {"check_response_timeout_minutes": 5,
            "grouping_strategy": "ALLGREEN", "max_entries_to_build": 1, "max_entries_to_merge": 5,
            "merge_method": METHOD, "min_entries_to_merge": 1, "min_entries_to_merge_wait_minutes": 1}},
          {"type": "required_status_checks", "parameters": {"strict_required_status_checks_policy": False,
            "required_status_checks": [{"context": "queue-observe", "integration_id": 15368}]}}]}
    rule = good(L.api(LABEL + "-create-exact-rule", "POST", API + "/rulesets", body), (201,))
    readback = good(L.api(LABEL + "-rule-readback", "GET", API + "/rulesets/" + str(rule["id"]), fresh=True))
    assert readback["bypass_actors"] == []
    required = [x["context"] for r in readback["rules"] if r["type"] == "required_status_checks" for x in r["parameters"]["required_status_checks"]]
    assert required == ["queue-observe"]
    value = load()
    value.update({"case": c, "rule": readback, "setup_at": now(), "synthetic_status_writes": 0})
    save(STATE, value)
    print(json.dumps({"prs": c["prs"], "stack": c["stack"], "ruleset": rule["id"], "method": METHOD, "required": required}))


def ready():
    value = load()
    rows = value.setdefault("source_ready_observations", [])
    for i in range(15):
        row = query(LABEL + "-source-ready")
        rows.append(row)
        save(STATE, value)
        states = [row["data"][letter]["mergeStateStatus"] for letter in ("a", "b")]
        print("SOURCE", states, flush=True)
        if states == ["CLEAN", "CLEAN"]:
            value["source_clean"] = row
            save(STATE, value)
            return
        time.sleep(2)
    raise RuntimeError("Source checks not yet CLEAN; read again without posting statuses")


def admit():
    value = load()
    c = value["case"]
    assert "source_clean" in value
    if "selected_head" not in value:
        before = query(LABEL + "-before-admission")
        assert all(before["data"][x]["mergeStateStatus"] == "CLEAN" for x in ("a", "b"))
        assert not before["data"]["mergeQueue"]["entries"]["nodes"]
        value["selected_head"] = before["data"]["b"]["headRefOid"]
        value["before_admission"] = before
        save(STATE, value)
    request = L.api(LABEL + "-enqueue-selected-B", "PUT", API + "/pulls/" + str(c["prs"]["B"]) + "/merge-async",
                    {"sha": value["selected_head"], "merge_action": "merge_queue"})
    response = good(request, (200, 202, 409))
    if request["http"] == 409:
        detail = response.get("details", {})
        assert detail.get("expected_head_sha") == value["selected_head"] and detail.get("merge_action") == "merge_queue"
    value["admission_request"] = request
    value.setdefault("admission_polls", [])
    uuid = response.get("details", {}).get("uuid")
    if uuid:
        for i in range(20):
            poll = L.api(LABEL + "-admission-poll", "GET", API + "/pulls/" + str(c["prs"]["B"]) + "/merge-async/" + uuid, fresh=True)
            value["admission_polls"].append(poll)
            result = good(poll)
            save(STATE, value)
            print("ADMISSION", result, flush=True)
            if result.get("status") != "pending":
                break
            time.sleep(1)
    value["admission_observation"] = query(LABEL + "-after-admission")
    save(STATE, value)


def observe(seconds):
    value = load()
    c = value["case"]
    start = time.monotonic()
    while time.monotonic() - start < seconds:
        index = len(value["observations"])
        row = query(LABEL + "-observe-" + str(index))
        row["refs_started"] = now()
        row["refs"] = L.git("ls-remote", "origin", "refs/heads/" + c["prefix"] + "/*", "refs/tags/" + c["prefix"] + "/*",
                            "refs/heads/gh-readonly-queue/" + c["trunk"] + "/*")
        row["refs_finished"] = now()
        value["observations"].append(row)
        save(STATE, value)
        print("OBSERVE", {x: {k: row["data"][x][k] for k in ("state", "merged", "headRefOid", "mergeStateStatus", "mergeQueueEntry")} for x in ("a", "b")}, flush=True)
        if all(row["data"][x]["merged"] for x in ("a", "b")):
            break
        time.sleep(3)
    value["last_observed_at"] = now()
    save(STATE, value)


def capture():
    value = load()
    c = value["case"]
    response = good(L.api(LABEL + "-actions-runs", "GET", API + "/actions/runs?per_page=100", fresh=True))
    runs = [r for r in response["workflow_runs"] if r["head_branch"] in {h["ref"] for h in c["heads"].values()} or
            (r["event"] == "merge_group" and ("gh-readonly-queue/" + c["trunk"] + "/") in r["head_branch"])]
    summary = []
    for r in runs:
        rid = r["id"]
        good(L.api(LABEL + "-run-" + str(rid), "GET", API + "/actions/runs/" + str(rid), fresh=True))
        good(L.api(LABEL + "-jobs-" + str(rid), "GET", API + "/actions/runs/" + str(rid) + "/jobs", fresh=True))
        if r["status"] == "completed":
            folder = HOME / "actions" / str(rid)
            if not folder.exists():
                folder.mkdir(parents=True)
                args = ["gh", "run", "download", str(rid), "--repo", REPO, "--dir", str(folder)]
                result = subprocess.run(args, text=True, capture_output=True)
                save(HOME / (str(rid) + "-download.json"), {"at": now(), "args": args, "exit": result.returncode,
                    "stdout": result.stdout, "stderr": result.stderr})
                assert result.returncode == 0, result.stderr
            log = subprocess.run(["gh", "run", "view", str(rid), "--repo", REPO, "--log"], text=True, capture_output=True)
            (HOME / (str(rid) + ".log")).write_text(log.stdout)
            assert log.returncode == 0, log.stderr
        summary.append({k: r[k] for k in ("id", "event", "head_branch", "head_sha", "status", "conclusion")})
    value["workflow_runs"] = summary
    value["removal_events"] = {}
    for letter, number in c["prs"].items():
        pr = good(L.api(LABEL + "-final-pr-" + letter, "GET", API + "/pulls/" + str(number), fresh=True))
        events = good(L.graphql(LABEL + "-removal-" + letter, """query($id:ID!){node(id:$id){... on PullRequest {
          number timelineItems(last:50){nodes{__typename ... on RemovedFromMergeQueueEvent {
           id createdAt reason beforeCommit{oid} actor{login}
          } } }
        } } }""", {"id": pr["node_id"]}, fresh=True))
        value["removal_events"][letter] = events
        for sha in {c["heads"][letter]["sha"], pr["head"]["sha"]}:
            good(L.api(LABEL + "-statuses-" + letter + "-" + sha, "GET", API + "/commits/" + sha + "/status", fresh=True))
            good(L.api(LABEL + "-checks-" + letter + "-" + sha, "GET", API + "/commits/" + sha + "/check-runs", fresh=True))
    value["capture_at"] = now()
    save(STATE, value)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    operation = sys.argv[1]
    if operation == "observe":
        observe(int(sys.argv[2]) if len(sys.argv) > 2 else 35)
    else:
        {"setup": setup, "ready": ready, "admit": admit, "capture": capture}[operation]()
