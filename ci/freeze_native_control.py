#!/usr/bin/env python3
"""Read and freeze exact native queue evidence; never mutate hosted state."""

import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab import Lane, REPO, now, save

L = Lane("ci")
METHODS = {"native-no-manual-gate": "SQUASH", "native-no-manual-gate-merge": "MERGE",
           "native-no-manual-gate-rebase": "REBASE"}
NAME = sys.argv[1]
METHOD = METHODS[NAME]
HOME = L.home / NAME
STATE = json.loads((HOME / "state.json").read_text())
CASE = STATE["case"]
PREFIX = "freeze-" + METHOD.lower()


def read(label, path):
    receipt = L.api(PREFIX + "-" + label, "GET", "repos/" + REPO + path, fresh=True)
    assert receipt["http"] == 200 and not receipt.get("parse_error"), receipt
    return receipt["data"]


def raw_git(*args):
    result = L.git(*args, check=False)
    assert result.returncode == 0, result.stderr
    return result.stdout


def refmap(raw):
    return {line.split("\t")[1]: line.split("\t")[0] for line in raw.splitlines()}


started = now()
effective = read("effective-rules", "/rules/branches/" + quote(CASE["trunk"], safe=""))
required = [item for rule in effective if rule["type"] == "required_status_checks"
            for item in rule["parameters"]["required_status_checks"]]
assert required == [{"context": "queue-observe", "integration_id": 15368}]
queue_rule = next(rule["parameters"] for rule in effective if rule["type"] == "merge_queue")
assert queue_rule["merge_method"] == METHOD and queue_rule["max_entries_to_build"] == 1 and queue_rule["max_entries_to_merge"] == 5
assert STATE["rule"]["bypass_actors"] == []
assert STATE["admission_request"]["payload"] == {"sha": CASE["heads"]["B"]["sha"], "merge_action": "merge_queue"}
assert STATE["admission_polls"][-1]["data"]["status"] == "enqueued"
assert all(STATE["source_clean"]["data"][x]["mergeStateStatus"] == "CLEAN" for x in ("a", "b"))
last = STATE["observations"][-1]
assert not last["data"]["mergeQueue"]["entries"]["nodes"]
assert all(last["data"][x]["mergeQueueEntry"] is None for x in ("a", "b"))
fresh_prs = {letter: read("pr-" + letter, "/pulls/" + str(number)) for letter, number in CASE["prs"].items()}
for letter in ("A", "B"):
    assert fresh_prs[letter]["head"]["sha"] == last["data"][letter.lower()]["headRefOid"]
fetch = L.git("fetch", "origin", "+refs/heads/" + CASE["prefix"] + "/*:refs/remotes/observed/" + NAME + "/*", check=False)
assert fetch.returncode == 0, fetch.stderr
save(HOME / "freeze-fetch.json", {"at": now(), "exit": fetch.returncode, "stdout": fetch.stdout, "stderr": fetch.stderr})
refs_started = now()
refs = refmap(raw_git("ls-remote", "origin", "refs/heads/" + CASE["prefix"] + "/*", "refs/tags/" + CASE["prefix"] + "/*"))
refs_finished = now()
old_a, old_b = CASE["heads"]["A"]["sha"], CASE["heads"]["B"]["sha"]
new_b = fresh_prs["B"]["head"]["sha"]
trunk = refs["refs/heads/" + CASE["trunk"]]
commits = {role: read("commit-" + role, "/git/commits/" + sha) for role, sha in
           {"original_A": old_a, "original_B": old_b, "current_B": new_b, "current_trunk": trunk}.items()}
assert len(commits["current_B"]["parents"]) == 1
new_parent = commits["current_B"]["parents"][0]["sha"]
before = raw_git("diff", "--binary", old_a, old_b)
after = raw_git("diff", "--binary", new_parent, new_b)
(HOME / "original-B-exact.patch").write_text(before)
(HOME / "current-B-exact.patch").write_text(after)
a, b = commits["original_B"], commits["current_B"]
comparison = {"old_B": old_b, "new_B": new_b, "old_parent": old_a, "new_parent": new_parent,
    "raw_patch_bytes_equal": before.encode() == after.encode(),
    "old_patch_sha256": hashlib.sha256(before.encode()).hexdigest(),
    "new_patch_sha256": hashlib.sha256(after.encode()).hexdigest(),
    "tree_equal": a["tree"]["sha"] == b["tree"]["sha"], "author_equal": a["author"] == b["author"],
    "message_equal": a["message"] == b["message"], "old_verified": a["verification"]["verified"],
    "new_verified": b["verification"]["verified"]}
assert all(comparison[key] for key in ("raw_patch_bytes_equal", "tree_equal", "author_equal", "message_equal"))
for letter in ("A", "B"):
    assert refs["refs/tags/" + CASE["prefix"] + "/authored/" + letter + "/v1"] == CASE["heads"][letter]["sha"]
    assert refs["refs/heads/" + CASE["heads"][letter]["ref"]] == fresh_prs[letter]["head"]["sha"]
