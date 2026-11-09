"""Audit retained bytes and challenge the frozen verifier; no process or network I/O."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
CAPTURE = ROOT / "capture-001"
FIXTURE = ROOT.parent / "fixture-held-fresh-prep"
SUPPORT = ROOT / "support-inputs"
REPO = "joshlf/gherrit-native-stack-experiments-2026-11-08"
URL = "https://github.com/" + REPO + ".git"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def forbidden(*args, **kwargs):
    raise RuntimeError("Offline probe attempted process/network access")


def verifier_control(result, mutation=None):
    # Temporary copies isolate the verifier's exclusive CHECKS.json output.
    with tempfile.TemporaryDirectory(prefix="offline-control-", dir=ROOT) as name:
        base = Path(name)
        out = base / "outcome"
        capture = out / "capture-001"
        fixture = base / "fixture"
        capture.mkdir(parents=True)
        fixture.mkdir()
        for source, target in [(ROOT / "observer.py", out / "observer.py"),
                               (SUPPORT / "NETWORK-HELD-FRESH.json", base / "NETWORK-HELD-FRESH.json"),
                               (CAPTURE / "INPUT-PINS.json", capture / "INPUT-PINS.json"),
                               (CAPTURE / "fsck.command.json", capture / "fsck.command.json")]:
            shutil.copyfile(source, target)
        for key in ("READY.json", "LOCAL-INPUTS.json", "fixture.py"):
            shutil.copyfile(SUPPORT / key, fixture / key)
        value = copy.deepcopy(result)
        if mutation is not None:
            mutation(value["observations"][0])
        (capture / "RESULTS.json").write_text(json.dumps(value))
        spec = importlib.util.spec_from_file_location("held_fresh_verify", ROOT / "verify.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.ROOT, module.CAPTURE, module.FIXTURE = out, capture, fixture
        try:
            with contextlib.redirect_stdout(io.StringIO()), patch.object(subprocess, "run", forbidden), patch.object(subprocess, "Popen", forbidden), patch.object(socket, "socket", forbidden):
                module.main()
        except (AssertionError, ValueError, KeyError) as error:
            return {"accepted": False, "exception": type(error).__name__}
        return {"accepted": True}


def main():
    ready = load(SUPPORT / "READY.json")
    result = load(CAPTURE / "RESULTS.json")
    assert ready == load(FIXTURE / "READY.json")
    source_pins = load(ROOT / "SOURCE-PINS.json")
    for item in source_pins["files"]:
        old = (ROOT / "source-inputs" / item["path"]).read_bytes()
        new = (ROOT / item["path"]).read_bytes()
        assert sha(old) == item["original_sha256"] and sha(new) == item["new_sha256"]
        expected = old
        for before, after in [(b"fixture-a-fresh-prep", b"fixture-held-fresh-prep"),
                              (b"exh-1109-ui-stale-debug-a-fresh-0a2893d4d4", b"exh-1109-ui-stale-debug-held-fresh-0a10ffe99c"),
                              (b"NETWORK-A-FRESH.json", b"NETWORK-HELD-FRESH.json"),
                              (b"667", b"670"), (b"668", b"671"), (b"669", b"672"),
                              (b"refs/observed/fresh-", b"refs/observed/held-fresh-")]:
            expected = expected.replace(before, after)
        assert new == expected

    counts = {"GET": 0, "ls-remote": 0, "fetch": 0, "local": 0}
    records = sorted(CAPTURE.glob("*.command.json"))
    for path in records:
        command = load(path)
        assert command["exit"] == 0
        for suffix in ("stdout", "stderr"):
            assert sha((CAPTURE / (command["label"] + "." + suffix)).read_bytes()) == command[suffix + "_sha256"]
        argv = command["argv"]
        if argv[:2] == ["gh", "api"]:
            assert argv[2:4] == ["--method", "GET"]
            assert argv[-1] in ["repos/" + REPO + suffix for suffix in ("/pulls/670", "/pulls/671", "/stacks/672")]
            counts["GET"] += 1
        elif "ls-remote" in argv:
            i = argv.index("ls-remote")
            assert argv[i:i+3] == ["ls-remote", "--refs", URL]
            assert set(argv[i+3:]) == {"refs/heads/" + key for key in ready["current_refs"]}
            counts["ls-remote"] += 1
        elif "fetch" in argv:
            i = argv.index("fetch")
            assert argv[i:i+4] == ["fetch", "--no-tags", "--no-write-fetch-head", URL]
            cohort = command["label"].split("-")[1]
            assert set(argv[i+4:]) == {"refs/heads/" + key + ":refs/observed/held-fresh-" + cohort + "/" + key for key in ready["current_refs"]}
            counts["fetch"] += 1
        else:
            assert argv[0] in ("git", "gh")
            assert any(word in argv for word in ("--version", "init", "rev-parse", "rev-list", "cat-file", "ls-tree", "diff", "show", "fsck"))
            counts["local"] += 1
    assert counts["GET"] == 9 and counts["ls-remote"] == counts["fetch"] == 3

    for row in result["observations"]:
        index = str(row["index"])
        assert set(row["markers"]) == {"A", "B"}
        for role in ("A", "B"):
            assert row["markers"][role].encode() == (CAPTURE / ("cohort-" + index + "-marker-" + role + ".stdout")).read_bytes()
        for n, (oid, record) in enumerate(row["objects"].items()):
            raw = record["raw_commit"]
            assert raw.encode() == (CAPTURE / ("cohort-" + index + "-object-" + str(n) + "-raw.stdout")).read_bytes()
            headers, message = raw.split("\n\n", 1)
            lines = headers.splitlines()
            assert record["tree"] == lines[0].split()[1]
            assert record["parents"] == [line[7:] for line in lines if line.startswith("parent ")]
            assert record["author"] == next(line[7:] for line in lines if line.startswith("author "))
            assert record["committer"] == next(line[10:] for line in lines if line.startswith("committer "))
            assert record["message"] == message
            assert record["agent_trailers"] == [line for line in message.splitlines() if line.startswith("Agent-authored-by:")]
            assert record["has_gpgsig"] == any(line.startswith("gpgsig ") for line in lines)
    network = load(SUPPORT / "NETWORK-HELD-FRESH.json")
    pause = load(SUPPORT / "PAUSE-HELD-FRESH.json")
    after = load(SUPPORT / "PAUSE-HELD-FRESH-AFTER-HOLD.json")
    timer = load(SUPPORT / "HOLD-VERIFIED.json")
    start = load(SUPPORT / "HOLD-START.json")
    expected_body = {"expectedHeadOids": {"670": ready["commits"]["A2"], "671": ready["commits"]["B0"]}}
    assert pause["body"] == after["body"] == network["selected_entries"][0]["request_body"] == expected_body
    assert pause["method"] == after["method"] == network["selected_entries"][0]["method"] == "POST"
    assert pause["url"] == after["url"] == network["selected_entries"][0]["url"]
    assert start["source_sha256"] == sha((SUPPORT / "hold_unchanged.py").read_bytes())
    assert start["ready_sha256"] == sha((SUPPORT / "READY.json").read_bytes())
    assert start["pause_sha256"] == sha((SUPPORT / "PAUSE-HELD-FRESH.json").read_bytes())
    assert after["hold_verified_sha256"] == sha((SUPPORT / "HOLD-VERIFIED.json").read_bytes())
    assert timer["elapsed_monotonic_seconds"] == network["hold_monotonic_seconds"] >= 420
    assert len(timer["samples"]) == 3 and [sample["target_seconds"] for sample in timer["samples"]] == [0, 210, 420]
    assert all(sample["refs"] == ready["current_refs"] and sample["matches"] for sample in timer["samples"])
    assert [entry["status"] for entry in network["selected_entries"]] == [200, 200, 200]
    assert [entry["response"]["jobState"] for entry in network["selected_entries"][1:]] == ["PENDING", "DONE"]
    assert [(q["number"], q["state"]) for q in network["selected_entries"][-1]["response"]["pullRequestStates"]] == [(670, "SUCCEEDED"), (671, "SUCCEEDED")]

    controls = {"positive": verifier_control(result)}
    mutations = {
        "missing_A_second_commit": lambda row: row["A_rewritten_commits"].pop(),
        "lost_B_marker": lambda row: row["markers"].update(B=""),
        "wrong_B_parent": lambda row: row["objects"][row["B_rewritten_commits"][0]].update(parents=[ready["commits"]["A0"]]),
        "changed_B_own_patch": lambda row: row.update(actual_B_full_patch=""),
        "wrong_canonical_repository": lambda row: row["REST_PRs"]["A"]["head"]["repo"].update(id=0),
        "missing_rewritten_A_trailer": lambda row: row["objects"][row["A_rewritten_commits"][-1]].update(agent_trailers=[]),
    }
    for label, mutation in mutations.items():
        controls[label] = verifier_control(result, mutation)
    assert controls["positive"]["accepted"]
    assert all(not value["accepted"] for key, value in controls.items() if key != "positive")
    output = dict(passed=True, command_receipts=len(records), command_counts=counts,
                  stdout_stderr_hashes_match=True, literal_source_adaptation=True,
                  raw_commit_fields_reparsed=True, exact_marker_keys_and_outputs=True,
                  held_fresh_inputs_consistent=True, controls=controls,
                  limits="Offline byte/consistency checks only. No process/network call, HAR read, cryptographic signature check, continuous ref lock, internal dispatch boundary or future-write-fence proof.")
    with (ROOT / "OFFLINE-CHECKS.json").open("x") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
