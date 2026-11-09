import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import partial_continue as continuation

d = continuation.d


class ContinuationControls(unittest.TestCase):
    def test_stale_base_oid_is_only_an_observation_with_exact_actual_vector(self):
        manifest = continuation.audit_original()
        terminal = json.loads((continuation.ORIGINAL / "terminal-readback.json").read_text())
        observed, full, expected = terminal["observation"], terminal["full_refs"], terminal["expected_refs"]
        result = continuation.validate_basis(manifest, observed, full, expected)
        self.assertNotEqual(result["B"]["REST_base_oid"], result["B"]["actual_named_parent_oid"])
        self.assertNotEqual(result["B"]["GraphQL_base_oid"], result["B"]["actual_named_parent_oid"])
        with self.assertRaises(RuntimeError):
            d.validate_observation(manifest, observed, expected, base_current=True)
        for change in ("selected", "canonical", "base_name", "actual_vector"):
            bad, refs = copy.deepcopy(observed), dict(full)
            if change == "selected": bad["prs"]["B"]["rest"]["head"]["sha"] = "f" * 40
            elif change == "canonical": bad["prs"]["B"]["rest"]["node_id"] = "foreign"
            elif change == "base_name": bad["prs"]["B"]["rest"]["base"]["ref"] = manifest["branches"]["trunk"]
            else: refs["refs/heads/foreign"] = "f" * 40
            with self.subTest(change=change), self.assertRaises((ValueError, RuntimeError)):
                continuation.validate_basis(manifest, bad, refs, expected)

    def test_original_writes_must_all_have_receipts_and_no_update_intent(self):
        before = continuation.original_bindings()
        with tempfile.TemporaryDirectory(prefix=".offline-prior-", dir=d.ROOT) as temp:
            root = Path(temp)
            (root / "evidence").mkdir()
            for name in ("case.json", "FREEZE.json", "MUTATION-AUDIT.json"):
                shutil.copyfile(continuation.ORIGINAL / name, root / name)
            for source in (continuation.ORIGINAL / "evidence").glob("*.json"):
                if source.name.endswith((".intent.json", ".receipt.json")):
                    shutil.copyfile(source, root / "evidence" / source.name)
            continuation.audit_original(root)
            file = root / "evidence/initial-push.receipt.json"
            saved = file.read_bytes()
            file.unlink()
            with self.assertRaises(ValueError): continuation.audit_original(root)
            file.write_bytes(saved)
            (root / "evidence/unexpected-B.intent.json").write_text(json.dumps({"kind": "update-branch"}))
            with self.assertRaises(ValueError): continuation.audit_original(root)
        self.assertEqual(before, continuation.original_bindings())

    def test_grant_binds_old_freeze_new_source_and_update_only_scope(self):
        path = d.CONTROL / "OFFLINE-CONTINUATION-NOT-CREATED.json"
        grant = {"grant_path": str(path.resolve()), "coordinator": "root", "repository": d.REPO,
                 "cases": {d.CASE: {"prefix": d.PREFIX, "actions": [continuation.ACTION], "effects": ["update-branch"]}},
                 "harness_sha256": d.HELPERS, "continuation_sha256": continuation.sha(continuation.__file__),
                 "original_bindings": continuation.original_bindings()}
        continuation.grant_check(path, grant)
        for field in ("source", "custody", "scope"):
            bad = copy.deepcopy(grant)
            if field == "source": bad["continuation_sha256"] = "old"
            elif field == "custody": bad["original_bindings"]["freeze_sha256"] = "foreign"
            else: bad["cases"][d.CASE]["effects"].append("push")
            with self.subTest(field=field), self.assertRaises(ValueError): continuation.grant_check(path, bad)

    def test_guard_cannot_create_push_or_target_foreign_selected_member(self):
        manifest = continuation.audit_original()
        manifest.update(request_layer="B", request_basis={"selected": manifest["inputs"]["B0"]})
        guard = continuation.ContinuationGuard(manifest)
        body = {"query": d.e.UPDATE_QUERY, "variables": {"input": {
            "pullRequestId": manifest["nodes"]["B"], "expectedHeadOid": manifest["inputs"]["B0"],
            "updateMethod": "REBASE", "clientMutationId": d.PREFIX + "-continuation-001-B"}}}
        guard.http("update-branch", "POST", "graphql", body)
        wrong = copy.deepcopy(body)
        wrong["variables"]["input"]["pullRequestId"] = manifest["nodes"]["C"]
        with self.assertRaises(ValueError): guard.http("update-branch", "POST", "graphql", wrong)
        wrong = copy.deepcopy(body)
        wrong["variables"]["input"]["expectedHeadOid"] = "f" * 40
        with self.assertRaises(ValueError): guard.http("update-branch", "POST", "graphql", wrong)
        with self.assertRaises(ValueError): guard.authorize("push")
        with self.assertRaises(ValueError): guard.http("create-pr", "POST", "ignored", {})


if __name__ == "__main__":
    unittest.main()
