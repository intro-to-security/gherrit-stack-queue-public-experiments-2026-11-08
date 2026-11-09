"""Effect-boundary checks; all process calls are replaced or rejected."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import harness
import git_gate


class EffectBoundaryTests(unittest.TestCase):
    def test_unknown_write_is_retained_and_cannot_be_redispatched(self):
        case = {"prefix": harness.PREFIX + "self", "prs": {"A": 1, "B": 2}}
        result = subprocess.CompletedProcess([], 1, "", "transport ended without an HTTP response")
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory)
            with patch.object(harness, "EVIDENCE", evidence), patch.object(harness, "run", return_value=result) as process:
                with self.assertRaisesRegex(RuntimeError, "Unknown HTTP"):
                    harness.api("write", "POST", "repos/" + harness.REPO + "/stacks", {"pull_requests": [1, 2]}, case=case)
                receipt = json.loads((evidence / "write.receipt.json").read_text())
                self.assertEqual(receipt["disposition"], "unknown-outcome")
                self.assertTrue((evidence / "write.intent.json").exists())
                with self.assertRaises(FileExistsError):
                    harness.api("write", "POST", "repos/" + harness.REPO + "/stacks", {"pull_requests": [1, 2]}, case=case)
                self.assertEqual(process.call_count, 1)

    def test_every_push_target_has_a_lease_and_cannot_escape_namespace(self):
        with patch.object(harness, "git", side_effect=AssertionError("process must not be reached")):
            with self.assertRaisesRegex(ValueError, "explicit lease"):
                harness.push("bad", {"refs/heads/main": "a" * 40}, {})
            with self.assertRaisesRegex(ValueError, "namespace"):
                harness.push("bad", {"refs/heads/main": "a" * 40}, {"refs/heads/main": "b" * 40})

    def test_pending_receipt_cannot_authorize_post_terminal_marker(self):
        with patch.object(harness, "git_read", side_effect=AssertionError("read must not be reached")):
            with self.assertRaisesRegex(ValueError, "terminal merged"):
                harness.publish_marker({}, "bad", terminal={"data": {"status": "pending"}})

    def test_http_policy_refuses_cross_fixture_and_settings(self):
        case = {"prefix": harness.PREFIX + "self", "prs": {"A": 1, "B": 2}}
        with self.assertRaisesRegex(ValueError, "Cross-fixture"):
            harness.allowed_http("POST", "repos/" + harness.REPO + "/pulls", {"head": harness.PREFIX + "other/A", "base": harness.PREFIX + "self/trunk"}, case)
        with self.assertRaisesRegex(ValueError, "effect policy"):
            harness.allowed_http("PATCH", "repos/" + harness.REPO, {"allow_squash_merge": False}, case)

    def test_cli_git_gate_requires_full_active_atomic_lease_vector(self):
        ref = "refs/heads/exh-1109-causal-ordinary-sync-3/B"
        valid = ["-c", "push.pushOption=pull.stacked", "push", "origin", "--force-with-lease=" + ref + ":" + "a" * 40, "--atomic", ref + ":" + ref]
        self.assertTrue(git_gate.validate_push(valid, {ref}))
        for args in (["push", "origin", "--atomic", ref + ":" + ref], ["push", "origin", "--force-with-lease=" + ref + ":" + "a" * 40, ref + ":" + ref], ["push", "origin", "--atomic", "--force-with-lease=refs/heads/main:" + "a" * 40, "refs/heads/main:refs/heads/main"]):
            with self.assertRaises(ValueError):
                git_gate.validate_push(args, {ref})


if __name__ == "__main__":
    unittest.main()
