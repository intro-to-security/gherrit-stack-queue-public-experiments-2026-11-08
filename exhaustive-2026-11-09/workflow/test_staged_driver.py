import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from core import Git, TRAILER, save
import run
import native_repeat
import cascade_followup


class LocalProvider:
    """Simulate only hosted effects while the driver uses real Git objects.

    This provider has immediate native settlement by construction. Passing
    these tests cannot establish any ordering property of GitHub's writer.
    """

    def __init__(self, manifest, git):
        self.manifest = manifest
        self.git = git
        self.refs = {}
        self.prs = {}
        self.next_pr = 1
        self.actions = []
        self.guard = SimpleNamespace(authorize=lambda kind: None)
        self.stack_members = []

    def namespace_inventory(self, label):
        return dict(self.refs)

    def remote_refs(self, label, refs):
        return {ref: self.refs[ref] for ref in refs if ref in self.refs}

    def push(self, label, updates, expected):
        for ref, oid in expected.items():
            actual = self.refs.get(ref, "0" * 40)
            if actual != oid:
                raise AssertionError("Lease mismatch in local provider")
        self.refs.update(updates)
        self.actions.append({"kind": "push", "label": label,
                             "updates": dict(updates), "expected": dict(expected)})
        return {"exit": 0}

    def fetch(self, label, refs):
        return {"exit": 0}

    def rest_pr(self, number):
        stored = self.prs[number]
        head = self.refs["refs/heads/" + stored["head"]]
        base = self.refs["refs/heads/" + stored["base"]]
        return {"number": number, "node_id": "NODE_" + str(number),
                "state": "closed" if stored["merged"] else "open",
                "merged": stored["merged"], "body": stored["body"],
                "head": {"sha": head, "ref": stored["head"],
                         "repo": {"full_name": run.REPO}},
                "base": {"sha": base, "ref": stored["base"]}}

    def api(self, label, method, path, payload=None, *, kind=None):
        self.actions.append({"kind": kind or "read", "label": label,
                             "method": method, "path": path, "payload": payload})
        if kind == "create-pr":
            number = self.next_pr
            self.next_pr += 1
            self.prs[number] = {**payload, "merged": False}
            return {"http": 201, "data": self.rest_pr(number)}
        if kind == "create-stack":
            self.stack_members = list(payload["pull_requests"])
            return {"http": 201, "data": {"id": 1000, "number": 1000}}
        if kind == "update-branch":
            number = int(payload["variables"]["input"]["pullRequestId"].removeprefix("NODE_"))
            selected = self.prs[number]
            head_ref = "refs/heads/" + selected["head"]
            old = self.refs[head_ref]
            parent = self.git.git("rev-parse", old + "^")
            base = self.refs["refs/heads/" + selected["base"]]
            self.refs[head_ref] = self.git.merge(label + "-native", parent, base, old)
            return {"http": 200, "data": {"data": {"updatePullRequestBranch": {"pullRequest": {"headRefOid": old}}}}}
        if kind == "merge":
            number = int(path.split("/")[-2])
            selected = self.prs[number]
            trunk_ref = "refs/heads/" + self.manifest["branches"]["trunk"]
            before = self.refs[trunk_ref]
            head = self.refs["refs/heads/" + selected["head"]]
            if head != payload["sha"]:
                raise AssertionError("Selected-head mismatch in local provider")
            merged = self.git.commit_tree(label + "-native-trunk", before,
                                           self.git.tree(head),
                                           "Land the isolated layer\n\n" + TRAILER + "\n")
            self.refs[trunk_ref] = merged
            selected["merged"] = True
            if selected["head"] == self.manifest["branches"]["A"]:
                b_number = self.manifest["prs"]["B"]
                b = self.prs[b_number]
                b_ref = "refs/heads/" + b["head"]
                self.refs[b_ref] = self.git.commit_tree(label + "-native-B", merged,
                                                       self.git.tree(self.refs[b_ref]),
                                                       self.git.message(self.refs[b_ref]))
                b["base"] = self.manifest["branches"]["trunk"]
            return {"http": 200, "data": {"status": "merged", "details": {"sha": merged}}}
        if method == "GET" and "/pulls/" in path:
            return {"http": 200, "data": self.rest_pr(int(path.split("/")[-1]))}
        raise AssertionError("Unexpected local-provider request")

    def observe(self, label):
        prs = {}
        for layer, number in self.manifest["prs"].items():
            stack = None
            if number in self.stack_members:
                stack = {"id": "STACK_NODE", "number": 1000, "size": len(self.stack_members),
                         "baseRefName": self.manifest["branches"]["trunk"],
                         "entries": {"pageInfo": {"hasNextPage": False},
                                     "nodes": [{"position": i + 1, "pullRequest": {"id": "NODE_" + str(n), "number": n}}
                                               for i, n in enumerate(self.stack_members)]}}
            prs[layer] = {"rest": self.rest_pr(number),
                          "graphql": {"data": {"repository": {"pullRequest": {"stack": stack}}}}}
        return {"prs": prs, "refs": dict(self.refs)}

    def freeze(self, label, reason):
        save(self.git.root / "FREEZE.json", {"attempt": label, "reason": reason}, exclusive=True)


