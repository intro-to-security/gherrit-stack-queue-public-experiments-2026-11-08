import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import traceback
from urllib.parse import quote

sys.dont_write_bytecode = True
HOME = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("public_edit_lab", HOME.parent / "lab.py")
lab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab)
L = lab.Lane("edit")
STATE_PATH = HOME / "state.json"
STATE = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {
    "name": "selected-head-edit-" + str(time.time_ns()), "checks": [], "phases": {}}
API = "repos/" + lab.REPO


def save():
    lab.save(STATE_PATH, STATE)


def check(label, actual, expected, required=True):
    row = {"at": lab.now(), "label": label, "actual": actual, "expected": expected,
           "passed": actual == expected, "required": required}
    STATE["checks"].append(row)
    save()
    if required and not row["passed"]:
        raise RuntimeError(json.dumps(row, indent=2))


def good(response, statuses=(200,)):
    if response.get("http") not in statuses or response.get("parse_error"):
        raise RuntimeError("Stop; no automatic retry of receipt: " + json.dumps(response, indent=2))
    if isinstance(response.get("data"), dict) and response["data"].get("errors"):
        raise RuntimeError("GraphQL errors: " + json.dumps(response, indent=2))
    return response["data"]


QUERY = """query($owner:String!,$name:String!,$trunk:String!,$a:Int!,$b:Int!) {
  repository(owner:$owner,name:$name) {
    mergeQueue(branch:$trunk) {
      id entries(first:100) {
        totalCount pageInfo { hasNextPage endCursor }
        nodes { id position state enqueuedAt headCommit { oid } baseCommit { oid }
          pullRequest { id number headRefOid } }
      }
    }
    a:pullRequest(number:$a) {
      id number state merged headRefOid baseRefName baseRefOid mergeStateStatus
      potentialMergeCommit { oid }
      mergeQueueEntry { id position state headCommit { oid } baseCommit { oid } }
      commits(last:1) { nodes { commit { oid statusCheckRollup {
        state contexts(first:100) { nodes {
          __typename ... on CheckRun { name status conclusion detailsUrl }
          ... on StatusContext { context state targetUrl }
        } }
      } } } }
    }
    b:pullRequest(number:$b) {
      id number state merged headRefOid baseRefName baseRefOid mergeStateStatus
      potentialMergeCommit { oid }
      mergeQueueEntry { id position state headCommit { oid } baseCommit { oid } }
      commits(last:1) { nodes { commit { oid statusCheckRollup {
        state contexts(first:100) { nodes {
          __typename ... on CheckRun { name status conclusion detailsUrl }
          ... on StatusContext { context state targetUrl }
        } }
      } } } }
    }
  }
}"""


def gql_read(label):
    case = STATE["case"]
    owner, name = lab.REPO.split("/")
    raw = L.graphql(label, QUERY, {"owner": owner, "name": name, "trunk": case["trunk"],
                    "a": case["prs"]["A"], "b": case["prs"]["B"]}, fresh=True)
    data = good(raw)["data"]["repository"]
    queue = data["mergeQueue"]
    if queue:
        check(label + " complete own queue listing", queue["entries"]["pageInfo"]["hasNextPage"], False)
        own = set(case["prs"].values())
        check(label + " all queue entries belong to fixture", all(p["pullRequest"]["number"] in own for p in queue["entries"]["nodes"]), True)
    return {"start": raw["start"], "end": raw["end"], "data": data}


def refs():
    case = STATE["case"]
    raw = L.git("ls-remote", "origin", "refs/heads/" + case["prefix"] + "/*",
                "refs/tags/" + case["prefix"] + "/*", "refs/heads/gh-readonly-queue/" + case["trunk"] + "/*")
    return {line.split("\t")[1]: line.split("\t")[0] for line in raw.splitlines()}


