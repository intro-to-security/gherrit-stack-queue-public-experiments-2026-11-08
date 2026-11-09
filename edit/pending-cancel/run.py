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
SPEC = importlib.util.spec_from_file_location("public_edit_lab", HOME.parents[1] / "lab.py")
lab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab)
L = lab.Lane("edit")
L.home = HOME
L.evidence = HOME / "evidence"
L.evidence.mkdir(parents=True, exist_ok=True)
L.gitdir = HOME / "git"
L.state_path = HOME / "fixtures.json"
STATE_PATH = HOME / "state.json"
STATE = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {
    "name": "pending-admission-dequeue-" + str(time.time_ns()), "checks": [], "phases": {}}
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



def race():
    case = STATE["case"]
    before = snapshot("before-race")
    data = before["graphql"]["data"]
    check("both source gates CLEAN before race", [data[k]["mergeStateStatus"] for k in ["a", "b"]], ["CLEAN", "CLEAN"])
    queue = data["mergeQueue"]
    check("queue empty before one admission", queue["entries"]["nodes"] if queue else [], [])
    selected = case["heads"]["B"]["sha"]
    node = data["b"]["id"]
    path = API + "/pulls/" + str(case["prs"]["B"]) + "/merge-async"
    enqueue_body = {"merge_action": "merge_queue", "sha": selected}
    dequeue_query = "mutation($id:ID!,$nonce:String!){dequeuePullRequest(input:{id:$id,clientMutationId:$nonce}){clientMutationId}}"
    dequeue_variables = {"id": node, "nonce": STATE["name"] + "-immediate-B"}
    lab.save(L.evidence / "prepared-race-intent.json", {"at": lab.now(), "selected_B": selected,
        "enqueue_path": path, "enqueue_body": enqueue_body, "dequeue_query": dequeue_query,
        "dequeue_variables": dequeue_variables, "required_order": "202 pending receipt, immediately dequeue B, then poll/read"})
    request = L.api("race-enqueue-B", "PUT", path, enqueue_body)
    if request.get("http") != 202 or not isinstance(request.get("data"), dict) or request["data"].get("status") != "pending":
        STATE["admission_request"] = request
        save()
        raise RuntimeError("This single race needs a 202 pending receipt; preserve outcome and do not repeat admission.")
    immediate = L.graphql("race-immediate-dequeue-B", dequeue_query, dequeue_variables)
    STATE["admission_request"] = request
    STATE["immediate_dequeue"] = immediate
    STATE["uuid"] = request["data"]["details"]["uuid"]
    STATE["client_gap_seconds"] = immediate["monotonic_start"] - request["monotonic_end"]
    save()
    print("IMMEDIATE_PAIR " + json.dumps({"uuid": STATE["uuid"], "enqueue_interval": [request["start"], request["end"]],
        "dequeue_interval": [immediate["start"], immediate["end"]], "client_gap_seconds": STATE["client_gap_seconds"],
        "dequeue_http": immediate["http"], "dequeue_data": immediate["data"]}), flush=True)
    check("admission receipt selected SHA", request["data"]["details"]["expected_head_sha"], selected)
    check("admission receipt queue action", request["data"]["details"]["merge_action"], "merge_queue")
    check("immediate dequeue has a known HTTP response", immediate["http"], 200)
    check("no response parse error on dequeue", bool(immediate.get("parse_error")), False)
    polls = []
    for index in range(20):
        raw = L.api("race-original-poll-" + str(index), "GET", path + "/" + STATE["uuid"], fresh=True)
        outcome = good(raw)
        polls.append(raw)
        if outcome["status"] != "pending":
            break
        time.sleep(2)
    STATE["original_polls"] = polls
    STATE["original_last_result"] = outcome
    observations = []
    for index in range(4):
        if index:
            time.sleep(3)
        observed = snapshot("after-race-" + str(index))
        observations.append(observed)
        print("RACE_OBSERVATION " + json.dumps({"at": lab.now(), "entries": observed["graphql"]["data"]["mergeQueue"]["entries"]["nodes"], "original_status": outcome["status"]}), flush=True)
    STATE["observations"] = observations
    dq_data = immediate["data"] or {}
    errors = dq_data.get("errors", [])
    messages = [error.get("message", "") for error in errors]
    selected_seen = any(case["prs"]["B"] in [n["pullRequest"]["number"] for n in snap["graphql"]["data"]["mergeQueue"]["entries"]["nodes"]] for snap in observations)
    known_success = not errors and (dq_data.get("data") or {}).get("dequeuePullRequest") is not None
    if errors and outcome["status"] == "enqueued" and selected_seen:
        interpretation = "The immediate dequeue was rejected; the one original admission subsequently reported enqueued and selected B was observed queued. Record the exact rejection reason before calling it not-queued."
    elif known_success and outcome["status"] == "enqueued" and not selected_seen:
        interpretation = "Immediate dequeue succeeded; the original request retained terminal enqueued, while selected B was absent from later queue samples. This does not distinguish removal after admission from cancellation of pending work."
    else:
        interpretation = "Observed ordering only; retained request, dequeue response and queue samples do not establish a pending-request cancellation contract."
    STATE["interpretation"] = {"text": interpretation, "dequeue_errors": messages, "dequeue_known_success": known_success,
        "selected_B_seen_after_pair": selected_seen, "original_status": outcome["status"]}
    save()
    if outcome["status"] == "pending":
        raise RuntimeError("Original admission remained pending at finite bound; no blind mutation retry or assumed cancellation.")
    cleanup()
    STATE["original_after_cleanup"] = poll_old("original-after-known-membership-cleanup")
    STATE["final"] = snapshot("final-after-known-membership-cleanup")
    save()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=["setup", "race", "cleanup"])
    args = p.parse_args()
    lab.save(HOME / ("environment-" + args.phase + ".json"), {"at": lab.now(), "repository": lab.REPO,
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "shared_lab_sha256": hashlib.sha256((HOME.parents[1] / "lab.py").read_bytes()).hexdigest()})
    try:
        if STATE["phases"].get(args.phase) == "complete":
            raise RuntimeError("Phase already complete; inspect retained results instead of replaying.")
        {"setup": setup, "race": race, "cleanup": cleanup}[args.phase]()
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
