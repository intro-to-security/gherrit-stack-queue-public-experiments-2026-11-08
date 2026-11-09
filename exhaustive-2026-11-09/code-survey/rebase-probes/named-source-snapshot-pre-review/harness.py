"""New isolated numeric-repository rebase experiments; never replay a write."""
import argparse
import concurrent.futures
import datetime
import hashlib
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
CONTROL = ROOT.parents[1] / "control"
REPO = "joshlf/gherrit-native-stack-experiments-2026-11-08"
REPOSITORY_ID = 1450723431
GH = "/opt/homebrew/bin/gh"
NOTICE = "*Authored by an AI agent acting on joshlf's behalf.*"
SPECS = {
    "capability": 3, "wrong-lower": 3, "wrong-upper": 3,
    "conflict-middle": 3, "overlap-vector": 5, "stale-vector": 3,
}
OID = re.compile(r"^[0-9a-f]{40}$")


def stamp():
    return {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "monotonic": time.monotonic()}


def directory_sync(path):
    fd = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def save(path, data):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as file:
        json.dump(data, file, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)
    directory_sync(path.parent)


def begin(label, data):
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", label):
        raise ValueError("Unsafe journal label")
    EVIDENCE.mkdir(exist_ok=True)
    path = EVIDENCE / (label + ".intent.json")
    record = {**data, "start": stamp()}
    with path.open("x") as file:
        json.dump(record, file, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())
    directory_sync(path.parent)
    return record


def command(args, *, input=None, env=None):
    return subprocess.run(args, input=input, env=env, capture_output=True, text=True)


def git(*args, input=None, env=None, check=True):
    result = command(["git", "-c", "core.hooksPath=" + str(HOOKS), "-C", str(GIT), *args], input=input, env=env)
    if check and result.returncode:
        raise RuntimeError("Owned Git operation failed: " + result.stderr)
    return result.stdout.strip() if check else result


def case_path(name):
    return ROOT / (name + ".case.json")


def own_ref(case, ref):
    if case["prefix"] != "exh-1109-causal-rb-" + case["name"]:
        raise ValueError("Fixture prefix does not match its allocation")
    prefix = "refs/heads/" + case["prefix"] + "/"
    if not ref.startswith(prefix) or ref[len(prefix):] not in ["trunk", *list("ABCDE")[:SPECS[case["name"]]]]:
        raise ValueError("Ref escapes its independent fixture")
    return ref


def route(case):
    if not isinstance(case.get("stack"), int) or isinstance(case["stack"], bool) or case["stack"] <= 0:
        raise ValueError("Owned native group identity is invalid")
    return f"repositories/{REPOSITORY_ID}/stacks/{case['stack']}/rebase"


def vector(case, variant=None):
    result = {str(case["prs"][letter]): head["sha"] for letter, head in case["heads"].items()}
    if variant == "wrong-lower":
        result[str(case["prs"]["A"])] = case["trunk_sha"]
    elif variant == "wrong-upper":
        top = list(case["heads"])[-1]
        previous = list(case["heads"])[-2]
        result[str(case["prs"][top])] = case["heads"][previous]["sha"]
    return {"expected_head_oid_by_pr_number": result}


def guard_http(case, method, path, payload):
    repo = "repos/" + REPO
    if method == "GET" and (path == repo or path.startswith(repo + "/") or (case.get("stack") and path == route(case))):
        return
    if method == "POST" and path == "graphql":
        query = (payload or {}).get("query", "")
        if query.startswith("query") and "mutation" not in query.lower() and 'repository(owner:"joshlf",name:"gherrit-native-stack-experiments-2026-11-08")' in query:
            return
    if method == "POST" and path == repo + "/pulls":
        for field in ("base", "head"):
            own_ref(case, "refs/heads/" + payload[field])
        return
    if method == "POST" and path == repo + "/stacks" and payload == {"pull_requests": list(case["prs"].values())} and len(case["prs"]) == SPECS[case["name"]]:
        return
    if method == "PUT" and case.get("stack") and path == route(case):
        mapping = (payload or {}).get("expected_head_oid_by_pr_number")
        if isinstance(payload, dict) and set(payload) == {"expected_head_oid_by_pr_number"} and isinstance(mapping, dict) and set(mapping) == {str(number) for number in case["prs"].values()} and all(isinstance(sha, str) and OID.fullmatch(sha) for sha in mapping.values()):
            return
    raise ValueError("HTTP operation escapes the granted rebase scope")


