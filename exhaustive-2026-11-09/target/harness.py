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
REPO = "joshlf/gherrit-native-stack-experiments-2026-11-08"
PREFIX = "exh-1109-target-profile001-"
GH = "/opt/homebrew/bin/gh"
NOTICE = "*Authored by an AI agent acting on joshlf's behalf.*"
TRAILER = "Agent-authored-by: AI agent acting on joshlf's behalf"
ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_TERMINAL_PROMPT="0",
           PYTHONDONTWRITEBYTECODE="1", XDG_CACHE_HOME=str(ROOT / "cache"))
SPECS = json.loads((ROOT / "harness-outline.json").read_text())["fixtures"]
POLICY = json.loads((ROOT / "branch-protection.proposed.json").read_text())
RULE = json.loads((ROOT / "ruleset.proposed.json").read_text())


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp-" + str(os.getpid()))
    with temp.open("w") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def nonce(label):
    return label + "-" + uuid.uuid4().hex[:12]


def state(name):
    return read(ROOT / "cases" / (name + ".json"))


def save_case(case):
    save(ROOT / "cases" / (case["name"] + ".json"), case)


def validate_grant():
    grant = read(ROOT.parent / "control" / "target-grant-001.json")
    if grant["repository"] != REPO or grant["prefix"] != PREFIX or set(grant["cases"]) != set(SPECS):
        raise ValueError("grant_identity_mismatch")
    if grant["max_new_refs"] != 14 or grant["max_new_prs"] != 9 or "policy_delegation" not in grant:
        raise ValueError("grant_scope_mismatch")
    return grant


def ref(name):
    if not re.fullmatch(re.escape(PREFIX) + r"[ufmrp]-(?:trunk|A|B)", name):
        raise ValueError("outside_exact_target_refs")
    fixture = name[len(PREFIX)]
    if fixture == "p" and name.endswith("-B"):
        raise ValueError("ungranted_second_P_layer")
    return name


def owns(case, number):
    return number in case.get("prs", {}).values()


def guard(method, path, payload, case=None):
    validate_grant()
    base = "repos/" + REPO
    if method == "GET" and path.startswith(base + "/") and not any(x in path for x in ("/secrets", "/environments", "/hooks", "/collaborators")):
        return
    if method == "POST" and path == "graphql" and payload.get("query", "").startswith("query") and "mutation" not in payload["query"].lower():
        return
    if method == "POST" and path == base + "/rulesets" and payload == RULE:
        return
    policy_refs = {SPECS[x]["trunk"] for x in "umrp"}
    for trunk in policy_refs:
        endpoint = base + "/branches/" + trunk + "/protection"
        if method == "PUT" and path == endpoint and payload == POLICY:
            return
        if method == "DELETE" and path == endpoint:
            owned = read(ROOT / "policy-owned.json")
            if trunk in owned.get("protections", []):
                return
    if method == "DELETE" and path.startswith(base + "/rulesets/"):
        owned = read(ROOT / "policy-owned.json")
        if path == base + "/rulesets/" + str(owned.get("ruleset_id")):
            return
    if case is None or case.get("name") not in SPECS:
        raise ValueError("missing_owned_case")
    name = case["name"]
    if method == "POST" and path == base + "/pulls":
        if payload["base"] in [SPECS[name]["trunk"], PREFIX + name + "-A"] and payload["head"] in [PREFIX + name + "-A", PREFIX + name + "-B"]:
            ref(payload["head"])
            ref(payload["base"])
            if payload["head"] == PREFIX + name + "-A" and payload["base"] != SPECS[name]["trunk"]:
                raise ValueError("wrong_lower_base")
            if payload["head"].endswith("-B") and payload["base"] != PREFIX + name + "-A":
                raise ValueError("wrong_upper_base")
            return
    if method == "POST" and path == base + "/stacks" and name != "p" and payload == {"pull_requests": [case["prs"]["A"], case["prs"]["B"]]}:
        return
    if method == "POST" and name == "p" and path == base + "/statuses/" + case["heads"]["A"]["sha"]:
        if payload == dict(state="success", context="Validate and Test", description="Synthetic user-producer negative control; no software test claim"):
            return
    if method == "PUT" and path == base + "/pulls/" + str(case.get("prs", {}).get("A")) + "/merge-async":
        if name != "f" and payload == dict(sha=case["heads"]["A"]["sha"], merge_method=SPECS[name]["method"], merge_action="direct_merge"):
            return
    if method == "PATCH" and path.startswith(base + "/pulls/") and payload == {"state": "closed"}:
        if path.rsplit("/", 1)[1].isdigit() and owns(case, int(path.rsplit("/", 1)[1])):
            return
    raise ValueError("outside_target_effect_policy")


