import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import harness as h
import named_probe as n


def retained():
    case = json.loads(h.case_path("capability").read_text())
    repo = json.loads((h.EVIDENCE / "capability-repository.receipt.json").read_text())["data"]
    stack = json.loads((h.EVIDENCE / "capability-final-stack.receipt.json").read_text())["data"]
    observed = json.loads((h.EVIDENCE / "capability-after-4.observation.json").read_text())
    nodes = {letter: json.loads((h.EVIDENCE / ("capability-pr-" + letter + ".receipt.json")).read_text())["data"]["node_id"] for letter in "ABC"}
    return case, repo, stack, observed, nodes


class NamedGuardTests(unittest.TestCase):
    def test_retained_positive_scope_and_fresh_identity_guards(self):
        case, repo, stack, observed, nodes = retained()
        self.assertEqual(n.fresh_payload(case, repo, stack, observed, nodes), h.vector(case))
        bad = copy.deepcopy(observed)
        bad["prs"]["data"]["data"]["repository"]["B"]["headRefOid"] = "0" * 40
        with self.assertRaises(ValueError):
            n.fresh_payload(case, repo, stack, bad, nodes)
        bad_stack = copy.deepcopy(stack)
        bad_stack["pull_requests"].reverse()
        with self.assertRaises(ValueError):
            n.fresh_payload(case, repo, bad_stack, observed, nodes)
        bad = copy.deepcopy(observed)
        bad["refs"]["refs"]["refs/heads/" + case["trunk"]] = "0" * 40
        with self.assertRaises(ValueError):
            n.fresh_payload(case, repo, stack, bad, nodes)
        with self.assertRaises(ValueError):
            n.fresh_payload(case, {**repo, "id": 1}, stack, observed, nodes)

    def test_exact_path_and_both_reviewed_source_hashes(self):
        path = h.CONTROL / "rebase-named-grant-001.json"
        grant = {"coordinator": "root", "repository": h.REPO, "repository_id": h.REPOSITORY_ID, "cases": [n.CASE], "request_path": n.PATH, "grant_path": str(path.resolve()), "named_probe_sha256": hashlib.sha256(Path(n.__file__).read_bytes()).hexdigest(), "harness_sha256": hashlib.sha256(Path(h.__file__).read_bytes()).hexdigest()}
        n.grant_check(path, grant)
        for key, value in (("named_probe_sha256", "0" * 64), ("harness_sha256", "0" * 64), ("request_path", "repos/other/repo/stacks/653/rebase"), ("cases", ["other"])):
            with self.assertRaises(ValueError):
                n.grant_check(path, {**grant, key: value})
        with self.assertRaises(ValueError):
            n.grant_check(Path("/private/tmp/unreviewed.json"), grant)

    def test_named_unknown_acknowledgement_cannot_be_repeated(self):
        case, *_ = retained()
        result = subprocess.CompletedProcess([], 1, "", "no HTTP acknowledgement")
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(h, "EVIDENCE", Path(directory)), patch.object(h, "command", return_value=result) as process:
                with self.assertRaisesRegex(RuntimeError, "acknowledgement unknown"):
                    n.initiate(case, h.vector(case))
                with self.assertRaises(FileExistsError):
                    n.initiate(case, h.vector(case))
                self.assertEqual(process.call_count, 1)
                receipt = json.loads((Path(directory) / "capability-named-init-001.receipt.json").read_text())
                self.assertEqual(receipt["disposition"], "unknown-outcome")


if __name__ == "__main__":
    unittest.main()
