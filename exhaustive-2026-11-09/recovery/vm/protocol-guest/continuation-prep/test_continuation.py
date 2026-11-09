import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

import continuation_controller as c

PREP = Path(__file__).resolve().parent
PACKAGE = PREP.parent
spec = importlib.util.spec_from_file_location("unchanged_guest_oracle", PACKAGE / "oracle.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


def log_records(name):
    return c.parse_records((PACKAGE / "actual-results-001" / name).read_bytes(), oracle)


def grant_for(records):
    runtime = records["records"]["runtime"]
    return {"runtime_python": runtime["python"],
            "runtime_git_stdout_sha256": hashlib.sha256(bytes.fromhex(runtime["git"]["stdout_hex"])).hexdigest()}


class FakeReviewed:
    def __init__(self):
        self.archives = []

    def save(self, path, value):
        with path.open("x") as stream:
            json.dump(value, stream)

    def archive(self, disk, target):
        assert disk.is_file()
        target.write_bytes(b"offline-archive-placeholder")
        self.archives.append(target.name)
        return {"file": target.name, "verified_lossless": True, "offline_fake": True}

    def bytes_under(self, path):
        return 0

    def sync_directory(self, path):
        pass


class FakeProcess:
    def __init__(self, premature=None):
        self.pid, self.returncode, self.kills = 999999, premature, 0
        self.stdout = types.SimpleNamespace(fileno=lambda: 123, close=lambda: None)

    def poll(self):
        return self.returncode

    def kill(self):
        self.kills += 1
        self.returncode = -9

    def wait(self, timeout):
        if self.returncode is None:
            raise c.subprocess.TimeoutExpired("fake-only", timeout)
        return self.returncode


class ContinuationControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".offline-", dir=PREP)
        self.out = Path(self.temp.name)
        self.patch_out = mock.patch.object(c, "OUT", self.out)
        self.patch_out.start()
        self.forbid_spawn = mock.patch.object(c.subprocess, "Popen", side_effect=AssertionError("real process forbidden"))
        self.forbid_run = mock.patch.object(c.subprocess, "run", side_effect=AssertionError("real command forbidden"))
        self.forbid_spawn.start()
        self.forbid_run.start()
        self.reviewed = FakeReviewed()

    def tearDown(self):
        self.forbid_run.stop()
        self.forbid_spawn.stop()
        self.patch_out.stop()
        self.temp.cleanup()

    def cut_and_recovery(self):
        cut_parsed = log_records("after_return-cut.log")
        recovered = log_records("after_return-recover.log")
        cut = {"receipt": {"known_stopped": True, "exact_abrupt_cut": True}, "parsed": cut_parsed}
        recovery = {"receipt": {"known_stopped": True, "natural_shutdown": False}, "parsed": recovered}
        return cut, recovery, grant_for(cut_parsed)

    def collect(self, cut, recovery, grant):
        base = self.out / "offline-base"
        base.write_bytes(b"not-a-filesystem; fake boot and archives only")
        command = types.SimpleNamespace(returncode=0, stdout="fake fsck", stderr="")
        with mock.patch.object(c, "boot", side_effect=[cut, recovery]) as boot, \
                mock.patch.object(c.subprocess, "run", return_value=command):
            result = c.collect_case("after_return", base, grant, self.reviewed, oracle)
        return result, boot

    def test_actual_failed_verdict_retained_and_known_refusal_continues(self):
        cut, recovery, grant = self.cut_and_recovery()
        row, boot = self.collect(cut, recovery, grant)
        self.assertEqual(boot.call_count, 2)
        self.assertTrue(row["cut_premise"]["exact"])
        self.assertTrue(row["matrix_continue_allowed"])
        self.assertFalse(row["verdict"]["passed"])
        self.assertEqual(row["verdict"]["classification"], "invalid_or_missing_evidence")
        self.assertEqual(len(self.reviewed.archives), 2)
        self.assertFalse((self.out / "after_return.raw").exists())
        saved = json.loads((self.out / "after_return-result.json").read_text())
        self.assertFalse(saved["disposition"]["clean_unmount"])

    def test_missing_or_malformed_result_is_diagnostic_and_stops(self):
        for value in (None, {"status": 7}, {"status": "refused"}):
            with self.subTest(value=value):
                cut, recovery, grant = self.cut_and_recovery()
                if value is None:
                    recovery["parsed"]["records"].pop("recovery_result")
                    recovery["parsed"]["counts"].pop("recovery_result")
                else:
                    recovery["parsed"]["records"]["recovery_result"] = value
                row, _ = self.collect(cut, recovery, grant)
                self.assertFalse(row["matrix_continue_allowed"])
                self.assertEqual(row["verdict"]["classification"], "recovery_collection_diagnostic")
                self.assertFalse(row["verdict"]["passed"])
                self.assertEqual(len(self.reviewed.archives), 2)
                for file in self.out.iterdir():
                    file.unlink()
                self.reviewed.archives.clear()

    def test_cut_premise_or_unknown_process_stops_without_unsafe_read(self):
        cut, recovery, grant = self.cut_and_recovery()
        cut["receipt"]["exact_abrupt_cut"] = False
        row, boot = self.collect(cut, recovery, grant)
        self.assertEqual(boot.call_count, 1)
        self.assertFalse(row["matrix_continue_allowed"])
        self.assertEqual(len(self.reviewed.archives), 1)
        for file in self.out.iterdir():
            file.unlink()
        self.reviewed.archives.clear()
        cut, recovery, grant = self.cut_and_recovery()
        recovery["receipt"]["known_stopped"] = False
        row, _ = self.collect(cut, recovery, grant)
        self.assertFalse(row["matrix_continue_allowed"])
        self.assertEqual(len(self.reviewed.archives), 1)

    def test_incomplete_snapshots_cannot_continue(self):
        for name in ("before_recovery", "after_recovery"):
            with self.subTest(name=name):
                cut, recovery, grant = self.cut_and_recovery()
                recovery["parsed"]["records"].pop(name)
                row, _ = self.collect(cut, recovery, grant)
                self.assertFalse(row["matrix_continue_allowed"])
                self.assertFalse(row["verdict"]["passed"])
                self.assertEqual(len(self.reviewed.archives), 2)
                for file in self.out.iterdir():
                    file.unlink()
                self.reviewed.archives.clear()

    def test_runtime_and_duplicate_results_cannot_be_adopted(self):
        cut, recovery, grant = self.cut_and_recovery()
        wrong = copy.deepcopy(recovery)
        wrong["parsed"]["records"]["runtime"]["prefix"] = "marked"
        self.assertFalse(c.recovery_disposition("after_return", wrong, grant)["known"])
        recovery["parsed"]["counts"]["recovery_result"] = 2
        self.assertFalse(c.recovery_disposition("after_return", recovery, grant)["known"])
        malformed = c.parse_records(b'PROTOCOL {not-json}\n', oracle)
        self.assertTrue(malformed["errors"])

    def test_boot_requires_owned_kill_and_reaps_exact_child(self):
        serial = b'PROTOCOL {"kind":"runtime","value":{}}\nBARRIER PROTOCOL marked\n'
        for premature in (None, 0, 1):
            with self.subTest(premature=premature):
                process = FakeProcess(premature)
                with mock.patch.object(c.subprocess, "Popen", return_value=process), \
                        mock.patch.object(c.select, "select", side_effect=lambda *args: ([process.stdout], [], [])), \
                        mock.patch.object(c.os, "read", side_effect=[serial, b""]):
                    result = c.boot(self.out / "not-a-disk", "marked", "cut", self.reviewed, oracle)
                self.assertTrue(result["receipt"]["known_stopped"])
                self.assertEqual(result["receipt"]["exact_abrupt_cut"], premature is None)
                self.assertEqual(process.kills, 1 if premature is None else 0)
                for file in self.out.iterdir():
                    file.unlink()

    def test_log_open_failure_spawns_nothing(self):
        (self.out / "marked-cut.log").write_bytes(b"occupied")
        with self.assertRaises(FileExistsError):
            c.boot(self.out / "not-a-disk", "marked", "cut", self.reviewed, oracle)
        c.subprocess.Popen.assert_not_called()

    def test_original_dependencies_unchanged_and_cases_exact(self):
        for name, expected in c.SOURCE_PINS.items():
            self.assertEqual(c.sha(PACKAGE / name), expected)
        self.assertEqual(len(c.CASES), 9)
        self.assertNotIn("validated", c.CASES)
        self.assertNotIn("after_return", c.CASES)


if __name__ == "__main__":
    unittest.main()
