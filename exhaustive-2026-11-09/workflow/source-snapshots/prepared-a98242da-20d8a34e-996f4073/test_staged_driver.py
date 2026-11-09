import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from core import Git, TRAILER
import run


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
            return {"http": 201, "data": {"id": 1000, "number": 1000}}
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
        return {"prs": {layer: {"rest": self.rest_pr(number), "graphql": {}}
                        for layer, number in self.manifest["prs"].items()},
                "refs": dict(self.refs)}

    def freeze(self, label, reason):
        raise AssertionError("Unexpected simulated fixture freeze: " + reason)


class FullDriverTests(unittest.TestCase):
    def exercise(self, name):
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

            with mock.patch.object(run, "ROOT", root), mock.patch.object(run, "context", local_context):
                prepared = run.prepare(name)
                _, manifest, git, provider = local_context(name)
                self.assertEqual(git.git("rev-parse", "refs/heads/authoring"), prepared["inputs"]["B0"])
                run.setup(name, "local-provider-only")
                run.stage_f(name, "local-provider-only")
                run.amend_b(name, "local-provider-only")
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


if __name__ == "__main__":
    unittest.main()