groups, event_summaries = [], []
for run in STATE["workflow_runs"]:
    assert run["status"] == "completed" and run["conclusion"] == "success"
    files = list((HOME / "actions" / str(run["id"])).glob("*/event.json"))
    assert len(files) == 1
    event = json.loads(files[0].read_text())
    context = json.loads(files[0].with_name("context.json").read_text())
    item = {"run_id": run["id"], "event": run["event"], "action": event.get("action"),
            "run_head_sha": run["head_sha"], "checkout": context,
            "pr_number": event.get("number"), "event_pr_head": (event.get("pull_request") or {}).get("head", {}).get("sha")}
    event_summaries.append(item)
    if run["event"] == "merge_group":
        group = event["merge_group"]
        assert group["head_sha"] == run["head_sha"] == context["head"] == context["env"]["GITHUB_SHA"]
        commit = read("group-" + str(run["id"]), "/git/commits/" + group["head_sha"])
        checks = read("group-checks-" + str(run["id"]), "/commits/" + group["head_sha"] + "/check-runs")
        assert context["tree"] == commit["tree"]["sha"]
        assert context["parents"].split()[1:] == [p["sha"] for p in commit["parents"]]
        observed = [c for c in checks["check_runs"] if c["name"] == "queue-observe"]
        assert observed and all(c["head_sha"] == group["head_sha"] and c["conclusion"] == "success" and c["app"]["id"] == 15368 for c in observed)
        groups.append({"run_id": run["id"], "event": group, "context": context, "commit": commit,
                       "check_runs": [{key: c[key] for key in ("id", "name", "head_sha", "status", "conclusion", "details_url")} for c in observed]})
removals = {letter: [e for e in value["data"]["node"]["timelineItems"]["nodes"]
                     if e["__typename"] == "RemovedFromMergeQueueEvent"] for letter, value in STATE["removal_events"].items()}
assert len(groups) == (2 if METHOD == "MERGE" else 1)
assert fresh_prs["A"]["merged"]
if METHOD == "MERGE":
    assert fresh_prs["B"]["merged"] and new_b == old_b
    assert all(len(removals[x]) == 1 and removals[x][0]["reason"] == "merged" for x in ("A", "B"))
else:
    assert not fresh_prs["B"]["merged"] and fresh_prs["B"]["state"] == "open" and new_b != old_b
    assert last["data"]["b"]["mergeStateStatus"] == "CLEAN"
    assert len(removals["B"]) == 1 and removals["B"][0]["reason"] == "invalid_merge_commit"
    assert any(e["action"] == "synchronize" and e["event_pr_head"] == new_b for e in event_summaries)
assert trunk in {g["event"]["head_sha"] for g in groups}
sha_set = {old_a, old_b, new_b, trunk} | {g["event"]["head_sha"] for g in groups}
status_lists = {sha: read("statuses-" + sha, "/commits/" + sha + "/status")["statuses"] for sha in sha_set}
assert all(items == [] for items in status_lists.values())
status_write_receipts = []
for path in L.evidence.glob("*.receipt.json"):
    row = json.loads(path.read_text())
    if row["method"] == "POST" and any(row["path"] == "repos/" + REPO + "/statuses/" + sha for sha in sha_set):
        status_write_receipts.append(path.name)
assert status_write_receipts == []
uuid = STATE["admission_request"]["data"]["details"]["uuid"]
old_receipt = read("old-admission", "/pulls/" + str(CASE["prs"]["B"]) + "/merge-async/" + uuid)
assert old_receipt["status"] == "enqueued"
pins = {}
for role, sha in {"current-B": new_b, "current-trunk": trunk}.items():
    ref = "refs/experiment-inputs/" + NAME + "-frozen-" + role
    existing = L.git("rev-parse", "--verify", ref, check=False)
    if existing.returncode:
        L.git("update-ref", ref, sha, "")
    else:
        assert existing.stdout.strip() == sha
    pins[ref] = sha
frozen = {"started": started, "finished": now(), "method": METHOD, "case": CASE, "effective_rules": effective,
    "selected_head": STATE["selected_head"], "request": STATE["admission_request"],
    "admission_terminal": STATE["admission_polls"][-1]["data"], "old_receipt_after": old_receipt,
    "last_queue_observation": last, "fresh_prs": {x: {key: p.get(key) for key in
        ("number", "node_id", "state", "merged", "merged_at")} | {"head": p["head"]["sha"], "base": p["base"]["ref"], "base_sha": p["base"]["sha"]} for x, p in fresh_prs.items()},
    "refs_started": refs_started, "refs_finished": refs_finished, "refs": refs, "commits": commits,
    "B_comparison": comparison, "groups": groups, "workflow_events": event_summaries, "removals": removals,
    "commit_status_lists": status_lists, "status_write_receipts": status_write_receipts, "local_pins": pins,
    "limits": "One fresh fixture per method; read intervals are not atomic; no future-write or provider-settlement guarantee"}
save(HOME / "frozen-summary.json", frozen)
print(json.dumps({"method": METHOD, "prs": CASE["prs"], "final_states": {x: p["state"] for x, p in frozen["fresh_prs"].items()},
    "last_queue_entries": {x: last["data"][x.lower()]["mergeQueueEntry"] for x in ("A", "B")},
    "removals": {x: [{key: e[key] for key in ("createdAt", "reason", "beforeCommit")} for e in rows] for x, rows in removals.items()},
    "groups": [{"run_id": g["run_id"], "head": g["event"]["head_sha"], "parents": [p["sha"] for p in g["commit"]["parents"]]} for g in groups],
    "B_comparison": comparison}, indent=2))
