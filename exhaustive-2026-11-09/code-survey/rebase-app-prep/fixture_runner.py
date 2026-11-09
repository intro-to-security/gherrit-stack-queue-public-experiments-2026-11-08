import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parents[1]
CONTROL = CAMPAIGN / "control"
HELPER = CONTROL / "rootlab.py"
RUN = ROOT / "run-001"
REPO = "joshlf/gherrit-native-stack-experiments-2026-11-08"
REPO_ID = 1450723431
PREFIX = "exh-1109-causal-rb-app-001"
REFS = {name: PREFIX + "/" + name for name in ["trunk", "A", "B", "runner"]}
ROOTLAB_SHA256 = "ae1ae63d5ee8370cbca11711f5d5e76a97669881ddf8ef8911493666393d128d"
PERMISSIONS = {"contents": "write", "pull-requests": "write"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sources():
    files = {name: ROOT / name for name in ["fixture_runner.py", "probe.py", "fixture.template.json", "workflow.template.yml"]}
    files["control/rootlab.py"] = HELPER
    return {name: digest(path.read_bytes()) for name, path in files.items()}


def load_helper():
    require(digest(HELPER.read_bytes()) == ROOTLAB_SHA256, "Reviewed rootlab helper changed")
    spec = importlib.util.spec_from_file_location("rebase_app_rootlab", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class ScopedLab(module.Lab):
        def refname(self, branch):
            require(branch in REFS.values(), "Ref is outside the exact four-ref allocation")
            return "refs/heads/" + branch
    return module, ScopedLab


def owned_lab(Lab):
    lab = Lab(RUN, PREFIX, REPO)
    require(lab.git("config", "--get", "core.hooksPath") == "/dev/null", "Owned hooks configuration changed")
    require(lab.git("remote", "get-url", "origin") == "https://github.com/" + REPO + ".git", "Owned remote changed")
    require(lab.git("remote", "get-url", "--push", "origin") == "https://github.com/" + REPO + ".git", "Owned push remote changed")
    return lab


def grant_check(path, phase, frozen, effects):
    require(path is not None and path.resolve().parent == CONTROL.resolve(), "Exact root control grant path required")
    grant = json.loads(path.read_bytes())
    expected = {
        "coordinator": "root", "grant_path": str(path.resolve()), "phase": phase,
        "repository": REPO, "repository_id": REPO_ID, "prefix": PREFIX,
        "run_directory": str(RUN.resolve()), "sources": sources(),
        "frozen_record_sha256": digest(frozen.read_bytes()), "effects": effects,
    }
    require(all(grant.get(key) == value for key, value in expected.items()), "Root grant does not bind exact source, frozen record and effects")
    return grant


def read_refs(lab, label):
    result = lab.command(label, ["git", "-c", "core.hooksPath=/dev/null", "--git-dir", str(lab.bare), "ls-remote", "--heads", "origin", "refs/heads/" + PREFIX + "/*"])
    refs = {}
    for line in result["stdout"].splitlines():
        oid, ref = line.split()
        require(re.fullmatch(r"[0-9a-f]{40}", oid) and ref in {"refs/heads/" + value for value in REFS.values()}, "Unexpected ref in the allocation")
        refs[ref] = oid
    return refs


def expected_refs(prepared):
    return {"refs/heads/" + REFS[name]: prepared["commits"]["advanced" if name == "trunk" else name] for name in ["trunk", "A", "B"]}


def pr_body(letter):
    return {"head": REFS[letter], "base": REFS["trunk" if letter == "A" else "A"], "title": "Actions installation-token capability: synthetic " + letter, "body": "Authorized isolated two-member capability fixture.\n\n*Authored by an AI agent acting on joshlf's behalf.*"}


def prepare():
    require(not RUN.exists(), "This local allocation already exists; do not recreate it")
    helper, Lab = load_helper()
    RUN.mkdir(mode=0o700)
    lab = owned_lab(Lab)
    root_files = {"root.txt": "Isolated synthetic Actions installation-token capability.\n"}
    commits = {"trunk": lab.commit(root_files, None, "Record the isolated App-token synthetic trunk")}
    a_files = {**root_files, "a.txt": "A=1\n"}
    commits["A"] = lab.commit(a_files, commits["trunk"], "Record synthetic App-token member A")
    b_files = {**a_files, "b.txt": "B=1\n"}
    commits["B"] = lab.commit(b_files, commits["A"], "Record synthetic App-token member B")
    advance_files = {**root_files, "trunk.txt": "Independent nonconflicting trunk advance.\n"}
    commits["advanced"] = lab.commit(advance_files, commits["trunk"], "Advance only the App-token synthetic trunk")
    for name, oid in commits.items():
        lab.git("update-ref", "refs/retained/" + name, oid)
    initial = {REFS[name]: {"expected": None, "target": commits[name]} for name in ["trunk", "A", "B"]}
    effects = [
        {"kind": "atomic_create_only_push", "updates": initial},
        {"kind": "POST", "path": "/repos/" + REPO + "/pulls", "body": pr_body("A")},
        {"kind": "POST", "path": "/repos/" + REPO + "/pulls", "body": pr_body("B")},
        {"kind": "POST", "path": "/repos/" + REPO + "/stacks", "body_from_acknowledged_own_PRs": ["A.number", "B.number"]},
        {"kind": "exact_lease_push", "ref": REFS["trunk"], "expected": commits["trunk"], "target": commits["advanced"]},
    ]
    helper.preserve(RUN / "PREPARED.json", {"phase": "local_only_no_hosted_effect", "repository": REPO, "repository_id": REPO_ID, "prefix": PREFIX, "sources": sources(), "commits": commits, "files": {"trunk": root_files, "A": a_files, "B": b_files, "advanced": advance_files}, "trees": {name: lab.git("rev-parse", oid + "^{tree}") for name, oid in commits.items()}, "effects": effects})
    print(json.dumps({"prepared_record": str(RUN / "PREPARED.json"), "next": "Root reviews exact local objects and grants only create-fixture; no hosted effect occurred"}))


def live_pr_check(pr, letter, prepared, number=None, node_id=None):
    require(isinstance(pr.get("number"), int) and pr["number"] > 653 and isinstance(pr.get("node_id"), str) and pr["node_id"] and pr.get("state") == "open", "PR identity/lifecycle mismatch")
    require(number is None or pr["number"] == number, "Canonical PR number changed")
    require(node_id is None or pr["node_id"] == node_id, "Canonical PR node changed")
    require(pr.get("head", {}).get("repo", {}).get("id") == REPO_ID and pr.get("base", {}).get("repo", {}).get("id") == REPO_ID, "Foreign PR repository")
    require(pr["head"].get("ref") == REFS[letter] and pr["head"].get("sha") == prepared["commits"][letter] and pr["base"].get("ref") == REFS["trunk" if letter == "A" else "A"], "PR head/base vector mismatch")


def save_bytes(path, data):
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def runner_commit(lab, files, trailer):
    blobs = {name: lab.git("hash-object", "-w", "--stdin", data=value.decode()) for name, value in files.items()}
    workflows = lab.git("mktree", data="100644 blob " + blobs["workflow.yml"] + "\trb-app-probe.yml\n")
    github = lab.git("mktree", data="040000 tree " + workflows + "\tworkflows\n")
    tree = lab.git("mktree", data="040000 tree " + github + "\t.github\n100644 blob " + blobs["fixture.json"] + "\tfixture.json\n100644 blob " + blobs["probe.py"] + "\tprobe.py\n")
    oid = lab.git("commit-tree", tree, data="Probe one isolated native rebase with the Actions installation token\n\n" + trailer + "\n")
    return oid, tree


def create_fixture(grant_path):
    frozen = RUN / "PREPARED.json"
    prepared = json.loads(frozen.read_bytes())
    require(prepared["sources"] == sources(), "Prepared sources changed")
    grant = grant_check(grant_path, "create-fixture", frozen, prepared["effects"])
    helper, Lab = load_helper()
    helper.preserve(RUN / "CREATE-START.json", {"at": helper.stamp(), "grant": str(grant_path.resolve()), "grant_sha256": digest(grant_path.read_bytes())})
    lab = owned_lab(Lab)
    repository = json.loads(lab.command("create-repository", ["gh", "api", "--method", "GET", "repos/" + REPO])["stdout"])
    require(repository.get("id") == REPO_ID and repository.get("full_name") == REPO, "Live repository identity mismatch")
    require(read_refs(lab, "create-absence") == {}, "New allocation has an occupied ref")
    lab.push("create-initial", {REFS[name]: (None, prepared["commits"][name]) for name in ["trunk", "A", "B"]})
    require(read_refs(lab, "create-initial-readback") == {"refs/heads/" + REFS[name]: prepared["commits"][name] for name in ["trunk", "A", "B"]}, "Initial exact refs did not read back")
    prs = {}
    for letter in ["A", "B"]:
        pr = lab.api("create-pr-" + letter, "/pulls", "POST", pr_body(letter))
        live_pr_check(pr, letter, prepared)
        require(pr["number"] not in [value["number"] for value in prs.values()], "Duplicate canonical PR")
        prs[letter] = {"number": pr["number"], "node_id": pr["node_id"]}
        helper.preserve(RUN / ("CREATED-" + letter + ".json"), prs[letter])
    stack = lab.api("create-stack", "/stacks", "POST", {"pull_requests": [prs[letter]["number"] for letter in ["A", "B"]]})
    require(isinstance(stack.get("number"), int) and stack["number"] > 653 and stack.get("node_id") and stack.get("base", {}).get("ref") == REFS["trunk"], "Created group identity mismatch")
    require([item["number"] for item in stack.get("pull_requests", [])] == [prs[letter]["number"] for letter in ["A", "B"]], "Created group membership mismatch")
    helper.preserve(RUN / "CREATED-STACK.json", {"number": stack["number"], "node_id": stack["node_id"], "prs": prs})
    lab.push("create-advance-trunk", {REFS["trunk"]: (prepared["commits"]["trunk"], prepared["commits"]["advanced"])})
    require(read_refs(lab, "create-final-refs") == expected_refs(prepared), "Final fixture ref vector mismatch")
    config = json.loads((ROOT / "fixture.template.json").read_bytes())
    config.update(root_reviewed=True, probe_sha256=digest((ROOT / "probe.py").read_bytes()), stack_number=stack["number"], stack_node_id=stack["node_id"], trunk={"ref": REFS["trunk"], "sha": prepared["commits"]["advanced"]})
    config["members"] = [{"number": prs[letter]["number"], "node_id": prs[letter]["node_id"], "head_ref": REFS[letter], "head_oid": prepared["commits"][letter], "base_ref": REFS["trunk" if letter == "A" else "A"]} for letter in ["A", "B"]]
    config_bytes = (json.dumps(config, indent=2, sort_keys=True) + "\n").encode()
    workflow = (ROOT / "workflow.template.yml").read_bytes()
    require(workflow.count(b"ROOT_MUST_FILL_EXACT_CONFIG_SHA256") == 1, "Workflow config binding placeholder changed")
    files = {"fixture.json": config_bytes, "probe.py": (ROOT / "probe.py").read_bytes(), "workflow.yml": workflow.replace(b"ROOT_MUST_FILL_EXACT_CONFIG_SHA256", digest(config_bytes).encode())}
    directory = RUN / "runner-source"
    directory.mkdir()
    for name, data in files.items():
        save_bytes(directory / name, data)
    commit, tree = runner_commit(lab, files, helper.TRAILER)
    lab.git("update-ref", "refs/retained/runner", commit)
    route = "/repositories/" + str(REPO_ID) + "/stacks/" + str(stack["number"]) + "/rebase"
    payload = {"expected_head_oid_by_pr_number": {str(prs[letter]["number"]): prepared["commits"][letter] for letter in ["A", "B"]}}
    effects = [{"kind": "create_only_runner_push_and_one_workflow", "ref": REFS["runner"], "expected": None, "target": commit, "request_path": route, "payload": payload, "requested_permissions": PERMISSIONS}]
    helper.preserve(RUN / "RUNNER-READY.json", {"phase": "fixture_created_runner_not_pushed", "sources": sources(), "prepared_sha256": digest(frozen.read_bytes()), "fixture_grant_sha256": digest(grant_path.read_bytes()), "stack": {"number": stack["number"], "node_id": stack["node_id"]}, "prs": prs, "commit": commit, "tree": tree, "runner_files": {name: digest(data) for name, data in files.items()}, "effects": effects})
    print(json.dumps({"ready_record": str(RUN / "RUNNER-READY.json"), "next": "Root reviews the filled sources, exact numeric path/map and runner commit; a separate launch grant is required"}))


def launch(grant_path):
    frozen = RUN / "RUNNER-READY.json"
    ready = json.loads(frozen.read_bytes())
    prepared = json.loads((RUN / "PREPARED.json").read_bytes())
    require(ready["sources"] == sources() and ready["prepared_sha256"] == digest((RUN / "PREPARED.json").read_bytes()), "Frozen source/prepared record changed")
    grant_check(grant_path, "launch", frozen, ready["effects"])
    helper, Lab = load_helper()
    helper.preserve(RUN / "LAUNCH-START.json", {"at": helper.stamp(), "grant": str(grant_path.resolve()), "grant_sha256": digest(grant_path.read_bytes())})
    lab = owned_lab(Lab)
    require(lab.git("rev-parse", ready["commit"] + "^{tree}") == ready["tree"], "Runner commit tree mismatch")
    for name, tree_path in {"probe.py": "probe.py", "fixture.json": "fixture.json", "workflow.yml": ".github/workflows/rb-app-probe.yml"}.items():
        data = (RUN / "runner-source" / name).read_bytes()
        readback = lab.command("launch-source-" + name.replace(".", "-"), ["git", "-c", "core.hooksPath=/dev/null", "--git-dir", str(lab.bare), "show", ready["commit"] + ":" + tree_path])["stdout"].encode()
        require(digest(data) == ready["runner_files"][name] and digest(readback) == digest(data), "Exact committed runner source differs")
    require(read_refs(lab, "launch-ref-premise") == expected_refs(prepared), "Runner occupied or original fixture vector changed")
    stack = lab.api("launch-stack-premise", "/stacks/" + str(ready["stack"]["number"]))
    require(stack.get("node_id") == ready["stack"]["node_id"] and [item["number"] for item in stack.get("pull_requests", [])] == [ready["prs"][letter]["number"] for letter in ["A", "B"]], "Canonical group changed")
    for letter in ["A", "B"]:
        live_pr_check(lab.api("launch-pr-" + letter, "/pulls/" + str(ready["prs"][letter]["number"])), letter, prepared, **ready["prs"][letter])
    lab.push("launch-runner", {REFS["runner"]: (None, ready["commit"])})
    refs = read_refs(lab, "launch-runner-readback")
    require(refs.get("refs/heads/" + REFS["runner"]) == ready["commit"], "Runner push readback absent; outcome may still be live")
    helper.preserve(RUN / "LAUNCHED.json", {"at": helper.stamp(), "runner_commit": ready["commit"], "runner_ref": REFS["runner"], "refs": refs, "workflow_execution": "Triggered or pending; retain exact run/permissions/artifact and reconcile read-only; never rerun/recreate"})
    print(json.dumps({"launched": ready["commit"], "next": "Read-only workflow/artifact/native outcome reconciliation; no retry"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="One exact synthetic fixture and one separately granted runner launch; no retries")
    parser.add_argument("phase", choices=["prepare", "create-fixture", "launch"])
    parser.add_argument("--grant", type=Path)
    args = parser.parse_args()
    try:
        if args.phase == "prepare":
            require(args.grant is None, "Local prepare needs no dispatch grant")
            prepare()
        elif args.phase == "create-fixture":
            create_fixture(args.grant)
        else:
            launch(args.grant)
    except Exception as error:
        print(json.dumps({"stopped": type(error).__name__, "reason": str(error), "policy": "Freeze retained intents/receipts; do not rerun a phase or recreate its namespace"}), file=sys.stderr)
        sys.exit(1)
