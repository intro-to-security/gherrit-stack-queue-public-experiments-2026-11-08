"""One scoped hosted B-success/C-conflict composition; never retry a write."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
WORKFLOW = ROOT.parent
CONTROL = WORKFLOW.parent / "control"
CASE = "gql-partial-001"
PREFIX = "exh-1109-workflow-gql-partial-001"
REPO = "joshlf/gherrit-native-stack-experiments-2026-11-08"
HELPERS = {"core.py": "a98242dabb752a89f8da47814ea62313d1d64871afe50042f930875445e4f453",
           "effects.py": "20d8a34e0d04e93080f70c5bc3499fe5835cb2d45feff4c5bb95a3fed6418cc9"}
for filename, expected in HELPERS.items():
    if hashlib.sha256((WORKFLOW / filename).read_bytes()).hexdigest() != expected:
        raise RuntimeError("Reviewed helper changed:" + filename)
sys.path.insert(0, str(WORKFLOW))
import core as c
import effects as e
if Path(c.__file__).resolve() != WORKFLOW / "core.py" or Path(e.__file__).resolve() != WORKFLOW / "effects.py":
    raise RuntimeError("Unexpected helper module identity")


def grant_check(path, grant):
    path = Path(path).resolve()
    wanted = {"prefix": PREFIX, "actions": ["partial-once"],
              "effects": ["push", "create-pr", "create-stack", "update-branch"]}
    if (path.parent != CONTROL.resolve() or grant.get("grant_path") != str(path)
            or grant.get("coordinator") != "root" or grant.get("repository") != REPO
            or grant.get("cases") != {CASE: wanted}
            or grant.get("harness_sha256") != HELPERS
            or grant.get("driver_sha256") != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()):
        raise ValueError("Exact new source/scope root grant required")


def ref(manifest, role):
    return "refs/heads/" + manifest["branches"][role]


def template():
    return {"case": CASE, "prefix": PREFIX, "repository": REPO,
            "branches": {role: PREFIX + "/" + role for role in ("trunk", "A", "B", "C", "author-source")},
            "archives": {key: "refs/tags/gherrit/" + PREFIX + "-" + role + "/v" + version
                         for key, role, version in (("A1", "A", "1"), ("B1", "B", "1"), ("C1", "C", "1"), ("A2", "A", "2"))},
            "planned_pr_bases": {"A": "trunk", "B": "A", "C": "B"},
            "prs": {}, "nodes": {}, "phase": "local-prepared"}


class PartialGuard(e.Guard):
    def __init__(self, manifest, grant=None, action=None):
        super().__init__(manifest, grant, action)
        expected = template()
        if any(manifest.get(key) != expected[key] for key in ("case", "prefix", "repository", "branches", "archives", "planned_pr_bases")):
            raise ValueError("Manifest escapes exact partial fixture")

    def authorize(self, kind):
        if self.grant is None:
            raise ValueError("New root grant required")
        grant_check(self.grant, json.loads(self.grant.read_text()))
        if kind not in {"push", "create-pr", "create-stack", "update-branch"}:
            raise ValueError("No merge, queue, settings or cleanup effect")
        return super().authorize(kind)

    def http(self, kind, method, path, payload):
        super().http(kind, method, path, payload)
        if kind == "update-branch":
            role = self.manifest.get("request_layer")
            value = payload["variables"]["input"]
            basis = self.manifest.get("request_basis", {})
            if (role not in ("B", "C") or value["pullRequestId"] != self.manifest["nodes"][role]
                    or value["expectedHeadOid"] != basis.get("selected")
                    or value["clientMutationId"] != PREFIX + "-" + role):
                raise ValueError("Request does not bind the exact current selected member")


class PartialEffects(e.Effects):
    def __init__(self, directory, git, manifest, grant):
        super().__init__(directory, git, manifest, grant, "partial-once")
        self.guard = PartialGuard(manifest, grant, "partial-once")

    def push(self, label, updates, expected):
        planned = self.manifest["initial_updates"] if label == "initial-push" else self.manifest["advance_updates"] if label == "advance-A" else None
        if planned is None:
            raise ValueError("Unknown push label")
        leases = {key: c.ZERO for key in planned} if label == "initial-push" else {
            ref(self.manifest, "A"): self.manifest["inputs"]["A0"], self.manifest["archives"]["A2"]: c.ZERO}
        if planned is None or updates != planned or expected != leases:
            raise ValueError("Only the two exact scoped push vectors are allowed")
        return super().push(label, updates, expected)


def prepare(directory):
    git = c.Git(directory)
    m = template()
    trunk = git.commit("trunk", None, {"a.txt": "0\n", "b.txt": "0\n", "c.txt": "0\n"}, "Seed isolated partial rebase fixture")
    a = git.commit("A0", trunk, {"a.txt": "1\n"}, "Change isolated A")
    b = git.commit("B0", a, {"b.txt": "1\n"}, "Change isolated B")
    top = git.commit("C0", b, {"c.txt": "2\n"}, "Change isolated C")
    advanced = git.commit("A1", a, {"c.txt": "1\n"}, "Advance A independently of B and against C")
    expected_b = git.commit("B-expected", advanced, {"b.txt": "1\n"}, "Expected B tree", message=git.message(b))
    try:
        git.merge("C-conflict-premise", b, expected_b, top)
    except c.Conflict:
        pass
    else:
        raise RuntimeError("Local C conflict premise absent")
    if git.patch(c.Range(a, b)) != git.patch(c.Range(advanced, expected_b)):
        raise RuntimeError("B own-patch preservation premise absent")
    m["inputs"] = {"trunk": trunk, "A0": a, "B0": b, "C0": top, "A1": advanced, "B-expected": expected_b}
    m["initial_updates"] = {ref(m, role): oid for role, oid in (("trunk", trunk), ("A", a), ("B", b), ("C", top), ("author-source", top))}
    m["initial_updates"].update({m["archives"][key]: oid for key, oid in (("A1", a), ("B1", b), ("C1", top))})
    m["advance_updates"] = {ref(m, "A"): advanced, m["archives"]["A2"]: advanced}
    m["authored_ranges"] = {"A1": {"base": trunk, "tip": a}, "B1": {"base": a, "tip": b}, "C1": {"base": b, "tip": top}, "A2": {"base": trunk, "tip": advanced}}
    c.save(directory / "case.json", m, exclusive=True)
    return git, m


def persist(directory, m):
    c.save(directory / "case.json", m)


def successful(receipt):
    if receipt["http"] != 200 and receipt["http"] != 201 or not isinstance(receipt["data"], dict) or receipt["data"].get("errors"):
        raise RuntimeError("Request rejected or acknowledgement shape unavailable")
    return receipt["data"]


def membership(m, observation):
    stack = observation["prs"]["A"]["graphql"]["data"]["repository"]["pullRequest"]["stack"]
    if not stack or stack["entries"]["pageInfo"]["hasNextPage"]:
        raise RuntimeError("Missing or incomplete native membership")
    entries = sorted(stack["entries"]["nodes"], key=lambda row: row["position"])
    members = [(row["pullRequest"]["number"], row["pullRequest"]["id"]) for row in entries]
    expected = [(m["prs"][role], m["nodes"][role]) for role in ("A", "B", "C")]
    if (stack["id"] != m["stack"]["node_id"] or stack["number"] != m["stack"]["number"]
            or stack["size"] != 3 or stack["baseRefName"] != m["branches"]["trunk"] or members != expected):
        raise RuntimeError("Native identity/order changed")
    for role, row in zip(("A", "B", "C"), entries):
        member = row["pullRequest"]
        if (member["headRefName"] != m["branches"][role]
                or member["headRefOid"] != observation["refs"].get(ref(m, role))
                or member["baseRefName"] != m["branches"][m["planned_pr_bases"][role]]):
            raise RuntimeError("Native member projection differs from exact branch vector")
    return {"id": stack["id"], "number": stack["number"], "members": members}


def validate_observation(m, observation, expected, *, base_current=False):
    for role in ("A", "B", "C"):
        pr = observation["prs"][role]["rest"]
        gql = observation["prs"][role]["graphql"]["data"]["repository"]["pullRequest"]
        base = m["planned_pr_bases"][role]
        if (pr["number"] != m["prs"][role] or pr["node_id"] != m["nodes"][role]
                or gql["id"] != m["nodes"][role] or gql["number"] != m["prs"][role]
                or pr["state"] != "open" or pr["merged"] or gql["state"] != "OPEN" or gql["merged"]
                or pr["head"]["ref"] != m["branches"][role] or gql["headRefName"] != m["branches"][role]
                or pr["base"]["ref"] != m["branches"][base] or gql["baseRefName"] != m["branches"][base]
                or pr["body"] != m["pr_bodies"][role]
                or pr["head"]["sha"] != expected[ref(m, role)] or gql["headRefOid"] != expected[ref(m, role)]):
            raise RuntimeError("Canonical selected-head/lifecycle/source projection mismatch:" + role)
        if base_current and (pr["base"]["sha"] != expected[ref(m, base)] or gql["baseRefOid"] != expected[ref(m, base)]):
            raise RuntimeError("Base projection has not acknowledged exact parent:" + role)
    if observation["refs"] != {ref(m, role): expected[ref(m, role)] for role in m["branches"]}:
        raise RuntimeError("Unexpected branch vector")
    return membership(m, observation)


def coherent(m, effects, label, expected, *, base_current=False):
    for sample in range(6):
        observation = effects.observe(label + "-" + str(sample))
        try:
            validate_observation(m, observation, expected, base_current=base_current)
            return observation
        except RuntimeError:
            if sample == 5:
                raise
            time.sleep(1)


def request(directory, m, effects, role, expected):
    basis = coherent(m, effects, role + "-basis", expected, base_current=True)
    if effects.remote_refs(role + "-basis-full-vector", list(expected)) != expected:
        raise RuntimeError("Full source/archive vector drift before mutation")
    parent = m["planned_pr_bases"][role]
    m["request_layer"] = role
    m["request_basis"] = {"selected": expected[ref(m, role)], "parent": expected[ref(m, parent)], "observation": basis}
    persist(directory, m)
    payload = {"query": e.UPDATE_QUERY, "variables": {"input": {
        "pullRequestId": m["nodes"][role], "expectedHeadOid": m["request_basis"]["selected"],
        "updateMethod": "REBASE", "clientMutationId": PREFIX + "-" + role}}}
    return effects.api("rebase-" + role + "-once", "POST", "graphql", payload, kind="update-branch")


def execute(grant):
    grant_check(grant, json.loads(Path(grant).read_text()))
    directory = ROOT / "fixture"
    if directory.exists():
        raise RuntimeError("Existing fixture is read-only; no reentry or retry")
    git, m = prepare(directory)
    effects = PartialEffects(directory, git, m, grant)
    try:
        snapshot = directory / "source-snapshot"
        snapshot.mkdir()
        for name, path in [("partial_once.py", Path(__file__)), *[(name, WORKFLOW / name) for name in HELPERS]]:
            c.save_text(snapshot / name, path.read_text())
        c.save(snapshot / "grant.json", json.loads(Path(grant).read_text()), exclusive=True)
        repo = successful(effects.api("repository", "GET", "repos/" + REPO))
        if repo["id"] != 1450723431 or repo["full_name"] != REPO or effects.namespace_inventory("initial-absence"):
            raise RuntimeError("Repository identity or namespace absence premise failed")
        effects.push("initial-push", m["initial_updates"], {key: c.ZERO for key in m["initial_updates"]})
        m["phase"] = "initial-refs-published"
        persist(directory, m)
        m["pr_bodies"] = {}
        for role in ("A", "B", "C"):
            body = "Isolated public sequential-rebase partial-failure fixture, layer " + role + ".\n\n" + e.NOTICE
            result = successful(effects.api("create-pr-" + role, "POST", "repos/" + REPO + "/pulls", {
                "title": PREFIX + " " + role, "body": body, "head": m["branches"][role],
                "base": m["branches"][m["planned_pr_bases"][role]], "draft": False}, kind="create-pr"))
            m["prs"][role], m["nodes"][role], m["pr_bodies"][role] = result["number"], result["node_id"], body
            persist(directory, m)
        m["stack"] = successful(effects.api("create-stack", "POST", "repos/" + REPO + "/stacks", {"pull_requests": list(m["prs"].values())}, kind="create-stack"))
        m["phase"] = "native-group-created"
        persist(directory, m)
        expected = dict(m["initial_updates"])
        coherent(m, effects, "initial", expected)
        effects.push("advance-A", m["advance_updates"], {ref(m, "A"): m["inputs"]["A0"], m["archives"]["A2"]: c.ZERO})
        m["phase"] = "A-advance-published"
        persist(directory, m)
        expected.update(m["advance_updates"])
        m["B_receipt"] = request(directory, m, effects, "B", expected)
        successful(m["B_receipt"])
        returned = m["B_receipt"]["data"].get("data", {}).get("updatePullRequestBranch")
        if (not isinstance(returned, dict) or returned.get("clientMutationId") != PREFIX + "-B"
                or returned.get("pullRequest", {}).get("id") != m["nodes"]["B"]
                or returned["pullRequest"].get("number") != m["prs"]["B"]):
            raise RuntimeError("B acknowledged payload identity unavailable; no C request")
        persist(directory, m)
        start = time.monotonic()
        for index, offset in enumerate((0, 2, 5, 10, 20, 30, 60)):
            time.sleep(max(0, offset - (time.monotonic() - start)))
            after = effects.observe("B-after-" + str(index))
            new_b = after["refs"].get(ref(m, "B"))
            if new_b and new_b != m["inputs"]["B0"]:
                candidate = dict(expected, **{ref(m, "B"): new_b})
                try:
                    validate_observation(m, after, candidate, base_current=True)
                except RuntimeError:
                    continue
                expected = candidate
                break
        else:
            raise RuntimeError("No usable coherent B result; no C request")
        effects.fetch("B-fetch", [ref(m, role) for role in ("A", "B", "C")])
        b_tip = expected[ref(m, "B")]
        if (git.git("show", "-s", "--format=%P", b_tip) != m["inputs"]["A1"]
                or git.tree(b_tip) != git.tree(m["inputs"]["B-expected"])
                or git.patch(c.Range(m["inputs"]["A1"], b_tip)) != git.patch(c.Range(m["inputs"]["A0"], m["inputs"]["B0"]))):
            raise RuntimeError("B parent/tree/own-patch oracle failed; no C request")
        m["B_checkpoint"] = {"head": b_tip, "parent": m["inputs"]["A1"], "patch": git.patch(c.Range(m["inputs"]["A1"], b_tip)), "source": m["inputs"]["C0"], "authored_ranges": m["authored_ranges"]}
        git.git("update-ref", "refs/retained/B-complete", b_tip, c.ZERO)
        m["phase"] = "B-usable-C-not-requested"
        persist(directory, m)
        m["C_receipt"] = request(directory, m, effects, "C", expected)
        persist(directory, m)
        errors = m["C_receipt"].get("data", {}).get("errors", [])
        conflict = m["C_receipt"]["http"] == 200 and any(error.get("type") == "UNPROCESSABLE" and "conflict" in error.get("message", "").lower() for error in errors)
        m["final_observations"] = []
        for index, delay in enumerate((0, 2, 5)):
            time.sleep(delay)
            observed = coherent(m, effects, "C-after-" + str(index), expected, base_current=True)
            m["final_observations"].append(observed)
        final_refs = effects.remote_refs("final-full-vector", list(expected))
        if final_refs != expected or not conflict:
            raise RuntimeError("C conflict-rejection or unchanged full-vector premise failed")
        m.update(phase="known-partial-B-complete-C-conflict", final_refs=final_refs,
                 limits="Two separately guarded requests; known completed B prefix and rejected C only. No transaction, rollback, cancellation, quiescence or future-write fence.")
        c.save(directory / "RESULTS.json", m, exclusive=True)
        persist(directory, m)
    except Exception as error:
        if not (directory / "FREEZE.json").exists():
            effects.freeze("driver-stop", str(error))
        m.update(phase="frozen-no-retry", stop_reason=str(error))
        persist(directory, m)
        c.save(directory / "STOP.json", {"at": c.now(), "error": str(error), "policy": "Read-only reconciliation; no repaired or repeated write"}, exclusive=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grant", type=Path, required=True)
    execute(parser.parse_args().grant)
