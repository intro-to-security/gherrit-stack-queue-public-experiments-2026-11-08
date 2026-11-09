import copy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

import partial_once as p


def configured():
    manifest = p.template()
    manifest.update(prs={"A": 1, "B": 2, "C": 3}, nodes={"A": "PRA", "B": "PRB", "C": "PRC"},
                    request_layer="B", request_basis={"selected": "1" * 40})
    return manifest


def payload(role="B", head="1" * 40):
    return {"query": p.e.UPDATE_QUERY, "variables": {"input": {
        "pullRequestId": "PR" + role, "expectedHeadOid": head,
        "updateMethod": "REBASE", "clientMutationId": p.PREFIX + "-" + role}}}


class PartialControls(unittest.TestCase):
    def test_local_fixture_proves_B_patch_and_C_conflict(self):
        with tempfile.TemporaryDirectory(prefix=".offline-git-", dir=p.ROOT) as root:
            git, manifest = p.prepare(Path(root) / "case")
            inputs = manifest["inputs"]
            self.assertEqual(git.patch(p.c.Range(inputs["A0"], inputs["B0"])),
                             git.patch(p.c.Range(inputs["A1"], inputs["B-expected"])))
            conflict = json.loads((git.root / "merges/C-conflict-premise.json").read_text())
            self.assertEqual(conflict["returncode"], 1)
            self.assertEqual(git.git("config", "--get", "core.hooksPath"), str(git.hooks))
            self.assertEqual(git.git("fsck", "--full", "--no-dangling"), "")

    def test_foreign_scope_and_wrong_selected_member_are_rejected(self):
        manifest = configured()
        guard = p.PartialGuard(manifest)
        guard.http("update-branch", "POST", "graphql", payload())
        for request in [payload("A"), payload("C"), payload("B", "2" * 40)]:
            with self.subTest(request=request), self.assertRaises(ValueError):
                guard.http("update-branch", "POST", "graphql", request)
        with self.assertRaises(ValueError):
            guard.branch("exh-1109-workflow-other/A")
        wrong = copy.deepcopy(manifest)
        wrong["prefix"] = "exh-1109-workflow-other"
        with self.assertRaises(ValueError): p.PartialGuard(wrong)

    def test_unknown_ack_is_retained_and_not_repeated(self):
        with tempfile.TemporaryDirectory(prefix=".offline-effects-", dir=p.ROOT) as root:
            effects = p.PartialEffects(root, None, configured(), None)
            result = types.SimpleNamespace(stdout="", stderr="offline missing ack", returncode=1)
            with mock.patch.object(p.PartialGuard, "authorize"), \
                    mock.patch.object(p.e.subprocess, "run", return_value=result) as run:
                with self.assertRaises(RuntimeError):
                    effects.api("B-once", "POST", "graphql", payload(), kind="update-branch")
                with self.assertRaises(RuntimeError):
                    effects.api("B-again", "POST", "graphql", payload(), kind="update-branch")
                self.assertEqual(run.call_count, 1)
            receipt = json.loads((Path(root) / "evidence/B-once.receipt.json").read_text())
            self.assertEqual(receipt["disposition"], "unknown-outcome")
            self.assertTrue((Path(root) / "FREEZE.json").exists())

    def test_push_vectors_and_leases_cannot_expand(self):
        manifest = configured()
        manifest["inputs"] = {"A0": "1" * 40}
        manifest["initial_updates"] = {p.ref(manifest, "A"): "2" * 40}
        manifest["advance_updates"] = {p.ref(manifest, "A"): "3" * 40, manifest["archives"]["A2"]: "3" * 40}
        with tempfile.TemporaryDirectory(prefix=".offline-push-", dir=p.ROOT) as root:
            effects = p.PartialEffects(root, None, manifest, None)
            with mock.patch.object(p.e.Effects, "push") as dispatch:
                with self.assertRaises(ValueError): effects.push("extra", {}, {})
                with self.assertRaises(ValueError): effects.push("initial-push", manifest["initial_updates"], {})
                with self.assertRaises(ValueError): effects.push("advance-A", manifest["advance_updates"], {key: p.c.ZERO for key in manifest["advance_updates"]})
                dispatch.assert_not_called()

    def test_grant_pins_scope_driver_and_both_helpers(self):
        path = p.CONTROL / "OFFLINE-ONLY-NOT-CREATED.json"
        grant = {"grant_path": str(path.resolve()), "coordinator": "root", "repository": p.REPO,
                 "cases": {p.CASE: {"prefix": p.PREFIX, "actions": ["partial-once"],
                                    "effects": ["push", "create-pr", "create-stack", "update-branch"]}},
                 "harness_sha256": p.HELPERS,
                 "driver_sha256": hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest()}
        p.grant_check(path, grant)
        for field, value in [("driver_sha256", "old"), ("harness_sha256", {}), ("cases", {}), ("repository", "other/repo")]:
            bad = copy.deepcopy(grant)
            bad[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): p.grant_check(path, bad)
        with self.assertRaises(ValueError): p.grant_check(p.ROOT / path.name, grant)

    def test_fresh_full_vector_is_required_before_request(self):
        with tempfile.TemporaryDirectory(prefix=".offline-basis-", dir=p.ROOT) as root:
            effects = types.SimpleNamespace(remote_refs=lambda *args: {"unexpected": "1" * 40}, api=mock.Mock())
            with mock.patch.object(p, "coherent", return_value={}), self.assertRaises(RuntimeError):
                p.request(Path(root), configured(), effects, "B", {})
            effects.api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
