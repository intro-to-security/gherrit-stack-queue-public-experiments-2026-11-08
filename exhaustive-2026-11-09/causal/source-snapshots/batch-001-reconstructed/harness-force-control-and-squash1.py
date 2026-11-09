"""Isolated recorded causal probes. Hosted writes require an explicit case grant."""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
GIT = ROOT / "git"
HOOKS = ROOT / "empty-hooks"
REPO = "joshlf/gherrit-native-stack-experiments-2026-11-08"
PREFIX = "exh-1109-causal-"
GH = "/opt/homebrew/bin/gh"
NOTICE = "*Authored by an AI agent acting on joshlf's behalf.*"
CASES = {
    "force-control": {"count": 2, "method": None, "timing": "control"},
    "post-squash-1": {"count": 2, "method": "squash", "timing": "post"},
    "post-rebase-3": {"count": 4, "method": "rebase", "timing": "post"},
    "post-merge-1": {"count": 2, "method": "merge", "timing": "post"},
    "post-squash-3": {"count": 4, "method": "squash", "timing": "post"},
    "early-squash-3": {"count": 4, "method": "squash", "timing": "early"},
}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def stamp():
    return {"utc": now(), "monotonic": time.monotonic()}


def flush_directory(path):
    directory = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def save(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w") as file:
        json.dump(value, file, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())
    os.replace(temp, path)
    flush_directory(path.parent)


def run(args, *, input=None, env=None):
    return subprocess.run(args, input=input, text=True, capture_output=True, env=env)


def git(*args, input=None, env=None, check=True):
    result = run(["git", "-c", "core.hooksPath=" + str(HOOKS), "-C", str(GIT), *args], input=input, env=env)
    if check and result.returncode:
        raise RuntimeError("Git failed: " + result.stderr)
    return result.stdout.strip() if check else result


def begin(label, record):
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", label):
        raise ValueError("Unsafe evidence label")
    EVIDENCE.mkdir(exist_ok=True)
    path = EVIDENCE / (label + ".intent.json")
    # Exclusive creation prevents accidental redispatch even after a known receipt.
    with path.open("x") as file:
        json.dump({**record, "start": stamp()}, file, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())
    flush_directory(path.parent)
    return json.loads(path.read_text())


def constrained_ref(ref):
    if not re.fullmatch(r"refs/heads/exh-1109-causal-[a-z0-9-]+/(trunk|[A-F])", ref):
        raise ValueError("Ref is outside the granted causal namespace: " + ref)
    return ref


def allowed_http(method, path, payload, case):
    if method == "GET" and path.startswith("repos/" + REPO + "/"):
        return
    if method == "POST" and path == "graphql":
        query = payload.get("query", "")
        if "mutation" not in query.lower() and query.startswith("query"):
            return
    root = "repos/" + REPO
    if method == "POST" and path == root + "/pulls":
        for field in ("head", "base"):
            ref = "refs/heads/" + payload[field]
            constrained_ref(ref)
            if not payload[field].startswith(case["prefix"] + "/"):
                raise ValueError("Cross-fixture PR")
        return
    numbers = set(case.get("prs", {}).values())
    if method == "POST" and path == root + "/stacks" and set(payload["pull_requests"]) == numbers and len(numbers) >= 2:
        return
    if method == "PUT" and path == root + "/pulls/" + str(case.get("prs", {}).get("A")) + "/merge-async":
        if payload == {"merge_method": case["method"], "merge_action": "direct_merge", "sha": case["heads"]["A"]["sha"]}:
            return
    raise ValueError("HTTP operation is outside this lane's effect policy")


def api(label, method, path, payload=None, *, case):
    allowed_http(method, path, payload, case)
    record = begin(label, {"kind": "http", "method": method, "path": path, "payload": payload})
    args = [GH, "api", "--include", "-H", "X-GitHub-Api-Version: 2026-03-10", "-X", method, path]
    if payload is not None:
        request_path = EVIDENCE / (label + ".request.json")
        save(request_path, payload)
        args += ["--input", str(request_path)]
    result = run(args)
    # gh supplies authentication internally. No token or request authorization header is logged.
    response = re.sub(r"(?im)^(set-cookie|authorization):.*$", r"\1: [redacted]", result.stdout)
    (EVIDENCE / (label + ".response.txt")).write_text(response)
    (EVIDENCE / (label + ".stderr.txt")).write_text(result.stderr)
    match = re.search(r"^HTTP/\S+\s+(\d+)", response)
    status = int(match.group(1)) if match else None
    parts = re.split(r"\r?\n\r?\n", response, maxsplit=1)
    try:
        data = json.loads(parts[1]) if len(parts) > 1 and parts[1].strip() else None
    except json.JSONDecodeError:
        data = None
    record.update(end=stamp(), exit=result.returncode, http=status, data=data)
    record["disposition"] = "response-retained" if status is not None else "unknown-outcome"
    save(EVIDENCE / (label + ".receipt.json"), record)
    if status is None or (method == "POST" and path == "graphql" and isinstance(data, dict) and data.get("errors")):
        raise RuntimeError("Unknown HTTP outcome or invalid observation; freeze and reconcile " + label)
    return record


def git_read(label, args):
    record = begin(label, {"kind": "git-read", "args": args})
    result = git(*args, check=False)
    record.update(end=stamp(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    save(EVIDENCE / (label + ".receipt.json"), record)
    if result.returncode:
        raise RuntimeError("Git observation failed: " + label)
    return record


def push(label, updates, expected):
    if set(updates) != set(expected):
        raise ValueError("Every update needs an explicit lease")
    for ref in updates:
        constrained_ref(ref)
    args = ["push", "--porcelain", "--atomic"]
    args += ["--force-with-lease=" + ref + ":" + expected[ref] for ref in updates]
    args += ["origin"] + [sha + ":" + ref for ref, sha in updates.items()]
    record = begin(label, {"kind": "git-push", "updates": updates, "expected": expected, "args": args})
    result = git(*args, check=False)
    record.update(end=stamp(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    record["disposition"] = "success-receipt" if result.returncode == 0 else "requires-read-only-reconciliation"
    save(EVIDENCE / (label + ".receipt.json"), record)
    if result.returncode:
        raise RuntimeError("Push failed or outcome uncertain; freeze and reconcile " + label)
    return record


def initialize():
    HOOKS.mkdir(exist_ok=True)
    if not GIT.exists():
        result = run(["git", "init", "--bare", str(GIT)])
        if result.returncode:
            raise RuntimeError(result.stderr)
        git("config", "core.hooksPath", str(HOOKS))
        git("config", "user.name", "Josh Liebow-Feeser")
        git("config", "user.email", "hello@joshlf.com")
        git("remote", "add", "origin", "https://github.com/" + REPO + ".git")
    if git("config", "--get", "core.hooksPath") != str(HOOKS):
        raise RuntimeError("Owned checkout hooks are not disabled")
    label = "seed-fetch-" + uuid.uuid4().hex[:10]
    git_read(label, ["fetch", "--no-tags", "origin", "main:refs/remotes/origin/main"])
    return git("rev-parse", "refs/remotes/origin/main")


def commit(label, parent, files, subject):
    start = stamp()
    index = ROOT / (label + ".index")
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    git("read-tree", parent, env=env)
    for path, value in files.items():
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise ValueError("Unsafe synthetic path")
        blob = git("hash-object", "-w", "--stdin", input=value)
        git("update-index", "--add", "--cacheinfo", "100644," + blob + "," + path, env=env)
    tree = git("write-tree", env=env)
    message = subject + "\n\nAgent-authored-by: AI agent acting on joshlf's behalf\n"
    sha = git("commit-tree", tree, "-p", parent, input=message)
    git("update-ref", "refs/inputs/" + label, sha)
    save(EVIDENCE / (label + ".commit.json"), {"start": start, "end": stamp(), "sha": sha, "parent": parent, "tree": tree, "files": files, "message": message})
    index.unlink(missing_ok=True)
    return sha


def case_path(name):
    return ROOT / (name + ".case.json")


def require_status(response, status):
    if response["http"] != status:
        raise RuntimeError("Unexpected known HTTP response; stop without retry: " + str(response["http"]))


def fixture(name):
    path = case_path(name)
    if path.exists():
        raise RuntimeError("Case already has durable identity; use read-only reconciliation")
    spec = CASES[name]
    case = {"name": name, "prefix": PREFIX + name, "method": spec["method"], "timing": spec["timing"], "created": stamp(), "prs": {}, "heads": {}, "phase": "local-preparation"}
    save(path, case)
    seed = initialize()
    parent = commit(name + "-trunk", seed, {name + "/base.txt": "base=0\n"}, "Record synthetic causal trunk " + name)
    case["trunk_sha"] = parent
    case["trunk"] = case["prefix"] + "/trunk"
    updates = {"refs/heads/" + case["trunk"]: parent}
    for letter in "ABCDEF"[:spec["count"]]:
        sha = commit(name + "-" + letter, parent, {name + "/" + letter + ".txt": letter + "=1\n"}, "Record synthetic causal " + name + " " + letter)
        case["heads"][letter] = {"ref": case["prefix"] + "/" + letter, "sha": sha}
        updates["refs/heads/" + case["heads"][letter]["ref"]] = sha
        parent = sha
    case["phase"] = "publishing-fixture"
    save(path, case)
    push(name + "-initial-push", updates, {ref: "" for ref in updates})
    parent_ref = case["trunk"]
    for letter, head in case["heads"].items():
        time.sleep(1)
        response = api(name + "-create-pr-" + letter, "POST", "repos/" + REPO + "/pulls", {"head": head["ref"], "base": parent_ref, "title": "Causal experiment " + name + " " + letter, "body": "Synthetic causal fixture; no production changes.\n\n" + NOTICE}, case=case)
        require_status(response, 201)
        case["prs"][letter] = response["data"]["number"]
        save(path, case)
        parent_ref = head["ref"]
    if case["method"]:
        time.sleep(1)
        response = api(name + "-register", "POST", "repos/" + REPO + "/stacks", {"pull_requests": list(case["prs"].values())}, case=case)
        require_status(response, 201)
        case["stack"] = response["data"]["number"]
    case["phase"] = "fixture-ready"
    save(path, case)
    return case


EVENT_FIELDS = """__typename
... on HeadRefForcePushedEvent { id createdAt actor { login __typename } beforeCommit { oid } afterCommit { oid } ref { name target { oid } } }
... on BaseRefChangedEvent { id createdAt actor { login __typename } previousRefName currentRefName }
... on AutomaticBaseChangeSucceededEvent { id createdAt actor { login __typename } oldBase newBase }
... on AutomaticBaseChangeFailedEvent { id createdAt actor { login __typename } oldBase newBase }
... on MergedEvent { id createdAt actor { login __typename } commit { oid } mergeRefName }
"""


def refs(case, label):
    result = git_read(label, ["ls-remote", "origin", "refs/heads/" + case["prefix"] + "/*"])
    result["refs"] = dict((line.split("\t")[1], line.split("\t")[0]) for line in result["stdout"].splitlines())
    result["object_fetch"] = git_read(label + "-objects", ["fetch", "--no-tags", "origin", "+refs/heads/" + case["prefix"] + "/*:refs/observed/" + case["name"] + "/*"])
    result["objects"] = {}
    for sha in set(result["refs"].values()):
        obj = git("show", "-s", "--format=%H%x00%T%x00%P", sha, check=False)
        if obj.returncode:
            result["objects"][sha] = {"disposition": "object-unavailable-after-later-fetch", "stderr": obj.stderr}
        else:
            oid, tree, parents = obj.stdout.strip().split("\0")
            result["objects"][sha] = {"oid": oid, "tree": tree, "parents": parents.split()}
    return result


def graphql(case, label):
    fields = []
    for letter, number in case["prs"].items():
        fields.append(letter + ":pullRequest(number:" + str(number) + "){ number id state merged mergedAt headRefName headRefOid baseRefName baseRefOid timelineItems(last:100,itemTypes:[HEAD_REF_FORCE_PUSHED_EVENT,BASE_REF_CHANGED_EVENT,AUTOMATIC_BASE_CHANGE_SUCCEEDED_EVENT,AUTOMATIC_BASE_CHANGE_FAILED_EVENT,MERGED_EVENT]){pageInfo{hasPreviousPage} nodes{" + EVENT_FIELDS + "}}}")
    query = 'query { repository(owner:"joshlf",name:"gherrit-native-stack-experiments-2026-11-08"){' + " ".join(fields) + "}}"
    response = api(label, "POST", "graphql", {"query": query}, case=case)
    require_status(response, 200)
    return response


def observe(case, label):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        ref_result = executor.submit(refs, case, label + "-refs")
        event_result = executor.submit(graphql, case, label + "-events")
        result = {"refs": ref_result.result(), "graphql": event_result.result()}
    save(EVIDENCE / (label + ".observation.json"), result)
    return result


def publish_marker(case, label, *, terminal=None, sibling=False):
    if terminal is not None and terminal["data"].get("status") != "merged":
        raise ValueError("Post-terminal marker requires a terminal merged receipt")
    target = list(case["heads"])[-1]
    ref = "refs/heads/" + case["heads"][target]["ref"]
    # Fetch captures the actual current remote head and obtains its objects in one read.
    fresh = git_read(label + "-fetch", ["fetch", "--no-tags", "origin", ref])
    before = git("rev-parse", "FETCH_HEAD")
    nonce = uuid.uuid4().hex
    parent = git("rev-parse", before + "^") if sibling else before
    marker = commit(label, parent, {case["name"] + "/marker.txt": "unique-marker=" + nonce + "\n"}, "Record unique causal marker " + nonce)
    result = {"target": target, "ref": ref, "before": before, "marker": marker, "nonce": nonce, "fetch": fresh, "terminal_receipt_end": terminal["end"] if terminal else None, "commit_record": str(EVIDENCE / (label + ".commit.json"))}
    save(EVIDENCE / (label + ".marker-before-dispatch.json"), result)
    result["push"] = push(label + "-push", {ref: marker}, {ref: before})
    save(EVIDENCE / (label + ".marker.json"), result)
    case["marker"] = {key: result[key] for key in ("target", "ref", "before", "marker", "nonce")}
    case["phase"] = "marker-published"
    save(case_path(case["name"]), case)
    return result


def poll(case, accepted):
    details = (accepted.get("data") or {}).get("details") or {}
    operation = details.get("uuid")
    if not operation:
        raise RuntimeError("No operation identity; freeze and reconcile")
    case["merge_uuid"] = operation
    save(case_path(case["name"]), case)
    for index in range(90):
        response = api(case["name"] + "-poll-" + str(index), "GET", "repos/" + REPO + "/pulls/" + str(case["prs"]["A"]) + "/merge-async/" + operation, case=case)
        require_status(response, 200)
        status = (response.get("data") or {}).get("status")
        if status != "pending":
            case["terminal"] = response
            save(case_path(case["name"]), case)
            return response
        time.sleep(0.5)
    raise RuntimeError("Operation lacks terminal receipt after bounded polling; freeze")


def sample_window(case):
    start = time.monotonic()
    for index, target in enumerate((0, 1, 3, 7, 15, 30, 60)):
        delay = target - (time.monotonic() - start)
        if delay > 0:
            time.sleep(delay)
        observe(case, case["name"] + "-after-" + str(index))
    case["phase"] = "bounded-observations-complete"
    case["observation_end"] = stamp()
    save(case_path(case["name"]), case)


def execute(name):
    case = fixture(name)
    observe(case, name + "-before")
    if case["timing"] == "control":
        publish_marker(case, name + "-marker", sibling=True)
    else:
        response = api(name + "-merge", "PUT", "repos/" + REPO + "/pulls/" + str(case["prs"]["A"]) + "/merge-async", {"merge_method": case["method"], "merge_action": "direct_merge", "sha": case["heads"]["A"]["sha"]}, case=case)
        require_status(response, 202)
        if case["timing"] == "early":
            publish_marker(case, name + "-marker")
        terminal = poll(case, response)
        if terminal["data"].get("status") != "merged":
            raise RuntimeError("Native merge did not succeed; no post-terminal marker")
        if case["timing"] == "post":
            publish_marker(case, name + "-marker", terminal=terminal)
    sample_window(case)


def self_check():
    constrained_ref("refs/heads/exh-1109-causal-post-squash-1/B")
    for ref in ("refs/heads/main", "refs/heads/exp/api/old/B", "refs/heads/exh-1109-ui-other/A", "refs/tags/exh-1109-causal-case/A"):
        try:
            constrained_ref(ref)
        except ValueError:
            pass
        else:
            raise AssertionError("Forbidden ref accepted")
    case = {"prefix": PREFIX + "self", "prs": {"A": 1, "B": 2}, "method": "squash", "heads": {"A": {"sha": "a" * 40}}}
    allowed_http("POST", "repos/" + REPO + "/stacks", {"pull_requests": [1, 2]}, case)
    for method, path, payload in (("PATCH", "repos/" + REPO, {}), ("POST", "graphql", {"query": "mutation { nope }"}), ("PUT", "repos/" + REPO + "/pulls/999/merge-async", {})):
        try:
            allowed_http(method, path, payload, case)
        except ValueError:
            pass
        else:
            raise AssertionError("Forbidden API mutation accepted")
    print(json.dumps({"self_check": "passed", "network_calls": 0, "cases": list(CASES)}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("check", "run", "observe"))
    parser.add_argument("case", nargs="?", choices=tuple(CASES))
    parser.add_argument("--grant", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        self_check()
    elif args.command == "observe":
        case = json.loads(case_path(args.case).read_text())
        observe(case, args.case + "-reconcile-" + uuid.uuid4().hex[:10])
    else:
        if not args.grant:
            parser.error("Hosted writes require root's explicit JSON case grant")
        grant = json.loads(args.grant.read_text())
        if grant.get("repository") != REPO or args.case not in grant.get("cases", []) or grant.get("coordinator") != "root":
            parser.error("Grant does not authorize this exact case/repository")
        try:
            execute(args.case)
        except Exception as error:
            save(ROOT / (args.case + ".STOP.json"), {"at": stamp(), "error": str(error), "policy": "No automatic write retry; read-only reconciliation required."})
            raise


if __name__ == "__main__":
    main()
