"""Offline guards for the proposed experimental writer; no candidate source runs."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import harness as h


def case():
    return {"name": "capability", "prefix": "exh-1109-causal-rb-capability", "stack": 99, "trunk_sha": "a" * 40, "prs": {"A": 11, "B": 12, "C": 13}, "heads": {letter: {"sha": str(index + 1) * 40, "ref": "exh-1109-causal-rb-capability/" + letter} for index, letter in enumerate("ABC")}}


class GuardTests(unittest.TestCase):
    def test_full_vector_and_deliberate_lower_upper_variants(self):
        c = case()
        correct = h.vector(c)["expected_head_oid_by_pr_number"]
        self.assertEqual(set(correct), {"11", "12", "13"})
        lower = h.vector(c, "wrong-lower")["expected_head_oid_by_pr_number"]
        upper = h.vector(c, "wrong-upper")["expected_head_oid_by_pr_number"]
        self.assertEqual([number for number in correct if lower[number] != correct[number]], ["11"])
        self.assertEqual([number for number in correct if upper[number] != correct[number]], ["13"])
        self.assertTrue(all(h.OID.fullmatch(value) for value in [*lower.values(), *upper.values()]))

    def test_numeric_repository_owned_group_and_complete_vector_are_required(self):
        c = case()
        h.guard_http(c, "PUT", h.route(c), h.vector(c))
        wrong_paths = ["repositories/1/stacks/99/rebase", f"repositories/{h.REPOSITORY_ID}/stacks/100/rebase", "repos/" + h.REPO + "/settings"]
        for path in wrong_paths:
            with self.assertRaises(ValueError):
                h.guard_http(c, "PUT", path, h.vector(c))
        for payload in (None, {"expected_head_oid_by_pr_number": {"11": "1" * 40}}, {"expected_head_oid_by_pr_number": {"11": "1" * 40, "12": "2" * 40, "13": "invalid"}}):
            with self.assertRaises(ValueError):
                h.guard_http(c, "PUT", h.route(c), payload)

    def test_push_requires_exact_owned_leases_before_any_process(self):
        c = case()
        with patch.object(h, "git", side_effect=AssertionError("process reached")):
            with self.assertRaises(ValueError):
                h.push(c, "bad", {"refs/heads/main": "1" * 40}, {})
            with self.assertRaises(ValueError):
                h.push(c, "bad", {"refs/heads/main": "1" * 40}, {"refs/heads/main": "2" * 40})
            with self.assertRaises(ValueError):
                h.own_ref(c, "refs/heads/exh-1109-causal-rb-other/A")

    def test_unknown_write_is_retained_and_never_repeated(self):
        c = case()
        result = subprocess.CompletedProcess([], 1, "", "connection ended before HTTP acknowledgement")
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(h, "EVIDENCE", Path(directory)), patch.object(h, "command", return_value=result) as process:
                with self.assertRaisesRegex(RuntimeError, "Unknown HTTP"):
                    h.api(c, "write", "PUT", h.route(c), h.vector(c))
                receipt = json.loads((Path(directory) / "write.receipt.json").read_text())
                self.assertEqual(receipt["disposition"], "unknown-outcome")
                with self.assertRaises(FileExistsError):
                    h.api(c, "write", "PUT", h.route(c), h.vector(c))
                self.assertEqual(process.call_count, 1)

    def test_done_partial_and_unknown_results_remain_distinct(self):
        c = case()
        self.assertEqual(h.job_disposition(c, {"status": "pending"})["phase"], "pending")
        results = [{"pull_request_number": number, "status": "succeeded"} for number in c["prs"].values()]
        self.assertTrue(h.job_disposition(c, {"job_state": "done", "pull_requests": results})["all_succeeded"])
        results[1]["status"] = "conflict"
        self.assertFalse(h.job_disposition(c, {"job_state": "done", "pull_requests": results})["all_succeeded"])
        self.assertFalse(h.job_disposition(c, {"job_state": "done", "pull_requests": results[:1]})["complete_member_results"])
        for body in ({"job_state": "paused"}, {"job_state": "done"}):
            with self.assertRaises(ValueError):
                h.job_disposition(c, body)

    def test_failed_job_cannot_authorize_marker(self):
        with patch.object(h, "git_read", side_effect=AssertionError("read reached")):
            with self.assertRaises(ValueError):
                h.publish_marker({"terminal": {}, "job_disposition": {"all_succeeded": False}})

    def test_existing_case_cannot_reinitialize(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(h, "ROOT", Path(directory)), patch.object(h, "initialize", side_effect=AssertionError("initialization reached")):
                (Path(directory) / "capability.case.json").write_text("{}")
                with self.assertRaisesRegex(RuntimeError, "Existing case"):
                    h.fixture("capability")


if __name__ == "__main__":
    unittest.main()
