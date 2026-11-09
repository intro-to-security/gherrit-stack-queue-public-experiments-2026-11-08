"""Separately granted B/C requests after a known-not-sent frozen precondition."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

import partial_once as d

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT / "fixture"
DIRECTORY = ROOT / "continuation-001"
DRIVER_SHA256 = "ac332861f99eac829c8bd8419ad765f07ddf29e5cbcd254a5e065de3acfdd7a6"
ACTION = "partial-continuation-001"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def original_bindings():
    return {"case_sha256": sha(ORIGINAL / "case.json"),
            "freeze_sha256": sha(ORIGINAL / "FREEZE.json"),
            "audit_sha256": sha(ORIGINAL / "MUTATION-AUDIT.json"),
            "driver_sha256": sha(ORIGINAL / "source-snapshot/partial_once.py")}


def audit_original(directory=ORIGINAL):
    manifest = json.loads((directory / "case.json").read_text())
    d.PartialGuard(manifest)
    if manifest["phase"] != "frozen-no-retry" or not (directory / "FREEZE.json").is_file():
        raise ValueError("Original frozen scope unavailable")
    expected = {"initial-push", "advance-A", "create-pr-A", "create-pr-B", "create-pr-C", "create-stack"}
    writes = []
    for path in (directory / "evidence").glob("*.intent.json"):
        intent = json.loads(path.read_text())
        if intent["kind"] in ("read", "git-read"):
            continue
        label = path.name.removesuffix(".intent.json")
        receipt_path = path.with_name(label + ".receipt.json")
        if intent["kind"] == "update-branch" or label not in expected or not receipt_path.exists():
            raise ValueError("Original update intent or unresolved/unplanned write exists")
        receipt = json.loads(receipt_path.read_text())
        if any(receipt.get(key) != value for key, value in intent.items()):
            raise ValueError("Original intent/receipt identity differs")
        if receipt.get("exit") != 0 or (intent["kind"] != "push" and receipt.get("http") != 201):
            raise ValueError("Original write is not a known acknowledged creation/push")
        writes.append(label)
    audit = json.loads((directory / "MUTATION-AUDIT.json").read_text())
    if (set(writes) != expected or len(writes) != 6 or audit["B_update_dispatched"]
            or audit["C_update_dispatched"] or audit["missing_receipts"]
            or audit["unknown_mutating_acknowledgements"]):
        raise ValueError("Original known-not-sent proof absent")
    return manifest


def grant_check(path, grant):
    path = Path(path).resolve()
    cases = {d.CASE: {"prefix": d.PREFIX, "actions": [ACTION], "effects": ["update-branch"]}}
    if (path.parent != d.CONTROL.resolve() or grant.get("grant_path") != str(path)
            or grant.get("coordinator") != "root" or grant.get("repository") != d.REPO
            or grant.get("cases") != cases or grant.get("harness_sha256") != d.HELPERS
            or grant.get("continuation_sha256") != sha(__file__)
            or grant.get("original_bindings") != original_bindings()
            or sha(d.__file__) != DRIVER_SHA256
            or grant["original_bindings"]["driver_sha256"] != DRIVER_SHA256):
        raise ValueError("Exact new continuation grant/source/original bindings required")
    audit_original()


class ContinuationGuard(d.e.Guard):
    def authorize(self, kind):
        if kind != "update-branch" or self.grant is None:
            raise ValueError("Only separately granted B/C update-branch is permitted")
        grant_check(self.grant, json.loads(self.grant.read_text()))
        return super().authorize(kind)

    def http(self, kind, method, path, payload):
        if kind != "update-branch":
            raise ValueError("No creation, push, merge, settings or cleanup effect")
        super().http(kind, method, path, payload)
        role = self.manifest.get("request_layer")
        value = payload["variables"]["input"]
        if (role not in ("B", "C") or value["pullRequestId"] != self.manifest["nodes"][role]
                or value["expectedHeadOid"] != self.manifest["request_basis"]["selected"]
                or value["clientMutationId"] != d.PREFIX + "-continuation-001-" + role):
            raise ValueError("Foreign or stale selected member")


def validate_basis(manifest, observation, full_refs, expected):
    d.validate_observation(manifest, observation, expected, base_current=False)
    if full_refs != expected:
        raise ValueError("Exact current named-parent/source/archive vector required")
    return {role: {"REST_base_oid": observation["prs"][role]["rest"]["base"]["sha"],
                   "GraphQL_base_oid": observation["prs"][role]["graphql"]["data"]["repository"]["pullRequest"]["baseRefOid"],
                   "actual_named_parent_oid": expected[d.ref(manifest, manifest["planned_pr_bases"][role])]}
            for role in ("A", "B", "C")}


def request(manifest, effects, role, expected):
    observation = d.coherent(manifest, effects, role + "-basis", expected, base_current=False)
    full = effects.remote_refs(role + "-basis-full-vector", list(expected))
    diagnostics = validate_basis(manifest, observation, full, expected)
    manifest.update(request_layer=role, request_basis={"selected": expected[d.ref(manifest, role)],
                    "actual_parent": diagnostics[role]["actual_named_parent_oid"],
                    "base_oid_observations": diagnostics, "observation": observation})
    d.c.save(DIRECTORY / "state.json", manifest)
    payload = {"query": d.e.UPDATE_QUERY, "variables": {"input": {
        "pullRequestId": manifest["nodes"][role], "expectedHeadOid": manifest["request_basis"]["selected"],
        "updateMethod": "REBASE", "clientMutationId": d.PREFIX + "-continuation-001-" + role}}}
    return effects.api("rebase-" + role + "-once", "POST", "graphql", payload, kind="update-branch")


def copied_git():
    source = ORIGINAL / "git"
    if any(path.is_symlink() for path in source.rglob("*")):
        raise RuntimeError("Unexpected symlink in owned original Git store")
    shutil.copytree(source, DIRECTORY / "git")
    hooks = DIRECTORY / "empty-hooks"
    hooks.mkdir()
    command = ["git", "-c", "core.hooksPath=" + str(hooks), "--git-dir=" + str(DIRECTORY / "git"), "config", "core.hooksPath", str(hooks)]
    result = subprocess.run(command, capture_output=True, text=True, env=d.c.ENV)
    d.c.save(DIRECTORY / "local-copy.json", {"source": str(source), "command": command,
             "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}, exclusive=True)
    result.check_returncode()
    return d.c.Git(DIRECTORY)


def execute(grant):
    grant_check(grant, json.loads(Path(grant).read_text()))
    if DIRECTORY.exists():
        raise RuntimeError("Continuation already exists; no reentry or retry")
    original = audit_original()
    before = original_bindings()
    DIRECTORY.mkdir()
    d.c.save(DIRECTORY / "prior-proof.json", {"bindings": before, "six_writes_acknowledged": True,
              "B_C_original_intents": 0, "scope": "New authority for known-not-sent requests; original freeze unchanged"}, exclusive=True)
    git = copied_git()
    manifest = json.loads(json.dumps(original))
    manifest.update(phase="continuation-checking-current-vector", original_frozen_phase=original["phase"])
    manifest["original_stop_reason"] = manifest.pop("stop_reason")
    effects = d.e.Effects(DIRECTORY, git, manifest, grant, ACTION)
    effects.guard = ContinuationGuard(manifest, grant, ACTION)
    try:
        snapshot = DIRECTORY / "source-snapshot"
        snapshot.mkdir()
        for name, path in [("partial_continue.py", Path(__file__)), ("partial_once.py", Path(d.__file__)), *[(name, d.WORKFLOW / name) for name in d.HELPERS]]:
            d.c.save_text(snapshot / name, path.read_text())
        d.c.save(snapshot / "grant.json", json.loads(Path(grant).read_text()), exclusive=True)
        expected = dict(manifest["initial_updates"])
        expected.update(manifest["advance_updates"])
        manifest["B_receipt"] = request(manifest, effects, "B", expected)
        d.successful(manifest["B_receipt"])
        returned = manifest["B_receipt"]["data"].get("data", {}).get("updatePullRequestBranch")
        if (not isinstance(returned, dict) or returned.get("clientMutationId") != d.PREFIX + "-continuation-001-B"
                or returned.get("pullRequest", {}).get("id") != manifest["nodes"]["B"]
                or returned["pullRequest"].get("number") != manifest["prs"]["B"]):
            raise RuntimeError("B response identity unavailable; no C request")
        d.c.save(DIRECTORY / "state.json", manifest)
        start = time.monotonic()
        for index, offset in enumerate((0, 2, 5, 10, 20, 30, 60)):
            time.sleep(max(0, offset - (time.monotonic() - start)))
            observed = effects.observe("B-after-" + str(index))
            new_b = observed["refs"].get(d.ref(manifest, "B"))
            if new_b and new_b != manifest["inputs"]["B0"]:
                candidate = dict(expected, **{d.ref(manifest, "B"): new_b})
                try:
                    d.validate_observation(manifest, observed, candidate, base_current=False)
                except RuntimeError:
                    continue
                expected = candidate
                break
        else:
            raise RuntimeError("No coherent B result; no C request")
        effects.fetch("B-fetch", [d.ref(manifest, role) for role in ("A", "B", "C")])
        b_tip = expected[d.ref(manifest, "B")]
        if (git.git("show", "-s", "--format=%P", b_tip) != manifest["inputs"]["A1"]
                or git.tree(b_tip) != git.tree(manifest["inputs"]["B-expected"])
                or git.patch(d.c.Range(manifest["inputs"]["A1"], b_tip)) != git.patch(d.c.Range(manifest["inputs"]["A0"], manifest["inputs"]["B0"]))):
            raise RuntimeError("B actual parent/tree/patch fails; no C request")
        git.git("update-ref", "refs/retained/B-continuation-001", b_tip, d.c.ZERO)
        manifest.update(phase="B-usable-C-not-requested", B_checkpoint={"head": b_tip,
                        "actual_parent": manifest["inputs"]["A1"], "patch": git.patch(d.c.Range(manifest["inputs"]["A1"], b_tip)),
                        "source": manifest["inputs"]["C0"], "authored_ranges": manifest["authored_ranges"]})
        d.c.save(DIRECTORY / "state.json", manifest)
        manifest["C_receipt"] = request(manifest, effects, "C", expected)
        d.c.save(DIRECTORY / "state.json", manifest)
        body = manifest["C_receipt"].get("data")
        errors = body.get("errors", []) if isinstance(body, dict) else []
        conflict = manifest["C_receipt"]["http"] == 200 and any(error.get("type") == "UNPROCESSABLE" and "conflict" in error.get("message", "").lower() for error in errors)
        manifest["final_observations"] = []
        for index, delay in enumerate((0, 2, 5)):
            time.sleep(delay)
            observation = d.coherent(manifest, effects, "C-after-" + str(index), expected, base_current=False)
            manifest["final_observations"].append(observation)
        final = effects.remote_refs("final-full-vector", list(expected))
        if final != expected or not conflict or original_bindings() != before:
            raise RuntimeError("Known conflict/full vector/original freeze preservation fails")
        manifest.update(phase="known-partial-B-complete-C-conflict", final_refs=final,
                        original_bindings_after=original_bindings(), limits="Two separately guarded requests; no transaction, rollback, cancellation or future-write fence")
        d.c.save(DIRECTORY / "RESULTS.json", manifest, exclusive=True)
        d.c.save(DIRECTORY / "state.json", manifest)
    except Exception as error:
        if not (DIRECTORY / "FREEZE.json").exists():
            effects.freeze("continuation-stop", str(error))
        manifest.update(phase="frozen-no-retry", stop_reason=str(error))
        d.c.save(DIRECTORY / "state.json", manifest)
        d.c.save(DIRECTORY / "STOP.json", {"at": d.c.now(), "error": str(error), "policy": "No repaired/repeated write; original freeze remains"}, exclusive=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grant", required=True, type=Path)
    execute(parser.parse_args().grant)
