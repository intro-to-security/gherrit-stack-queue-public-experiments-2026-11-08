"""One separately granted named-route initiation on the known404 fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time

import harness as h

CASE = "capability-named-route"
PATH = "repos/" + h.REPO + "/stacks/653/rebase"
STATE = h.ROOT / "named-alias.case.json"


def validate_scope(case):
    if case.get("name") != "capability" or case.get("prefix") != "exh-1109-causal-rb-capability" or case.get("repository") != h.REPO or case.get("repository_id") != h.REPOSITORY_ID or case.get("stack") != 653 or case.get("prs") != {"A": 650, "B": 651, "C": 652} or (case.get("request") or {}).get("http") != 404:
        raise ValueError("Existing fixture is not the root-reviewed known404 scope")


def grant_check(path, grant):
    resolved = Path(path).resolve()
    if resolved.parent != h.CONTROL.resolve() or grant.get("grant_path") != str(resolved):
        raise ValueError("Exact root control grant path required")
    hashes = {"named_probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "harness_sha256": hashlib.sha256(Path(h.__file__).read_bytes()).hexdigest()}
    if any(grant.get(key) != value for key, value in hashes.items()):
        raise ValueError("Reviewed helper/base-harness source hash differs")
    if grant.get("coordinator") != "root" or grant.get("repository") != h.REPO or grant.get("repository_id") != h.REPOSITORY_ID or grant.get("cases") != [CASE] or grant.get("request_path") != PATH:
        raise ValueError("Grant does not bind this single named request")


def fresh_payload(case, repository, stack, observation, node_ids):
    validate_scope(case)
    if repository.get("id") != h.REPOSITORY_ID or repository.get("full_name") != h.REPO or stack.get("number") != 653 or stack.get("base", {}).get("ref") != case["trunk"]:
        raise ValueError("Fresh repository/group/trunk identity mismatch")
    members = stack.get("pull_requests") or []
    if [member.get("number") for member in members] != [650, 651, 652]:
        raise ValueError("Fresh native member identity/order changed")
    remote = observation["refs"]["refs"]
    prs = observation["prs"]["data"]["data"]["repository"]
    if remote.get("refs/heads/" + case["trunk"]) != case["advanced_trunk_sha"]:
        raise ValueError("Owned advanced trunk changed")
    payload = {}
    parent_ref = case["trunk"]
    for (letter, head), member in zip(case["heads"].items(), members):
        pr = prs[letter]
        expected = head["sha"]
        if member.get("state") != "open" or member.get("merged_at") is not None or member.get("head", {}).get("ref") != head["ref"] or member.get("head", {}).get("sha") != expected or member.get("base", {}).get("ref") != parent_ref or remote.get("refs/heads/" + head["ref"]) != expected or pr.get("number") != case["prs"][letter] or pr.get("headRefOid") != expected or pr.get("headRefName") != head["ref"] or pr.get("baseRefName") != parent_ref or pr.get("state") != "OPEN" or pr.get("id") != node_ids[letter]:
            raise ValueError("Fresh PR/head/ref/base/canonical identity drift: " + letter)
        payload[str(member["number"])] = member["head"]["sha"]
        parent_ref = head["ref"]
    return {"expected_head_oid_by_pr_number": payload}


def initiate(case, payload):
    validate_scope(case)
    if payload != h.vector(case):
        raise ValueError("Named request is not the complete checked current vector")
    label = "capability-named-init-001"
    record = h.begin(label, {"kind": "named-rebase-initiation", "method": "PUT", "path": PATH, "payload": payload, "api_version": "2026-03-10", "authority": "Separate root named-route decision after known numeric404; never a numeric retry."})
    request_path = h.EVIDENCE / (label + ".request.json")
    h.save(request_path, payload)
    result = h.command([h.GH, "api", "--include", "-X", "PUT", "-H", "X-GitHub-Api-Version: 2026-03-10", PATH, "--input", str(request_path)])
    response = re.sub(r"(?im)^(set-cookie|authorization):.*$", r"\1: [redacted]", result.stdout)
    (h.EVIDENCE / (label + ".response.txt")).write_text(response)
    (h.EVIDENCE / (label + ".stderr.txt")).write_text(result.stderr)
    match = re.search(r"^HTTP/\S+\s+(\d+)", response)
    parts = re.split(r"\r?\n\r?\n", response, maxsplit=1)
    try:
        data = json.loads(parts[1]) if len(parts) > 1 and parts[1].strip() else None
    except ValueError:
        data = None
    record.update(end=h.stamp(), exit=result.returncode, http=int(match.group(1)) if match else None, data=data)
    record["disposition"] = "response-retained" if match else "unknown-outcome"
    h.save(h.EVIDENCE / (label + ".receipt.json"), record)
    if not match:
        raise RuntimeError("Named initiation acknowledgement unknown; never resend")
    return record


def execute():
    if STATE.exists() or (h.EVIDENCE / "capability-named-init-001.intent.json").exists():
        raise RuntimeError("Named initiation scope already retained; no repetition")
    case = json.loads(h.case_path("capability").read_text())
    validate_scope(case)
    state = {"scope": CASE, "phase": "checking-fresh-premises", "created": h.stamp(), "original_numeric_request": case["request"]}
    h.save(STATE, state)
    repository = h.api(case, "named-fresh-repository", "GET", "repos/" + h.REPO)
    stack = h.api(case, "named-fresh-stack", "GET", "repos/" + h.REPO + "/stacks/653")
    if repository["http"] != 200 or stack["http"] != 200:
        raise RuntimeError("Fresh repository/group read unavailable; no initiation")
    observation = h.observe(case, "named-fresh-graph")
    node_ids = {letter: json.loads((h.EVIDENCE / ("capability-pr-" + letter + ".receipt.json")).read_text())["data"]["node_id"] for letter in "ABC"}
    payload = fresh_payload(case, repository["data"], stack["data"], observation, node_ids)
    state.update(fresh_repository=repository, fresh_stack=stack, fresh_observation=observation, payload=payload, phase="prepared")
    h.save(STATE, state)
    request = initiate(case, payload)
    state["request"] = request
    h.save(STATE, state)
    if request["http"] == 404:
        state.update(phase="known404-frozen", final_observation=h.observe(case, "named-after404"))
        h.save(STATE, state)
        return
    # Known non404 and unknown response shapes are reconciled using reads only.
    state["reads"] = []
    start = time.monotonic()
    for index, target in enumerate((0, 1, 3, 7, 15, 30, 60)):
        delay = target - (time.monotonic() - start)
        if delay > 0:
            time.sleep(delay)
        reads = {"named": h.api(case, "named-status-" + str(index), "GET", PATH), "numeric": h.api(case, "named-numeric-status-" + str(index), "GET", h.route(case)), "observation": h.observe(case, "named-readback-" + str(index))}
        state["reads"].append(reads)
        h.save(STATE, state)
    state.update(phase="bounded-read-only-reconciliation-complete", marker_dispatches=0)
    h.save(STATE, state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grant", type=Path, required=True)
    args = parser.parse_args()
    try:
        grant_check(args.grant, json.loads(args.grant.read_text()))
    except ValueError as error:
        parser.error(str(error))
    if STATE.exists():
        parser.error("Named scope already exists; read-only inspection only")
    try:
        execute()
    except Exception as error:
        if STATE.exists():
            state = json.loads(STATE.read_text())
            state.update(phase="frozen-no-retry", stop_reason=str(error))
            h.save(STATE, state)
        h.save(h.ROOT / "named-alias.STOP.json", {"at": h.stamp(), "error": str(error), "policy": "No repeated initiation, marker or new fixture."})
        raise