def begin(label, record):
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", label):
        raise ValueError("unsafe_attempt_label")
    path = ROOT / "evidence" / (label + ".intent.json")
    path.parent.mkdir(exist_ok=True)
    with path.open("x") as stream:
        active = read(ROOT / "source-active.json") if (ROOT / "source-active.json").exists() else None
        json.dump(dict(record, start=now(), source_snapshot=active), stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return read(path)


def api(label, method, path, payload=None, case=None):
    verify_source()
    guard(method, path, payload, case)
    record = begin(label, dict(method=method, path=path, payload=payload))
    args = [GH, "api", "--include", "-H", "X-GitHub-Api-Version: 2026-03-10", "-X", method, path]
    if payload is not None:
        request = ROOT / "evidence" / (label + ".request.json")
        save(request, payload)
        args += ["--input", str(request)]
    result = subprocess.run(args, text=True, capture_output=True, env=ENV)
    raw = re.sub(r"(?im)^(authorization|set-cookie):.*$", r"\1: [redacted]", result.stdout)
    (ROOT / "evidence" / (label + ".response.txt")).write_text(raw)
    (ROOT / "evidence" / (label + ".stderr.txt")).write_text(result.stderr)
    status = re.search(r"^HTTP/\S+\s+(\d+)", raw)
    code = int(status.group(1)) if status else None
    body = re.split(r"\r?\n\r?\n", raw, maxsplit=1)
    try:
        data = json.loads(body[1]) if len(body) > 1 and body[1].strip() else None
    except ValueError:
        data = None
    record.update(end=now(), exit=result.returncode, http=code, data=data,
                  disposition="response-retained" if code else "unknown-outcome-freeze")
    save(ROOT / "evidence" / (label + ".receipt.json"), record)
    if code is None:
        raise RuntimeError("unknown_HTTP_outcome_no_retry:" + label)
    return record


def get(path, label="read"):
    return api(nonce(label), "GET", "repos/" + REPO + "/" + path)


def require(response, allowed):
    if response["http"] not in allowed:
        raise RuntimeError("known_response_requires_review:" + str(response["http"]) + ":" + response["path"])
    return response["data"]


def git(*args, stdin=None, env=None, allowed=(0,)):
    cmd = ["git", "-c", "core.hooksPath=/dev/null", "-c", "credential.helper=", "-c",
           "credential.helper=!" + GH + " auth git-credential", "-C", str(ROOT / "git"), *args]
    result = subprocess.run(cmd, input=stdin, text=True, capture_output=True, env=env or ENV)
    with (ROOT / "git-commands.jsonl").open("a") as stream:
        stream.write(json.dumps(dict(argv=cmd, stdin=stdin, exit=result.returncode, stdout=result.stdout, stderr=result.stderr, time=now())) + "\n")
    if result.returncode not in allowed:
        raise RuntimeError("git_failure:" + result.stderr)
    return result


def initialize():
    validate_grant()
    if not (ROOT / "git").exists():
        result = subprocess.run(["git", "init", "--bare", str(ROOT / "git")], text=True, capture_output=True, env=ENV)
        if result.returncode:
            raise RuntimeError(result.stderr)
        for key, value in [("user.name", "Josh Liebow-Feeser"), ("user.email", "hello@joshlf.com"), ("core.hooksPath", "/dev/null")]:
            git("config", "--local", key, value)
        git("remote", "add", "origin", "https://github.com/" + REPO + ".git")
    if git("remote", "get-url", "origin").stdout.strip() != "https://github.com/" + REPO + ".git":
        raise ValueError("wrong_git_destination")


def commit(label, files, parent=None):
    index = ROOT / ("index-" + uuid.uuid4().hex)
    env = dict(ENV, GIT_INDEX_FILE=str(index))
    git("read-tree", "--empty", env=env)
    for path, contents in files.items():
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise ValueError("unsafe_fixture_path")
        blob = git("hash-object", "-w", "--stdin", stdin=contents).stdout.strip()
        git("update-index", "--add", "--cacheinfo", "100644", blob, path, env=env)
    tree = git("write-tree", env=env).stdout.strip()
    args = ["commit-tree", tree] + (["-p", parent] if parent else [])
    sha = git(*args, stdin="Record synthetic target " + label + "\n\n" + TRAILER + "\n").stdout.strip()
    git("update-ref", "refs/inputs/" + label, sha)
    index.unlink()
    save(ROOT / "evidence" / (label + ".commit.json"), dict(sha=sha, tree=tree, parent=parent, files=files))
    return sha


def push(label, updates, expected):
    verify_source()
    validate_grant()
    if set(updates) != set(expected):
        raise ValueError("missing_exact_push_lease")
    for target in updates:
        if not target.startswith("refs/heads/"):
            raise ValueError("wrong_ref_family")
        ref(target[len("refs/heads/"):])
    args = ["push", "--atomic", "--porcelain"] + ["--force-with-lease=" + target + ":" + expected[target] for target in updates]
    args += ["origin"] + [sha + ":" + target for target, sha in updates.items()]
    record = begin(label, dict(kind="git-push", updates=updates, expected=expected, args=args))
    result = git(*args, allowed=(0, 1, 128))
    record.update(end=now(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    save(ROOT / "evidence" / (label + ".receipt.json"), record)
    if result.returncode:
        raise RuntimeError("push_requires_readonly_reconciliation:" + label)
    actual = git("ls-remote", "origin", *updates).stdout
    found = {line.split("\t")[1]: line.split("\t")[0] for line in actual.splitlines()}
    if found != updates:
        raise RuntimeError("push_readback_disagreement")


def fixture(name):
    initialize()
    path = ROOT / "cases" / (name + ".json")
    if path.exists():
        raise RuntimeError("case_already_allocated_reconcile_instead:" + name)
    spec = SPECS[name]
    workflow = (ROOT / "minimal-ci.yml").read_text()
    if name == "f":
        workflow = workflow.replace("  pull_request:\n", "  pull_request:\n    branches: [" + spec["trunk"] + "]\n", 1)
    if name == "p":
        workflow = workflow.replace("name: Validate and Test", "name: Wrong context - target probe")
    files = {".github/workflows/ci.yml": workflow, "fixture.txt": "Synthetic target compatibility fixture " + name + "\n"}
    trunk = commit(name + "-trunk", files)
    case = dict(name=name, trunk=spec["trunk"], trunk_sha=trunk, heads={}, prs={}, files=files, native=[], phase="local-prepared")
    updates = {"refs/heads/" + spec["trunk"]: trunk}
    parent = trunk
    for layer in "AB"[:spec["layers"]]:
        files = dict(files, **{layer + ".txt": "layer " + layer + "\n"})
        sha = commit(name + "-" + layer, files, parent)
        case["heads"][layer] = dict(ref=PREFIX + name + "-" + layer, sha=sha, files=files)
        updates["refs/heads/" + PREFIX + name + "-" + layer] = sha
        parent = sha
    save_case(case)
    found = git("ls-remote", "origin", *updates).stdout
    if found.strip():
        raise RuntimeError("occupied_target_namespace")
    push(name + "-initial-push", updates, {target: "" for target in updates})
    case["phase"] = "refs-published"
    save_case(case)
    return case


def protect():
    if (ROOT / "policy-owned.json").exists():
        raise RuntimeError("policy_ownership_already_exists_reconcile")
    for name in "umrp":
        if state(name)["phase"] != "refs-published":
            raise RuntimeError("trunk_not_known_owned")
    existing = require(get("rulesets?per_page=100", "policy-before-rulesets"), [200])
    if any(item["name"] == RULE["name"] for item in existing):
        raise RuntimeError("existing_named_ruleset")
    owned = dict(protections=[], ruleset_id=None, grant="target-grant-001")
    save(ROOT / "policy-owned.json", owned)
    for name in "umrp":
        trunk = SPECS[name]["trunk"]
        before = get("branches/" + trunk + "/protection", "policy-before-" + name)
        require(before, [404])
        require(api("policy-apply-" + name, "PUT", "repos/" + REPO + "/branches/" + trunk + "/protection", POLICY), [200])
        owned["protections"].append(trunk)
        save(ROOT / "policy-owned.json", owned)
    response = api("policy-create-ruleset", "POST", "repos/" + REPO + "/rulesets", RULE)
    data = require(response, [201])
    owned["ruleset_id"] = data["id"]
    save(ROOT / "policy-owned.json", owned)
    return policy_snapshot("installed")


def policy_snapshot(label):
    owned = read(ROOT / "policy-owned.json")
    ruleset = require(get("rulesets/" + str(owned["ruleset_id"]), label + "-ruleset"), [200])
    for key in ("name", "target", "enforcement", "conditions", "bypass_actors"):
        if ruleset[key] != RULE[key]:
            raise RuntimeError("ruleset_ownership_or_scope_changed:" + key)
    target_rules = {x["type"]: x for x in ruleset["rules"]}
    for requested in RULE["rules"]:
        observed = target_rules[requested["type"]]
        for key, value in requested.get("parameters", {}).items():
            if observed.get("parameters", {}).get(key) != value:
                raise RuntimeError("ruleset_parameter_changed:" + requested["type"] + ":" + key)
    snapshots = {}
    for name in "umrp":
        trunk = SPECS[name]["trunk"]
        protection = require(get("branches/" + trunk + "/protection", label + "-protection-" + name), [200])
        checks = protection["required_status_checks"]
        if checks["strict"] is not True or checks["checks"] != POLICY["required_status_checks"]["checks"]:
            raise RuntimeError("classic_check_policy_changed")
        for field in ("enforce_admins", "required_linear_history", "required_conversation_resolution"):
            if protection[field]["enabled"] is not True:
                raise RuntimeError("classic_policy_changed:" + field)
        effective = require(get("rules/branches/" + trunk, label + "-effective-" + name), [200])
        snapshots[name] = dict(protection=protection, effective_rules=effective)
    save(ROOT / ("policy-snapshot-" + label + ".json"), dict(ruleset=ruleset, trunks=snapshots))
    return snapshots


def create_prs(name):
    case = state(name)
    if case["prs"]:
        raise RuntimeError("existing_PR_identity_reconcile")
    base = case["trunk"]
    for layer, head in case["heads"].items():
        payload = dict(head=head["ref"], base=base, title="Target profile minimal probe " + name.upper() + " " + layer,
                       body="Synthetic target CI/rule fixture. Minimal payload only; full Rust CI does not run.\n\n" + NOTICE)
        data = require(api(name + "-create-" + layer, "POST", "repos/" + REPO + "/pulls", payload, case), [201])
        case["prs"][layer] = data["number"]
        save_case(case)
        base = head["ref"]
    case["phase"] = "prs-open-before-membership"
    save_case(case)
    return case


def pr(case, layer):
    data = require(get("pulls/" + str(case["prs"][layer]), case["name"] + "-pr-" + layer), [200])
    if data["head"]["ref"] != case["heads"][layer]["ref"]:
        raise RuntimeError("PR_head_identity_changed")
    return data


def observation(name, label):
    case = state(name)
    result = dict(time=now(), prs={})
    for layer in case["prs"]:
        data = pr(case, layer)
        source = data["head"]["sha"]
        checks = require(get("commits/" + source + "/check-runs?per_page=100", label + "-source-checks-" + layer), [200])
        statuses = require(get("commits/" + source + "/status?per_page=100", label + "-source-statuses-" + layer), [200])
        merge = data.get("merge_commit_sha")
        candidate_checks = require(get("commits/" + merge + "/check-runs?per_page=100", label + "-merge-checks-" + layer), [200, 404, 422]) if merge else None
        runs = require(get("actions/runs?head_sha=" + source + "&per_page=100", label + "-runs-" + layer), [200])
        result["prs"][layer] = dict(pr=data, source_checks=checks, source_statuses=statuses,
                                    merge_checks=candidate_checks, runs=runs)
    save(ROOT / "observations" / (label + ".json"), result)
    return result


def wait_ci(name, label, expected_layers, seconds=240):
    deadline = time.monotonic() + seconds
    n = 0
    while True:
        snapshot = observation(name, label + "-" + str(n))
        ready = True
        for layer in expected_layers:
            records = snapshot["prs"][layer]["source_checks"]["check_runs"]
            desired = "Wrong context - target probe" if name == "p" and state(name).get("p_stage") is None else "Validate and Test"
            matching = [record for record in records if record["name"] == desired and record["app"]["id"] == 15368]
            if not matching or any(record["status"] != "completed" for record in matching):
                ready = False
        if ready or time.monotonic() >= deadline:
            save(ROOT / "observations" / (label + "-final.json"), dict(ready=ready, snapshot=snapshot))
            return snapshot
        time.sleep(10)
        n += 1


def register(name):
    case = state(name)
    if case.get("stack"):
        raise RuntimeError("already_registered")
    data = require(api(name + "-register", "POST", "repos/" + REPO + "/stacks",
                       dict(pull_requests=[case["prs"]["A"], case["prs"]["B"]]), case), [201])
    case["stack"] = data["number"]
    case["phase"] = "registered"
    save_case(case)
    return case


def amend(name, layer, label, fail=False, required_context=True):
    case = state(name)
    fresh = pr(case, layer)
    if fresh["state"] != "open" or fresh["merged"]:
        raise RuntimeError("canonical_PR_not_open")
    if case["native"] and any(x.get("terminal") is None for x in case["native"]):
        raise RuntimeError("unknown_old_native_effect")
    before = fresh["head"]["sha"]
    files = dict(case["heads"][layer]["files"])
    files[layer + ".txt"] = "amended " + label + "\n"
    if name == "p" and required_context:
        files[".github/workflows/ci.yml"] = (ROOT / "minimal-ci.yml").read_text()
        case["p_stage"] = label
    if fail:
        files[".fixture-fail"] = "known expected failure\n"
    else:
        files.pop(".fixture-fail", None)
    parent = case["trunk_sha"] if layer == "A" else case["heads"]["A"]["sha"]
    sha = commit(label, files, parent)
    push(label + "-push", {"refs/heads/" + case["heads"][layer]["ref"]: sha},
         {"refs/heads/" + case["heads"][layer]["ref"]: before})
    case["heads"][layer].update(sha=sha, files=files)
    save_case(case)
    return case


def request_merge(name, label):
    case = state(name)
    if name == "f":
        raise ValueError("no_filter_control_landing")
    if any(record.get("terminal") is None for record in case["native"]):
        raise RuntimeError("unknown_prior_request")
    policy_snapshot(label + "-fresh")
    fresh = pr(case, "A")
    if fresh["head"]["sha"] != case["heads"]["A"]["sha"] or fresh["state"] != "open":
        raise RuntimeError("merge_input_changed")
    payload = dict(sha=case["heads"]["A"]["sha"], merge_method=SPECS[name]["method"], merge_action="direct_merge")
    record = dict(label=label, payload=payload, terminal=None)
    case["native"].append(record)
    save_case(case)
    response = api(label, "PUT", "repos/" + REPO + "/pulls/" + str(case["prs"]["A"]) + "/merge-async", payload, case)
    record["response"] = response
    save_case(case)
    if response["http"] != 202:
        if 400 <= response["http"] < 500 and response["http"] != 409:
            record["terminal"] = dict(status="request-rejected", response=response)
        else:
            record["recovery"] = "HTTP response does not establish absence of effects; freeze and reconcile"
        save_case(case)
        return record
    operation = ((response["data"] or {}).get("details") or {}).get("uuid")
    if not operation:
        raise RuntimeError("accepted_without_operation_identity_freeze")
    record["uuid"] = operation
    save_case(case)
    deadline = time.monotonic() + 300
    n = 0
    while True:
        result = get("pulls/" + str(case["prs"]["A"]) + "/merge-async/" + operation, label + "-poll-" + str(n))
        data = require(result, [200])
        record["latest"] = result
        if data.get("status") != "pending":
            record["terminal"] = data
            save_case(case)
            return record
        save_case(case)
        if time.monotonic() >= deadline:
            return record
        time.sleep(2)
        n += 1


def logs(name, label):
    snapshot = observation(name, label + "-snapshot")
    found = {}
    for layer, data in snapshot["prs"].items():
        for run in data["runs"]["workflow_runs"]:
            identity = str(run["id"])
            if identity in found or run["status"] != "completed":
                continue
            jobs = require(get("actions/runs/" + identity + "/jobs?per_page=100", label + "-jobs"), [200])
            result = subprocess.run([GH, "run", "view", identity, "--repo", REPO, "--log"], text=True, capture_output=True, env=ENV)
            path = ROOT / "logs" / (identity + ".txt")
            path.parent.mkdir(exist_ok=True)
            path.write_text(result.stdout)
            path.with_suffix(".stderr.txt").write_text(result.stderr)
            contexts = []
            for line in result.stdout.splitlines():
                if '"scope": "Minimal synthetic event/check probe; full Rust CI did not run"' in line:
                    try:
                        contexts.append(json.loads(line[line.index("{"):]))
                    except ValueError:
                        pass
            found[identity] = dict(run=run, jobs=jobs, log_exit=result.returncode, contexts=contexts,
                                   path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    save(ROOT / (label + "-run-mapping.json"), found)
    return found


def cleanup():
    for name in SPECS:
        case = state(name)
        if any(record.get("terminal") is None or record["terminal"].get("status") not in ("merged", "failed", "request-rejected") for record in case["native"]):
            raise RuntimeError("pending_native_outcome_blocks_cleanup:" + name)
        for layer in case["prs"]:
            fresh = pr(case, layer)
            if fresh["state"] == "open":
                require(api("cleanup-close-" + name + "-" + layer, "PATCH", "repos/" + REPO + "/pulls/" + str(case["prs"][layer]), {"state": "closed"}, case), [200])
                if pr(case, layer)["state"] != "closed":
                    raise RuntimeError("PR_close_readback_failed")
    policy_snapshot("before-cleanup")
    owned = read(ROOT / "policy-owned.json")
    for trunk in owned["protections"]:
        require(api("cleanup-protection-" + trunk, "DELETE", "repos/" + REPO + "/branches/" + trunk + "/protection"), [204])
        require(get("branches/" + trunk + "/protection", "cleanup-protection-absent"), [404])
    require(api("cleanup-ruleset", "DELETE", "repos/" + REPO + "/rulesets/" + str(owned["ruleset_id"])), [204])
    require(get("rulesets/" + str(owned["ruleset_id"]), "cleanup-ruleset-absent"), [404])
    save(ROOT / "cleanup.json", dict(time=now(), protections_removed=owned["protections"], ruleset_removed=owned["ruleset_id"], refs_retained=True))


def freeze_source():
    names = ["harness.py", "driver.py", "challenge.py", "minimal-ci.yml", "PLAN.md", "harness-outline.json", "branch-protection.proposed.json", "ruleset.proposed.json"]
    folder = ROOT / "source-snapshots" / str(time.time_ns())
    folder.mkdir(parents=True)
    hashes = {}
    for name in names:
        contents = (ROOT / name).read_bytes()
        (folder / name).write_bytes(contents)
        hashes[name] = hashlib.sha256(contents).hexdigest()
    grant = ROOT.parent / "control" / "target-grant-001.json"
    record = dict(path=str(folder.relative_to(ROOT)), hashes=hashes,
                  grant_sha256=hashlib.sha256(grant.read_bytes()).hexdigest(), time=now())
    save(folder / "manifest.json", record)
    save(ROOT / "source-active.json", record)
    return record


def verify_source():
    frozen = read(ROOT / "source-active.json")
    for name, expected in frozen["hashes"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError("source_changed_after_snapshot:" + name)
    if hashlib.sha256((ROOT.parent / "control" / "target-grant-001.json").read_bytes()).hexdigest() != frozen["grant_sha256"]:
        raise ValueError("grant_changed_after_snapshot")