def snapshot(label):
    case = STATE["case"]
    result = {"start": lab.now(), "graphql": gql_read(label + "-gql"), "prs": {}}
    for letter, number in case["prs"].items():
        raw = L.api(label + "-" + letter, "GET", API + "/pulls/" + str(number), fresh=True)
        result["prs"][letter] = {"start": raw["start"], "end": raw["end"], "data": good(raw)}
    stack = L.api(label + "-stack", "GET", API + "/stacks/" + str(case["stack"]), fresh=True)
    result["stack"] = good(stack)
    result["refs_start"] = lab.now()
    result["refs"] = refs()
    result["end"] = lab.now()
    target = L.evidence / (label + ".snapshot.json")
    assert not target.exists()
    lab.save(target, result)
    check(label + " trunk unchanged", result["refs"]["refs/heads/" + case["trunk"]], case["trunk_sha"])
    for letter in ["A", "B"]:
        check(label + " " + letter + " unmerged", result["prs"][letter]["data"]["merged"], False)
    return result


def initial_release(label):
    case = STATE["case"]
    shas = set(head["sha"] for head in case["heads"].values())
    for letter, number in case["prs"].items():
        p = good(L.api(label + "-pr-" + letter, "GET", API + "/pulls/" + str(number), fresh=True))
        if p.get("merge_commit_sha"):
            shas.add(p["merge_commit_sha"])
        raw = L.git("ls-remote", "origin", "refs/pull/" + str(number) + "/merge")
        if raw:
            shas.add(raw.split("\t")[0])
    for sha in sorted(shas):
        good(L.status("initial-release-" + sha, sha, "success"), (201,))
    STATE.setdefault("initial_release_shas", [])
    STATE["initial_release_shas"] = sorted(set(STATE["initial_release_shas"]) | shas)
    save()


def setup():
    seed = L.init_git()
    check("authorized bootstrap seed", seed, "3a9df32f515072950fac44b3f0bb9ab2b549170e")
    L.git("config", "--local", "commit.gpgsign", "false")
    files = {"B": {".queue-experiment/FAIL_MERGE_GROUP": "Keep the queued-edit fixture from landing.\n"}}
    case = L.fixture(STATE["name"], count=2, native=True, files=files)
    STATE["case"] = case
    save()
    print("FIXTURE " + json.dumps(case), flush=True)
    params = {"check_response_timeout_minutes": 5, "grouping_strategy": "ALLGREEN",
        "max_entries_to_build": 0, "max_entries_to_merge": 2, "merge_method": "SQUASH",
        "min_entries_to_merge": 1, "min_entries_to_merge_wait_minutes": 0}
    body = {"name": "edit-" + STATE["name"], "target": "branch", "enforcement": "active", "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["refs/heads/" + case["trunk"]], "exclude": []}},
        "rules": [{"type": "merge_queue", "parameters": params},
                  {"type": "required_status_checks", "parameters": {
                      "required_status_checks": [{"context": "queue-observe"}, {"context": "experiment/queue-release"}],
                      "strict_required_status_checks_policy": False}}]}
    created = L.api("create-exact-trunk-rule", "POST", API + "/rulesets", body)
    rule = good(created, (201,))
    STATE["ruleset_id"] = rule["id"]
    save()
    readback = good(L.api("read-own-rule", "GET", API + "/rulesets/" + str(rule["id"]), fresh=True))
    check("exact owned trunk only", readback["conditions"]["ref_name"], body["conditions"]["ref_name"])
    check("no bypass actors", readback["bypass_actors"], [])
    actual_queue = next(r["parameters"] for r in readback["rules"] if r["type"] == "merge_queue")
    check("queue build remains zero", actual_queue["max_entries_to_build"], 0)
    check("required contexts exactly two", sorted(c["context"] for r in readback["rules"] if r["type"] == "required_status_checks" for c in r["parameters"]["required_status_checks"]),
          ["experiment/queue-release", "queue-observe"])
    initial_release("initial-gates")
    for index in range(36):
        sample = gql_read("source-gates-" + str(index))
        nodes = sample["data"]
        states = {letter: nodes[letter.lower()]["mergeStateStatus"] for letter in ["A", "B"]}
        print("SOURCE " + json.dumps({"at": lab.now(), "states": states}), flush=True)
        if all(value == "CLEAN" for value in states.values()):
            STATE["source_clean"] = sample
            save()
            snapshot("source-clean-before-admission")
            return
        if index in [6, 18]:
            initial_release("refreshed-test-merge-" + str(index))
        time.sleep(5)
    raise RuntimeError("Initial PR gates did not become CLEAN within the bounded interval; no enqueue attempted.")


