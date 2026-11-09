import copy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

import complete_controller as wrapper

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent


class CompleteControls(unittest.TestCase):
    def test_complete_only_grant_and_full_source_vector(self):
        def sha(path):
            path = Path(path)
            if path == Path(wrapper.__file__): return "wrapper"
            if path == PACKAGE / wrapper.COLLECTOR: return wrapper.COLLECTOR_SHA256
            if path == PACKAGE / "oracle.py": return "oracle"
            if path.name == "test-initramfs.gz": return "image"
            if path.name == "Image-virt": return "kernel"
            raise AssertionError(path)
        collector = types.SimpleNamespace(DISK_BYTES=33554432, SOURCE_PINS={"oracle.py": "oracle"}, sha=sha)
        grant = {"coordinator": "root", "grant_path": str(PACKAGE / "COMPLETE-GRANT.json"),
                 "root": str(PACKAGE), "out": str(PACKAGE / "actual-results-complete-001"),
                 "cases": ["complete"], "disk_bytes": 33554432, "runtime_python": "captured-python",
                 "runtime_git_stdout_sha256": "0" * 64, "initramfs_sha256": "image", "kernel_sha256": "kernel",
                 "source_hashes": {"oracle.py": "oracle", wrapper.COLLECTOR: wrapper.COLLECTOR_SHA256, wrapper.SELF: "wrapper"}}
        with mock.patch.object(wrapper, "ROOT", PACKAGE), \
                mock.patch.object(wrapper, "OUT", PACKAGE / "actual-results-complete-001"), \
                mock.patch.object(wrapper, "GRANT", PACKAGE / "COMPLETE-GRANT.json"):
            wrapper.check_grant(grant, collector)
            for field, value in [("cases", ["result_checkpoint"]), ("out", "old-output"),
                                 ("initramfs_sha256", "wrong"), ("source_hashes", {wrapper.SELF: "wrapper"})]:
                bad = copy.deepcopy(grant)
                bad[field] = value
                with self.subTest(field=field), self.assertRaises(RuntimeError):
                    wrapper.check_grant(bad, collector)

    def test_one_explicit_call_preserves_failed_verdict(self):
        with tempfile.TemporaryDirectory(prefix=".offline-", dir=HERE) as temporary:
            parent = Path(temporary)
            output = parent / "new-output"
            grant = parent / "offline-grant.json"
            grant.write_text("{}")
            saved, calls = {}, []
            def save(path, value):
                self.assertNotIn(path.name, saved)
                saved[path.name] = value
            reviewed = types.SimpleNamespace(save=save, sync_directory=lambda path: None)
            oracle = object()
            row = {"prefix": "complete", "verdict": {"passed": False, "classification": "retained-failure"}, "matrix_continue_allowed": True}
            def collect(prefix, base, value, primitives, strict_oracle):
                calls.append(prefix)
                self.assertIs(strict_oracle, oracle)
                self.assertIs(primitives, reviewed)
                return row
            collector = types.SimpleNamespace(DISK_BYTES=1, reviewed_modules=lambda: (reviewed, oracle),
                                              budget=lambda *args: None, collect_case=collect)
            make = types.SimpleNamespace(returncode=0, stdout="fake-only", stderr="", check_returncode=lambda: None)
            with mock.patch.object(wrapper, "OUT", output), mock.patch.object(wrapper, "GRANT", grant), \
                    mock.patch.object(wrapper, "load_collector", return_value=collector), \
                    mock.patch.object(wrapper, "check_grant"), \
                    mock.patch.object(wrapper.subprocess, "run", return_value=make):
                wrapper.main()
            self.assertEqual(calls, ["complete"])
            self.assertEqual(collector.OUT, output)
            self.assertFalse(saved["RESULTS.json"]["all_passed"])
            self.assertEqual(saved["RESULTS.json"]["cases"], [row])

    def test_parent_collector_and_unrun_evidence_remain_exact(self):
        self.assertEqual(hashlib.sha256((PACKAGE / wrapper.COLLECTOR).read_bytes()).hexdigest(), wrapper.COLLECTOR_SHA256)
        result = json.loads((PACKAGE / "actual-results-continuation-001/RESULTS.json").read_text())
        self.assertEqual(result["not_run"], ["complete"])
        self.assertNotIn("complete", [row["prefix"] for row in result["cases"]])
        self.assertEqual(wrapper.CASES, ("complete",))


if __name__ == "__main__":
    unittest.main()