class FullDriverTests(unittest.TestCase):
    def exercise(self, name, *, native=False):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            providers = {}

            def local_context(case, grant=None, action=None):
                directory = root / "cases" / case
                manifest = json.loads((directory / "case.json").read_text())
                git = Git(directory)
                provider = providers.setdefault(case, LocalProvider(manifest, git))
                provider.manifest = manifest
                provider.git = git
                return directory, manifest, git, provider

            with mock.patch.object(run, "ROOT", root), mock.patch.object(run, "context", local_context), mock.patch.object(native_repeat, "context", local_context):
                prepared = run.prepare(name)
                _, manifest, git, provider = local_context(name)
                self.assertEqual(git.git("rev-parse", "refs/heads/authoring"), prepared["inputs"]["B0"])
                run.setup(name, "local-provider-only")
                run.stage_f(name, "local-provider-only")
                run.amend_b(name, "local-provider-only")
                if native:
                    native_repeat.run(name, "local-provider-only")
                    final = json.loads((root / "cases" / name / "case.json").read_text())
                    self.assertEqual(final["phase"], "staged-trace-complete-with-actual-native-repetition")
                    self.assertEqual(len(final["native_rebase_operations"]), 2)
                else:
                    final = run.repeated_hosted_control(name, "local-provider-only")
                    self.assertEqual(final["phase"], "staged-trace-complete-with-labeled-hosted-control")
                self.assertTrue(all(item["passed"] for item in final["assertions"]))
                self.assertEqual(len(final["native_operations"]), 2)
                self.assertTrue(all(op["suffix_settlement"].startswith("not established")
                                    for op in final["native_operations"]))
                self.assertEqual(final["checkpoint"]["incorporated"]["B"], final["incorporated_B"])
                self.assertNotEqual(final["incorporated_B"]["tip"], final["local_B"]["tip"])
                self.assertEqual(len(provider.prs), 3)
                self.assertEqual(git.git("rev-parse", "refs/heads/authoring"), prepared["inputs"]["Bprime"])
                history = json.loads((root / "cases" / name / "archive-history.json").read_text())
                self.assertEqual(sorted(history), ["A1", "B1", "B2", "F1"])
                f_push = next(action for action in provider.actions if action.get("label") == "F-only-push")
                self.assertNotIn("refs/heads/" + prepared["branches"]["B"], f_push["updates"])
                if name == "staged-private":
                    self.assertFalse(any("source" in ref for ref in provider.refs))
                else:
                    self.assertEqual(provider.refs["refs/heads/" + prepared["branches"]["sourceF"]], final["F"])

    def test_private_staged_trace_preserves_custody_and_roles(self):
        self.exercise("staged-private")

    def test_public_staged_trace_exports_exactly_F_at_the_staged_step(self):
        self.exercise("staged-public-f-only")

    def test_native_repeat_driver_preserves_pending_edit_and_archives_locally(self):
        self.exercise("staged-private", native=True)

    def exercise_cascade(self, *, refuse_c=False):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            providers = {}

            def local_context(case, grant=None, action=None):
                directory = root / "cases" / case
                manifest = json.loads((directory / "case.json").read_text())
                git = Git(directory)
                provider = providers.setdefault(case, LocalProvider(manifest, git))
                provider.manifest, provider.git = manifest, git
                return directory, manifest, git, provider

            name = "gql-native-lower"
            with mock.patch.object(run, "ROOT", root), mock.patch.object(run, "context", local_context), mock.patch.object(cascade_followup, "context", local_context), mock.patch.object(run.time, "sleep", lambda delay: None):
                run.prepare(name)
                run.setup(name, "local-provider-only")
                run.gql_probe(name, "local-provider-only")
                directory, before, git, provider = local_context(name)
                old_b = provider.refs[run.branch_ref(before, "B")]
                old_c = provider.refs[run.branch_ref(before, "C")]
                original_api = provider.api

                def refusing_api(label, method, path, payload=None, *, kind=None):
                    if kind == "update-branch" and payload["variables"]["input"]["pullRequestId"] == before["nodes"]["C"]:
                        return {"http": 200, "data": {"errors": [{"message": "synthetic C refusal"}]}}
                    return original_api(label, method, path, payload, kind=kind)

                if refuse_c:
                    provider.api = refusing_api
                    with self.assertRaises(RuntimeError):
                        cascade_followup.run("local-provider-only")
                else:
                    cascade_followup.run("local-provider-only")
                final = json.loads((directory / "case.json").read_text())
                self.assertNotEqual(provider.refs[run.branch_ref(before, "B")], old_b)
                self.assertEqual(len(final["cascade_requests"]), 2)
                if refuse_c:
                    self.assertEqual(final["phase"], "cascade-followup-limited")
                    self.assertEqual(provider.refs[run.branch_ref(before, "C")], old_c)
                    self.assertEqual([row["layer"] for row in final["cascade_outputs"]], ["B"])
                else:
                    self.assertEqual(final["phase"], "cascade-followup-complete")
                    self.assertTrue(all(row["passed"] for row in final["assertions"]))
                    self.assertEqual([row["layer"] for row in final["cascade_outputs"]], ["B", "C"])

    def test_sequential_public_cascade_driver_locally(self):
        self.exercise_cascade()

    def test_second_cascade_refusal_retains_the_completed_prefix(self):
        self.exercise_cascade(refuse_c=True)


if __name__ == "__main__":
    unittest.main()
