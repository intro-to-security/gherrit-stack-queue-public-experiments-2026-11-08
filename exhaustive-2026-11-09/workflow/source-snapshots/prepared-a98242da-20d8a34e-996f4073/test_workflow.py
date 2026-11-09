import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from core import ZERO, save
import effects
from effects import Guard, NOTICE, REPO, UPDATE_QUERY


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.prefix = "exh-1109-workflow-unit-abcdef"
        self.manifest = {"case": "unit", "repository": REPO, "prefix": self.prefix,
                         "branches": {"trunk": self.prefix + "/trunk", "A": self.prefix + "/A", "B": self.prefix + "/B"},
                         "planned_pr_bases": {"A": "trunk", "B": "A"},
                         "archives": {"A1": "refs/tags/gherrit/" + self.prefix + "-A/v1"},
                         "prs": {"A": 1, "B": 2}, "nodes": {"A": "NODE_A", "B": "NODE_B"}}
        self.guard = Guard(self.manifest)

    def test_foreign_repository_rejected(self):
        with self.assertRaises(ValueError):
            Guard({**self.manifest, "repository": "joshlf/gherrit"})

    def test_cross_fixture_and_undeclared_refs_rejected(self):
        for ref in ["refs/heads/main", "refs/heads/exh-1109-workflow-other/A",
                    "refs/heads/" + self.prefix + "/UNPLANNED"]:
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                self.guard.ref(ref, ZERO)

    def test_archive_cannot_be_retargeted_or_invented(self):
        ref = self.manifest["archives"]["A1"]
        self.guard.ref(ref, ZERO)
        for target, expected in [(ref, "a" * 40), (ref.replace("v1", "v99"), ZERO)]:
            with self.subTest(ref=target), self.assertRaises(ValueError):
                self.guard.ref(target, expected)

    def test_wrong_pr_relation_rejected(self):
        payload = {"title": "fixture", "body": NOTICE, "draft": False,
                   "head": self.manifest["branches"]["B"],
                   "base": self.manifest["branches"]["trunk"]}
        with self.assertRaises(ValueError):
            self.guard.http("create-pr", "POST", "repos/" + REPO + "/pulls", payload)

    def test_graphql_cannot_target_foreign_node_or_arbitrary_mutation(self):
        payload = {"query": UPDATE_QUERY, "variables": {"input": {
            "pullRequestId": "NODE_A", "expectedHeadOid": "a" * 40,
            "updateMethod": "REBASE", "clientMutationId": "unit"}}}
        self.guard.http("update-branch", "POST", "graphql", payload)
        payload["variables"]["input"]["pullRequestId"] = "FOREIGN"
        with self.assertRaises(ValueError):
            self.guard.http("update-branch", "POST", "graphql", payload)
        payload["query"] = "mutation { deleteRef(input:{refId:\"foreign\"}) { clientMutationId } }"
        with self.assertRaises(ValueError):
            self.guard.http("update-branch", "POST", "graphql", payload)

    def test_missing_or_changed_grant_rejected(self):
        with self.assertRaises(ValueError):
            self.guard.authorize("push")
        grant = self.directory / "grant.json"
        save(grant, {"coordinator": "root", "repository": REPO,
                     "cases": {"unit": {"prefix": self.prefix, "effects": ["push"], "actions": ["setup"]}},
                     "harness_sha256": {"effects.py": "0" * 64}})
        with mock.patch.object(effects, "CONTROL", self.directory):
            with self.assertRaises(ValueError):
                Guard(self.manifest, grant, "setup").authorize("push")

    def test_action_grant_prevents_later_phase_dispatch(self):
        grant = self.directory / "grant.json"
        save(grant, {"coordinator": "root", "repository": REPO,
                     "cases": {"unit": {"prefix": self.prefix, "effects": ["push"], "actions": ["setup"]}}})
        with mock.patch.object(effects, "CONTROL", self.directory):
            Guard(self.manifest, grant, "setup").authorize("push")
            with self.assertRaises(ValueError):
                Guard(self.manifest, grant, "repeat-hosted-control").authorize("push")

    def test_unknown_attempt_and_same_label_rejected_before_dispatch(self):
        sink = effects.Effects(self.directory, None, self.manifest)
        sink.intent("earlier", {"kind": "push"})
        with self.assertRaises(RuntimeError):
            sink.intent("later", {"kind": "push"}, mutation=True)
        with self.assertRaises(FileExistsError):
            sink.intent("earlier", {"kind": "read"})

    def test_no_subprocess_on_missing_write_grant(self):
        sink = effects.Effects(self.directory, None, self.manifest)
        with mock.patch.object(effects.subprocess, "run") as process:
            with self.assertRaises(ValueError):
                sink.api("write", "POST", "repos/" + REPO + "/pulls", {}, kind="create-pr")
            process.assert_not_called()

    def test_low_level_git_cannot_bypass_write_classification(self):
        sink = effects.Effects(self.directory, None, self.manifest)
        with mock.patch.object(effects.subprocess, "run") as process:
            with self.assertRaises(ValueError):
                sink.network_git("hidden", ["push", effects.URL, "HEAD:refs/heads/main"])
            with self.assertRaises(ValueError):
                sink.network_git("foreign", ["fetch", "https://example.com/repo.git"])
            process.assert_not_called()


if __name__ == "__main__":
    unittest.main()