def api(case, label, method, path, payload=None):
    guard_http(case, method, path, payload)
    record = begin(label, {"kind": "http", "case": case["name"], "method": method, "path": path, "payload": payload})
    args = [GH, "api", "--include", "-H", "X-GitHub-Api-Version: 2026-03-10", "-X", method, path]
    if payload is not None:
        request_path = EVIDENCE / (label + ".request.json")
        save(request_path, payload)
        args += ["--input", str(request_path)]
    result = command(args)
    response = re.sub(r"(?im)^(set-cookie|authorization):.*$", r"\1: [redacted]", result.stdout)
    (EVIDENCE / (label + ".response.txt")).write_text(response)
    (EVIDENCE / (label + ".stderr.txt")).write_text(result.stderr)
    match = re.search(r"^HTTP/\S+\s+(\d+)", response)
    parts = re.split(r"\r?\n\r?\n", response, maxsplit=1)
    try:
        data = json.loads(parts[1]) if len(parts) > 1 and parts[1].strip() else None
    except ValueError:
        data = None
    record.update(end=stamp(), exit=result.returncode, http=int(match.group(1)) if match else None, data=data)
    record["disposition"] = "response-retained" if match else "unknown-outcome"
    save(EVIDENCE / (label + ".receipt.json"), record)
    if not match or (path == "graphql" and isinstance(data, dict) and data.get("errors")):
        raise RuntimeError("Unknown HTTP outcome or invalid read; freeze without retry: " + label)
    return record


