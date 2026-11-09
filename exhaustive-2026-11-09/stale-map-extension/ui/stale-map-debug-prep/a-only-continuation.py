"""Prearchive A2, then separately advance only A during the captured pause."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture-a-prep"
CONTROL = HERE.parents[1] / "control"
ORIGINAL_SOURCE_SHA = "91c4a317145202a640cc348f2cef6358518589e5db495f0e8d2f3d70cc814dfc"
INPUTS_SHA = "db41a6aba4751aa2e69914b4bdd80ad2267cfa1fd10b42ce920003c1eda7dfe3"
PREFIX = "exh-1109-ui-stale-debug-a-5949ea0a29"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(action, grant_path):
    if digest(FIXTURE / "fixture.py") != ORIGINAL_SOURCE_SHA or digest(FIXTURE / "LOCAL-INPUTS.json") != INPUTS_SHA:
        raise ValueError("Frozen source or inputs changed")
    spec = importlib.util.spec_from_file_location("lower_a_fixture", FIXTURE / "fixture.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    grant = json.loads(grant_path.read_bytes())
    if (grant_path.parent != CONTROL or grant.get("coordinator") != "root"
            or grant.get("action") != action or grant.get("source_sha256") != digest(Path(__file__))
            or grant.get("prefix") != PREFIX or grant.get("inputs_sha256") != INPUTS_SHA):
        raise ValueError("Separate exact root grant required")
    ready_path = FIXTURE / ("READY.json" if action == "prearchive" else "READY-A-ARCHIVED.json")
    if grant.get("ready_sha256") != digest(ready_path):
        raise ValueError("Ready basis changed")
    ready = json.loads(ready_path.read_bytes())
    if ready["prefix"] != PREFIX or (FIXTURE / "FROZEN.json").exists() or (FIXTURE / "advance-a-START.json").exists():
        raise ValueError("Wrong or previously advanced/frozen fixture")
    if action == "advance-only-a":
        evidence = grant["pause_evidence"]
        path = Path(evidence["path"]).resolve()
        if not path.is_relative_to(HERE) or digest(path) != evidence["sha256"]:
            raise ValueError("Pause evidence changed")
        pause = json.loads(path.read_bytes())
        if pause.get("coordinator") != "root" or pause.get("prefix") != PREFIX or pause.get("state") != "paused-before-dispatch":
            raise ValueError("Actual pre-dispatch pause required")
    module.preserve(FIXTURE / (action + "-START.json"), {"at": module.stamp(), "grant": grant})
    lab = module.owned_lab(ready)
    expected = dict(ready["current_refs"])
    if module.current_refs(lab, ready, action + "-before") != expected:
        raise ValueError("Exact ref basis changed; stop without retry")
    c, r = ready["commits"], ready["refs"]
    if action == "prearchive":
        lab.push("prearchive-a2", {r["archiveA2"]: (None, c["A2"])})
        expected[r["archiveA2"]] = c["A2"]
    else:
        if expected[r["archiveA2"]] != c["A2"] or expected[r["A"]] != c["A0"] or expected[r["B"]] != c["B0"]:
            raise ValueError("Not the archived original member vector")
        lab.push("advance-only-a-after-pause", {r["A"]: (c["A0"], c["A2"])})
        expected[r["A"]] = c["A2"]
    if module.current_refs(lab, ready, action + "-readback") != expected:
        raise ValueError("Post-effect refs differ; preserve uncertainty and do not retry")
    if action == "prearchive":
        module.preserve(FIXTURE / "READY-A-ARCHIVED.json", {**ready, "current_refs": expected, "archive_prepared_at": module.stamp(), "original_ready_sha256": digest(FIXTURE / "READY.json"), "scope": "Archive created before browser load; paused continuation changes only existing A ref."})
    else:
        module.preserve(FIXTURE / "A-ADVANCED.json", {"at": module.stamp(), "before": c["A0"], "after": c["A2"], "selected_B_unchanged": c["B0"], "current_refs": expected, "pause_evidence": grant["pause_evidence"], "range": ready["ranges"]["A-v2"], "controller": "a-only-continuation.py; only A changed during pause, archive already retained"})
    print(json.dumps({"action": action, "member_A": expected[r["A"]], "member_B": expected[r["B"]], "refs": len(expected)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prearchive", "advance-only-a"])
    parser.add_argument("--grant", required=True, type=Path)
    args = parser.parse_args()
    main(args.action, args.grant.resolve())