def poll_old(label):
    if not STATE.get("uuid"):
        return {"unavailable": "Initial immediate terminal response supplied no UUID"}
    case = STATE["case"]
    raw = L.api(label, "GET", API + "/pulls/" + str(case["prs"]["B"]) + "/merge-async/" + STATE["uuid"], fresh=True)
    data = good(raw)
    lab.save(L.evidence / (label + ".old-async.json"), {"start": raw["start"], "end": raw["end"], "data": data})
    return data


def cleanup():
    current = gql_read("cleanup-read-first")
    case = STATE["case"]
    for index in range(3):
        q = current["data"]["mergeQueue"]
        entries = q["entries"]["nodes"] if q else []
        if not entries:
            STATE["cleanup"] = {"status": "own_queue_empty", "last_read": current, "at": lab.now()}
            save()
            return
        entry = sorted(entries, key=lambda x: x["position"])[0]
        pr = entry["pullRequest"]
        check("cleanup touches only fixture PR", pr["number"] in case["prs"].values(), True)
        query = "mutation($id:ID!,$nonce:String!){dequeuePullRequest(input:{id:$id,clientMutationId:$nonce}){clientMutationId}}"
        response = L.graphql("cleanup-dequeue-" + str(pr["number"]), query, {"id": pr["id"], "nonce": STATE["name"] + "-" + str(pr["number"])})
        good(response)
        current = gql_read("cleanup-after-" + str(index))
    raise RuntimeError("Cleanup did not observe an empty own queue; preserve residual state without retry.")


def probe():
    case = STATE["case"]
    before = snapshot("before-enqueue")
    data = before["graphql"]["data"]
    check("both source PR gates CLEAN at dispatch", [data[k]["mergeStateStatus"] for k in ["a", "b"]], ["CLEAN", "CLEAN"])
    queue = data["mergeQueue"]
    check("own queue initially empty", queue["entries"]["nodes"] if queue else [], [])
    selected = case["heads"]["B"]["sha"]
    path = API + "/pulls/" + str(case["prs"]["B"]) + "/merge-async"
    request = L.api("enqueue-selected-B", "PUT", path, {"merge_action": "merge_queue", "sha": selected})
    result = good(request, (200, 202))
    STATE["admission_request"] = request
    if result["status"] == "pending":
        details = result["details"]
        check("admission receipt selected SHA", details["expected_head_sha"], selected)
        check("admission receipt queue action", details["merge_action"], "merge_queue")
        STATE["uuid"] = details["uuid"]
        save()
        for index in range(20):
            result = poll_old("admission-poll-" + str(index))
            if result["status"] != "pending":
                break
            time.sleep(2)
    check("async request terminal enqueued", result["status"], "enqueued")
    STATE["terminal_admission"] = result
    save()
    admitted = snapshot("admitted-before-edit")
    entries = admitted["graphql"]["data"]["mergeQueue"]["entries"]["nodes"]
    check("selected B actually in own queue", case["prs"]["B"] in [p["pullRequest"]["number"] for p in entries], True)
    check("observed queue contains full A-B prefix", [p["pullRequest"]["number"] for p in entries], [case["prs"]["A"], case["prs"]["B"]], required=False)
    check("old B head still exact before edit", admitted["refs"]["refs/heads/" + case["heads"]["B"]["ref"]], selected)
    b2 = L.commit(STATE["name"] + "-B2", case["heads"]["A"]["sha"], {
        case["name"] + "/B.txt": "B=2 substantive selected-head edit\n",
        ".queue-experiment/FAIL_MERGE_GROUP": "Keep the queued-edit fixture from landing.\n"})
    STATE["B2"] = b2
    save()
    head = "refs/heads/" + case["heads"]["B"]["ref"]
    archive = "refs/tags/" + case["prefix"] + "/authored/B/v2"
    pushed = L.push("substantive-B2-and-archive", {head: b2, archive: b2}, {head: selected, archive: ""})
    check("B2 and archive atomic push succeeds", pushed["exit"], 0)
    observations = []
    for index in range(7):
        if index:
            time.sleep(3 if index < 4 else 5)
        snap = snapshot("after-edit-" + str(index))
        check("after-edit ref is exact B2 " + str(index), snap["refs"][head], b2)
        check("after-edit archive v2 exact " + str(index), snap["refs"][archive], b2)
        observations.append(snap)
        print("AFTER_EDIT " + json.dumps({"at": lab.now(), "queue_entries": snap["graphql"]["data"]["mergeQueue"]["entries"]["nodes"]}), flush=True)
    STATE["after_edit"] = observations
    STATE["old_async_after_edit"] = poll_old("old-async-after-edit")
    save()
    cleanup()
    STATE["old_async_after_cleanup"] = poll_old("old-async-after-cleanup")
    STATE["final"] = snapshot("final-after-cleanup")
    save()