def git_read(label, args):
    record = begin(label, {"kind": "git-read", "args": args})
    result = git(*args, check=False)
    record.update(end=stamp(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    save(EVIDENCE / (label + ".receipt.json"), record)
    if result.returncode:
        raise RuntimeError("Git read unavailable: " + label)
    return record


def push(case, label, updates, expected, *, stacked=False):
    if set(updates) != set(expected) or not updates:
        raise ValueError("Every push update requires an explicit lease")
    for ref in updates:
        own_ref(case, ref)
        if not OID.fullmatch(updates[ref]) or (expected[ref] and not OID.fullmatch(expected[ref])):
            raise ValueError("Invalid push object or lease")
    args = ["push", "--porcelain", "--atomic"]
    args += ["--force-with-lease=" + ref + ":" + expected[ref] for ref in updates]
    if stacked:
        args += ["-o", "pull.stacked"]
    args += ["origin"] + [sha + ":" + ref for ref, sha in updates.items()]
    record = begin(label, {"kind": "git-push", "case": case["name"], "updates": updates, "expected": expected, "args": args})
    result = git(*args, check=False)
    record.update(end=stamp(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    save(EVIDENCE / (label + ".receipt.json"), record)
    if result.returncode:
        raise RuntimeError("Push rejected or uncertain; reconcile read-only without retry: " + label)
    return record


def commit(label, parent, files):
    start = stamp()
    index = ROOT / (label + ".index")
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    git("read-tree", parent, env=env)
    for path, value in files.items():
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise ValueError("Invalid synthetic file path")
        blob = git("hash-object", "-w", "--stdin", input=value)
        git("update-index", "--add", "--cacheinfo", "100644," + blob + "," + path, env=env)
    tree = git("write-tree", env=env)
    message = "Record synthetic rebase probe " + label + "\n\nAgent-authored-by: AI agent acting on joshlf's behalf\n"
    sha = git("commit-tree", tree, "-p", parent, input=message)
    git("update-ref", "refs/inputs/" + label, sha)
    save(EVIDENCE / (label + ".commit.json"), {"start": start, "end": stamp(), "sha": sha, "parent": parent, "tree": tree, "files": files, "message": message})
    index.unlink(missing_ok=True)
    return sha


def initialize(case):
    HOOKS.mkdir(exist_ok=True)
    if not GIT.exists():
        result = command(["git", "init", "--bare", str(GIT)])
        if result.returncode:
            raise RuntimeError("Private Git initialization failed")
        git("config", "core.hooksPath", str(HOOKS))
        git("config", "user.name", "Josh Liebow-Feeser")
        git("config", "user.email", "hello@joshlf.com")
        git("remote", "add", "origin", "https://github.com/" + REPO + ".git")
    if git("config", "--get", "core.hooksPath") != str(HOOKS):
        raise RuntimeError("Private hooks are not disabled")
    metadata = api(case, case["name"] + "-repository", "GET", "repos/" + REPO)
    if metadata["http"] != 200 or metadata["data"].get("id") != REPOSITORY_ID or metadata["data"].get("full_name") != REPO:
        raise RuntimeError("Repository identity premise failed")
    git_read(case["name"] + "-seed-fetch", ["fetch", "--no-tags", "origin", "main:refs/remotes/origin/main"])
    return git("rev-parse", "refs/remotes/origin/main")


def fixture(name):
    if case_path(name).exists():
        raise RuntimeError("Existing case is never redispatched; reconcile read-only")
    if name != "capability":
        proof = ROOT / "capability-proof.json"
        if not proof.exists() or not json.loads(proof.read_text()).get("capability_proven"):
            raise RuntimeError("Positive capability premise has not been exercised")
    case = {"name": name, "prefix": "exh-1109-causal-rb-" + name, "repository": REPO, "repository_id": REPOSITORY_ID, "heads": {}, "prs": {}, "phase": "local-preparation", "created": stamp()}
    save(case_path(name), case)
    seed = initialize(case)
    parent = commit(name + "-trunk", seed, {name + "/base.txt": "base=0\n", name + "/shared.txt": "base\n"})
    case.update(trunk=case["prefix"] + "/trunk", trunk_sha=parent)
    updates = {"refs/heads/" + case["trunk"]: parent}
    for letter in "ABCDE"[:SPECS[name]]:
        files = {name + "/" + letter + ".txt": letter + "=1\n"}
        if name == "conflict-middle" and letter == "B":
            files[name + "/shared.txt"] = "B\n"
        sha = commit(name + "-" + letter, parent, files)
        case["heads"][letter] = {"ref": case["prefix"] + "/" + letter, "sha": sha}
        updates["refs/heads/" + case["heads"][letter]["ref"]] = sha
        parent = sha
    save(case_path(name), case)
    push(case, name + "-initial", updates, {ref: "" for ref in updates})
    parent_ref = case["trunk"]
    for letter, head in case["heads"].items():
        time.sleep(1)
        response = api(case, name + "-pr-" + letter, "POST", "repos/" + REPO + "/pulls", {"head": head["ref"], "base": parent_ref, "title": "Native rebase probe " + name + " " + letter, "body": "Independent synthetic native rebase fixture.\n\n" + NOTICE})
        if response["http"] != 201:
            raise RuntimeError("PR creation not acknowledged as expected")
        created = response["data"] or {}
        number = created.get("number")
        if not isinstance(number, int) or number <= 0 or number in case["prs"].values() or created.get("head", {}).get("ref") != head["ref"] or created.get("base", {}).get("ref") != parent_ref:
            raise RuntimeError("Created PR identity does not bind the owned head/base")
        case["prs"][letter] = number
        save(case_path(name), case)
        parent_ref = head["ref"]
    time.sleep(1)
    response = api(case, name + "-register", "POST", "repos/" + REPO + "/stacks", {"pull_requests": list(case["prs"].values())})
    if response["http"] != 201:
        raise RuntimeError("Native group creation not acknowledged as expected")
    group = response["data"] or {}
    number = group.get("number")
    members = group.get("pull_requests") or []
    if not isinstance(number, int) or number <= 0 or [member.get("number") for member in members] != list(case["prs"].values()):
        raise RuntimeError("Created group identity/membership is not the owned vector")
    case["stack"] = number
    advance = {name + "/shared.txt": "trunk\n"} if name == "conflict-middle" else {name + "/trunk-advance.txt": "advanced\n"}
    case["advanced_trunk_sha"] = commit(name + "-advance-trunk", case["trunk_sha"], advance)
    if name == "capability":
        case["expected_rebased_trees"] = {}
        for letter, head in case["heads"].items():
            expected = commit(name + "-expected-tree-" + letter, head["sha"], advance)
            case["expected_rebased_trees"][letter] = git("rev-parse", expected + "^{tree}")
    save(case_path(name), case)
    ref = "refs/heads/" + case["trunk"]
    time.sleep(1)
    push(case, name + "-advance-trunk", {ref: case["advanced_trunk_sha"]}, {ref: case["trunk_sha"]})
    case["phase"] = "fixture-ready"
    save(case_path(name), case)
    return case


EVENT_FIELDS = """__typename
... on HeadRefForcePushedEvent { id createdAt actor { login __typename } beforeCommit { oid } afterCommit { oid } ref { name target { oid } } }
... on BaseRefChangedEvent { id createdAt actor { login __typename } previousRefName currentRefName }
... on AutomaticBaseChangeSucceededEvent { id createdAt actor { login __typename } oldBase newBase }
... on AutomaticBaseChangeFailedEvent { id createdAt actor { login __typename } oldBase newBase }
"""


def observe_refs(case, label):
    result = git_read(label, ["ls-remote", "origin", "refs/heads/" + case["prefix"] + "/*"])
    result["refs"] = {line.split("\t")[1]: line.split("\t")[0] for line in result["stdout"].splitlines()}
    result["fetch"] = git_read(label + "-objects", ["fetch", "--no-tags", "origin", "+refs/heads/" + case["prefix"] + "/*:refs/observed/" + case["name"] + "/*"])
    result["objects"] = {}
    for sha in set(result["refs"].values()):
        obj = git("show", "-s", "--format=%H%x00%T%x00%P", sha, check=False)
        if obj.returncode:
            result["objects"][sha] = {"disposition": "not-obtained-by-later-fetch"}
        else:
            oid, tree, parents = obj.stdout.strip().split("\0")
            result["objects"][sha] = {"oid": oid, "tree": tree, "parents": parents.split()}
    return result


def observe_prs(case, label):
    fields = []
    for letter, number in case["prs"].items():
        fields.append(letter + ":pullRequest(number:" + str(number) + "){ number id state merged mergedAt headRefName headRefOid baseRefName baseRefOid timelineItems(last:100,itemTypes:[HEAD_REF_FORCE_PUSHED_EVENT,BASE_REF_CHANGED_EVENT,AUTOMATIC_BASE_CHANGE_SUCCEEDED_EVENT,AUTOMATIC_BASE_CHANGE_FAILED_EVENT]){pageInfo{hasPreviousPage} nodes{" + EVENT_FIELDS + "}}}")
    query = 'query { repository(owner:"joshlf",name:"gherrit-native-stack-experiments-2026-11-08"){' + " ".join(fields) + "}}"
    response = api(case, label, "POST", "graphql", {"query": query})
    if response["http"] != 200:
        raise RuntimeError("PR/event observation failed")
    return response


def observe(case, label):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        refs = executor.submit(observe_refs, case, label + "-refs")
        prs = executor.submit(observe_prs, case, label + "-prs")
        result = {"refs": refs.result(), "prs": prs.result()}
    save(EVIDENCE / (label + ".observation.json"), result)
    return result


def job_disposition(case, body):
    if not isinstance(body, dict):
        raise ValueError("Rebase job body is unavailable")
    state = body.get("job_state", body.get("status"))
    if state in {"pending", "queued", "running", "in_progress"}:
        return {"phase": "pending"}
    if state != "done":
        raise ValueError("Unrecognized rebase job state: " + str(state))
    results = body.get("pull_requests")
    if not isinstance(results, list) or not all(isinstance(item, dict) and isinstance(item.get("pull_request_number"), int) and isinstance(item.get("status"), str) for item in results):
        raise ValueError("Done rebase job has no complete typed per-PR results")
    numbers = [item["pull_request_number"] for item in results]
    complete = len(numbers) == len(set(numbers)) and set(numbers) == set(case["prs"].values())
    return {"phase": "done", "complete_member_results": complete, "all_succeeded": complete and all(item["status"] == "succeeded" for item in results), "results": results}


def poll_job(case, initial):
    latest = initial
    try:
        job_disposition(case, latest["data"])
    except ValueError:
        # A known admission response need not contain the polling response shape.
        latest = api(case, case["name"] + "-first-status-read", "GET", route(case))
        if latest["http"] != 200:
            raise RuntimeError("Admission retained; first read-only job reconciliation unavailable")
    for index in range(90):
        disposition = job_disposition(case, latest["data"])
        if disposition["phase"] == "done":
            case.update(terminal=latest, job_disposition=disposition)
            save(case_path(case["name"]), case)
            return disposition
        time.sleep(1)
        latest = api(case, case["name"] + "-poll-" + str(index), "GET", route(case))
        if latest["http"] != 200:
            raise RuntimeError("Rebase job read unavailable; retain pending scope")
    case.update(last_pending=latest, phase="pending-after-bounded-poll")
    save(case_path(case["name"]), case)
    raise RuntimeError("Rebase still pending after bounded reads; no completion claim")


def full_rewrite_premise(case, observation):
    remote = observation["refs"]["refs"]
    prs = observation["prs"]["data"]["data"]["repository"]
    parent = remote["refs/heads/" + case["trunk"]]
    if parent != case.get("advanced_trunk_sha"):
        return False
    for letter, head in case["heads"].items():
        current = remote["refs/heads/" + head["ref"]]
        obj = observation["refs"]["objects"].get(current, {})
        if current == head["sha"] or prs[letter]["headRefOid"] != current or obj.get("parents") != [parent] or obj.get("tree") != case.get("expected_rebased_trees", {}).get(letter) or prs[letter]["state"] != "OPEN":
            return False
        parent = current
    return True


def await_full_rewrite(case):
    start = time.monotonic()
    for index in range(16):
        observation = observe(case, case["name"] + "-rewrite-premise-" + str(index))
        if full_rewrite_premise(case, observation):
            return observation
        if time.monotonic() - start > 30:
            break
        time.sleep(1)
    raise RuntimeError("Complete rewrite observation premise missed its bounded window")


def publish_marker(case):
    terminal = case["terminal"]
    if not case["job_disposition"]["all_succeeded"]:
        raise ValueError("Marker requires captured complete successful job")
    top = list(case["heads"])[-1]
    ref = "refs/heads/" + case["heads"][top]["ref"]
    git_read(case["name"] + "-marker-fetch", ["fetch", "--no-tags", "origin", ref])
    before = git("rev-parse", "FETCH_HEAD")
    nonce = uuid.uuid4().hex
    sha = commit(case["name"] + "-marker", before, {case["name"] + "/marker.txt": "unique-marker=" + nonce + "\n"})
    record = {"ref": ref, "before": before, "marker": sha, "nonce": nonce, "terminal_receipt_end": terminal["end"]}
    save(EVIDENCE / (case["name"] + "-marker-before-dispatch.json"), record)
    record["push"] = push(case, case["name"] + "-marker", {ref: sha}, {ref: before})
    case["marker"] = {key: record[key] for key in ("ref", "before", "marker", "nonce")}
    save(EVIDENCE / (case["name"] + "-marker.json"), record)
    save(case_path(case["name"]), case)


def observe_window(case, seconds=30):
    targets = (0, 1, 3, 10, 30, 60) if seconds == 60 else (0, 1, 3, 10, 30)
    start = time.monotonic()
    for index, target in enumerate(targets):
        delay = target - (time.monotonic() - start)
        if delay > 0:
            time.sleep(delay)
        observe(case, case["name"] + "-after-" + str(index))


def execute(name):
    case = fixture(name)
    observe(case, name + "-before-request")
    case["expected_vector"] = vector(case, name)
    save(case_path(name), case)
    if name == "stale-vector":
        b = commit(name + "-legitimate-B2", case["heads"]["A"]["sha"], {name + "/B.txt": "B=2\n"})
        c = commit(name + "-legitimate-C2", b, {name + "/C.txt": "C=1\n"})
        updates = {"refs/heads/" + case["heads"]["B"]["ref"]: b, "refs/heads/" + case["heads"]["C"]["ref"]: c}
        expected = {"refs/heads/" + case["heads"][letter]["ref"]: case["heads"][letter]["sha"] for letter in "BC"}
        push(case, name + "-legitimate-edit", updates, expected, stacked=True)
        observe(case, name + "-after-legitimate-edit")
    request = api(case, name + "-request", "PUT", route(case), case["expected_vector"])
    case["request"] = request
    save(case_path(name), case)
    if request["http"] not in {200, 202}:
        case.update(phase="request-rejected-frozen", rejected_http=request["http"])
        save(case_path(name), case)
        observe_window(case)
        return
    try:
        initial = job_disposition(case, request["data"])
    except ValueError as error:
        initial = {"phase": "unrecognized-admission-shape", "read_only_reconciliation_required": True, "reason": str(error)}
        case["initial_disposition"] = initial
        save(case_path(name), case)
    if name == "overlap-vector" and initial["phase"] == "pending":
        second = api(case, name + "-deliberate-overlap", "PUT", route(case), vector(case, "wrong-upper"))
        case["second_request"] = second
        case["overlap_attribution"] = "Per-stack result route; no request UUID assumed."
        save(case_path(name), case)
    disposition = poll_job(case, request)
    after = observe(case, name + "-after-job")
    if name == "capability":
        if not disposition["all_succeeded"]:
            raise RuntimeError("Positive capability did not report all members succeeded")
        after = await_full_rewrite(case)
        proof = {"capability_proven": True, "repository": REPO, "repository_id": REPOSITORY_ID, "case": name, "stack": case["stack"], "terminal": case["terminal"], "observation": after, "claim": "This explicit job and captured vector only; no future-write exclusion promise."}
        save(ROOT / "capability-proof.json", proof)
        publish_marker(case)
    observe_window(case, seconds=60 if case.get("marker") else 30)
    case.update(phase="bounded-observations-complete", observation_end=stamp())
    save(case_path(name), case)


def check():
    for name in SPECS:
        case = {"name": name, "prefix": "exh-1109-causal-rb-" + name, "prs": {letter: index + 1 for index, letter in enumerate("ABCDE"[:SPECS[name]])}, "heads": {letter: {"sha": str(index + 1) * 40} for index, letter in enumerate("ABCDE"[:SPECS[name]])}, "trunk_sha": "a" * 40, "stack": 99}
        guard_http(case, "PUT", route(case), vector(case))
        own_ref(case, "refs/heads/" + case["prefix"] + "/trunk")
    print(json.dumps({"local_scope_checks": "passed", "network_calls": 0, "cases": list(SPECS)}))


def validate_grant(path, grant, name):
    resolved = Path(path).resolve()
    if resolved.parent != CONTROL.resolve() or grant.get("grant_path") != str(resolved):
        raise ValueError("Grant must name its exact root-owned control path")
    source_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if grant.get("harness_sha256") != source_sha:
        raise ValueError("Live harness SHA256 differs from root's reviewed grant")
    if grant.get("coordinator") != "root" or grant.get("repository") != REPO or grant.get("repository_id") != REPOSITORY_ID or name not in grant.get("cases", []):
        raise ValueError("Grant does not authorize this case/repository identity")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("check", "run", "observe"))
    parser.add_argument("case", nargs="?", choices=tuple(SPECS))
    parser.add_argument("--grant", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        check()
        return
    if args.command == "observe":
        case = json.loads(case_path(args.case).read_text())
        label = args.case + "-reconcile-" + uuid.uuid4().hex[:10]
        if case.get("stack"):
            api(case, label + "-job", "GET", route(case))
        observe(case, label)
        return
    if not args.grant:
        parser.error("Root's exact rebase case grant is required")
    grant = json.loads(args.grant.read_text())
    try:
        validate_grant(args.grant, grant, args.case)
    except ValueError as error:
        parser.error(str(error))
    if case_path(args.case).exists():
        parser.error("Existing case execution is forbidden; use read-only observe")
    try:
        execute(args.case)
    except Exception as error:
        if case_path(args.case).exists():
            case = json.loads(case_path(args.case).read_text())
            case.update(phase="frozen-requires-read-only-reconciliation", stop_reason=str(error))
            save(case_path(args.case), case)
        save(ROOT / (args.case + ".STOP.json"), {"at": stamp(), "error": str(error), "policy": "No automatic write retry."})
        raise


if __name__ == "__main__":
    main()
