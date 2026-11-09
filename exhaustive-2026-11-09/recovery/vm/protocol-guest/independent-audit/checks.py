import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import types
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent
sys.path.insert(0, str(PACKAGE))


def load(name, filename):
    source = (PACKAGE / filename).read_text()
    module = types.ModuleType(name)
    module.__file__ = str(PACKAGE / filename)
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module, hashlib.sha256(source.encode()).hexdigest()


def blocked(*args, **kwargs):
    raise AssertionError("External process or network action forbidden in offline audit")


class FakePath:
    name = "offline-only.log"
    def __init__(self, fail=False):
        self.fail = fail
        self.stream = io.BytesIO()
    def __truediv__(self, value):
        return self
    def with_suffix(self, suffix):
        return self
    def open(self, mode):
        if self.fail:
            raise OSError("injected log-open failure")
        return FakeStream()
    def __str__(self):
        return "offline-only-fake-path"


class FakeStream(io.BytesIO):
    def fileno(self):
        return 123456
    def __exit__(self, *args):
        return False


class FakeProcess:
    pid = 987654
    stdout = FakeStream()
    def __init__(self, natural_exit):
        self.natural_exit = natural_exit
        self.kills = 0
        self.waits = 0
    def poll(self):
        return -9 if self.kills else self.natural_exit
    def kill(self):
        self.kills += 1
    def wait(self, timeout=None):
        self.waits += 1
        return -9 if self.kills else self.natural_exit


def driver_probe(controller, log_fails, natural_exit):
    state = dict(spawns=0, receipts=[])
    process = FakeProcess(natural_exit)
    def spawn(*args, **kwargs):
        state["spawns"] += 1
        return process
    serial = b'PROTOCOL {"kind":"runtime","value":{}}\nPROTOCOL {"kind":"baseline","value":{}}\nBARRIER PROTOCOL validated\n'
    with patch.object(controller, "OUT", FakePath(log_fails)), \
         patch.object(controller, "save", lambda path, value:state["receipts"].append(value)), \
         patch.object(controller.subprocess, "Popen", spawn), \
         patch.object(controller.select, "select", lambda *args:([process.stdout],[],[])), \
         patch.object(controller.os, "read", lambda *args:serial), \
         patch.object(controller.os, "fsync", lambda *args:None):
        try:
            result = controller.boot(Path("/offline-no-disk"), "validated", "cut")
            state.update(accepted=True, parsed_kinds=sorted(result))
        except Exception as error:
            state.update(accepted=False, error=str(error))
    state.update(kills=process.kills, waits=process.waits, requested_natural_exit=natural_exit)
    return state


def main():
    names = ["PLAN.md","ROOT-RECIPE.md","guest.py","oracle.py","build-root.py","MANIFEST.json", "root_controller.py", "source/protocol.py", "source/run.py", "init", "test_offline.py"]
    sources = {name:hashlib.sha256((PACKAGE/name).read_bytes()).hexdigest() for name in names}
    with patch.object(subprocess, "run", blocked), patch.object(subprocess, "Popen", blocked), patch.object(socket, "socket", blocked):
        import oracle
        import test_offline as candidate_tests
        output = io.StringIO()
        candidate = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(candidate_tests))
        mutations = []
        for label, name, value in [
            ("baseline binding contradicts frozen intent", "bindings.json", {"review":999}),
            ("baseline custody token is wrong", "authority.json", {"owner":"/foreign", "token":"wrong"}),
            ("baseline original checkpoint contradicts frozen intent", "original-checkpoint.json", {"accepted_local":"foreign"})]:
            baseline,before,after,returned = candidate_tests.model("after_return")
            for snapshot in (baseline,before,after):
                snapshot["files"][name] = candidate_tests.raw(value)
            verdict = oracle.check("after_return",baseline,before,after,returned)
            mutations.append(dict(label=label, accepted=verdict["passed"],classification=verdict["classification"],
                                  limit="Pure oracle assumes semantically valid trusted baseline; actual source worker would reject these values"))
        controller, controller_hash = load("audited_root_controller", "root_controller.py")
        drivers = {"log_open_failure":driver_probe(controller,True,None),
                   "normal_owned_cut":driver_probe(controller,False,None),
                   "unexpected_clean_exit_after_marker":driver_probe(controller,False,0),
                   "unexpected_error_exit_after_marker":driver_probe(controller,False,1)}
    pins = json.loads((PACKAGE / "SOURCE-PINS.json").read_text())
    identities = [dict(retained=pin["retained"], recorded=pin["sha256"],
                       retained_matches=hashlib.sha256((PACKAGE/pin["retained"]).read_bytes()).hexdigest()==pin["sha256"],
                       current_original_matches=hashlib.sha256(Path(pin["original"]).read_bytes()).hexdigest()==pin["sha256"]) for pin in pins]
    all_expected = candidate.wasSuccessful() and all(row["retained_matches"] and row["current_original_matches"] for row in identities)
    all_expected = all_expected and drivers["log_open_failure"]["spawns"] == 0 and not drivers["log_open_failure"]["accepted"]
    all_expected = all_expected and drivers["normal_owned_cut"]["accepted"] and drivers["normal_owned_cut"]["kills"] == 1 and drivers["normal_owned_cut"]["waits"] == 1
    all_expected = all_expected and all(not drivers[name]["accepted"] and "Guest premise failed" in drivers[name]["error"] for name in ("unexpected_clean_exit_after_marker","unexpected_error_exit_after_marker"))
    all_expected = all_expected and not any(row["accepted"] for row in mutations)
    report = dict(source_hashes=sources, tested_controller_sha256=controller_hash,
                  candidate_offline_suite=dict(tests=candidate.testsRun, errors=len(candidate.errors),failures=len(candidate.failures),output=output.getvalue()),
                  baseline_semantics_mutants=mutations, driver_probes=drivers, source_pins=identities,
                  external_actions=0, all_audit_regressions_passed=all_expected,
                  limits="Pure modeled snapshots and fake process/stream faults only; no Git, fixture, VM, container, build or network action")
    (OUT / "CHECKS.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(dict(candidate_tests=candidate.testsRun,candidate_failures=len(candidate.errors)+len(candidate.failures),
                         driver_probes={name:{key:row[key] for key in ('spawns','kills','accepted') } for name,row in drivers.items()},
                         baseline_mutants_accepted=sum(row["accepted"] for row in mutations),external_actions=0,all_expected=all_expected)))
    if not all_expected:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