def observe_rejected_edit():
    case = STATE["case"]
    receipt = json.loads((L.evidence / "substantive-B2-and-archive.push.json").read_text())
    check("queued-edit push returned rejection", receipt["exit"] != 0, True)
    check("rejection identifies queued branch protection", "GH006" in receipt["stderr"] and "queued for merging cannot be updated" in receipt["stderr"], True)
    head = "refs/heads/" + case["heads"]["B"]["ref"]
    archive = "refs/tags/" + case["prefix"] + "/authored/B/v2"
    observations = []
    for index in range(7):
        if index:
            time.sleep(3 if index < 4 else 5)
        snap = snapshot("after-rejected-edit-" + str(index))
        check("rejected edit retains original B " + str(index), snap["refs"][head], case["heads"]["B"]["sha"])
        check("atomic rejection leaves no archive v2 " + str(index), archive in snap["refs"], False)
        observations.append(snap)
        print("AFTER_REJECTED_EDIT " + json.dumps({"at": lab.now(), "queue_entries": snap["graphql"]["data"]["mergeQueue"]["entries"]["nodes"]}), flush=True)
    STATE["after_rejected_edit"] = observations
    STATE["old_async_after_rejected_edit"] = poll_old("old-async-after-rejected-edit")
    save()
    cleanup()
    STATE["old_async_after_cleanup"] = poll_old("old-async-after-rejected-edit-cleanup")
    STATE["final"] = snapshot("final-after-rejected-edit-cleanup")
    save()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=["setup", "probe", "observe-rejected-edit", "cleanup"])
    args = p.parse_args()
    lab.save(HOME / ("environment-" + args.phase + ".json"), {"at": lab.now(), "repository": lab.REPO,
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "shared_lab_sha256": hashlib.sha256((HOME.parent / "lab.py").read_bytes()).hexdigest()})
    try:
        if STATE["phases"].get(args.phase) == "complete":
            raise RuntimeError("Phase already complete; inspect retained results instead of replaying.")
        {"setup": setup, "probe": probe, "observe-rejected-edit": observe_rejected_edit, "cleanup": cleanup}[args.phase]()
        STATE["phases"][args.phase] = "complete"
        save()
        print(json.dumps({"phase": args.phase, "status": "complete", "case": STATE.get("case"), "checks": len(STATE["checks"])}), flush=True)
        return 0
    except Exception:
        STATE["phases"][args.phase] = "stopped"
        save()
        target = L.evidence / (args.phase + "-failure-" + str(time.time_ns()) + ".txt")
        target.write_text(traceback.format_exc())
        print(json.dumps({"phase": args.phase, "status": "stopped", "failure": str(target)}), flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
