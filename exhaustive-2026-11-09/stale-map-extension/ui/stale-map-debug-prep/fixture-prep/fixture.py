"""Minimal root-owned fixture preparation and separately granted paused B push."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import uuid

ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parents[2]
CONTROL = CAMPAIGN / "control"
HELPER = CONTROL / "rootlab.py"
HELPER_SHA256 = "ae1ae63d5ee8370cbca11711f5d5e76a97669881ddf8ef8911493666393d128d"
sys.path.insert(0, str(CONTROL))
from rootlab import Lab, PERSONAL, preserve, stamp


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def owned_lab(inputs):
    if sha(HELPER) != HELPER_SHA256:
        raise RuntimeError("Reviewed helper changed")
    lab = Lab(ROOT, inputs["prefix"])
    expected = "https://github.com/" + PERSONAL + ".git"
    if (lab.git("remote", "get-url", "origin") != expected
            or lab.git("remote", "get-url", "--push", "origin") != expected
            or lab.git("config", "--get", "core.hooksPath") != "/dev/null"
            or lab.git("rev-parse", "--is-bare-repository") != "true"):
        raise RuntimeError("Unexpected owned Git origin/push destination/hooks/layout")
    return lab


def local():
    if (ROOT / "LOCAL-INPUTS.json").exists():
        raise RuntimeError("Local inputs already frozen")
    prefix = "exh-1109-ui-stale-debug-" + uuid.uuid4().hex[:10]
    m = {"repository": PERSONAL, "prefix": prefix, "prepared": stamp()}
    lab = owned_lab(m)
    trees = {"T0": {"root.txt": "Isolated website stale-map debugger fixture.\n"}}
    trees["A0"] = dict(trees["T0"], **{"a.txt": "Disjoint A " + prefix + "\n"})
    trees["B0"] = dict(trees["A0"], **{"b.txt": "Disjoint B " + prefix + "\n"})
    trees["T1"] = dict(trees["T0"], **{"trunk-progress.txt": "Independent trunk advance " + prefix + "\n"})
    trees["B2"] = dict(trees["B0"], **{"late-marker.txt": "Post-pause publication marker " + prefix + "\n"})
    for name, original in [("expected-A", "A0"), ("expected-B0", "B0"), ("expected-B2", "B2")]:
        trees[name] = dict(trees[original], **{"trunk-progress.txt": trees["T1"]["trunk-progress.txt"]})
    commits = {}
    for key, parent in [("T0", None), ("A0", "T0"), ("B0", "A0"), ("T1", "T0"), ("B2", "B0"), ("expected-A", "T1"), ("expected-B0", "expected-A"), ("expected-B2", "expected-B0")]:
        commits[key] = lab.commit(trees[key], commits.get(parent), "Record synthetic stale-map input " + key)
        lab.git("update-ref", "refs/inputs/" + key, commits[key], "0" * 40)
    refs = {key: prefix + "-" + suffix for key, suffix in [("trunk", "trunk"), ("A", "a"), ("B", "b"), ("source", "source-v1"), ("archiveA", "archive-a-v1"), ("archiveB", "archive-b-v1"), ("archiveB2", "archive-b-v2")]}
    m.update(trees=trees, commits=commits, refs=refs,
             ranges={"A": [commits["T0"], commits["A0"]], "B-v1": [commits["A0"], commits["B0"]], "B-v2": [commits["A0"], commits["B2"]]},
             objects={key: lab.git("cat-file", "commit", value) for key, value in commits.items()},
             expected_result_trees={key: lab.git("rev-parse", commits[key] + "^{tree}") for key in ("expected-A", "expected-B0", "expected-B2")},
             marker_scope="B2 is a frozen local-only input; its publication and archive-v2 occur only after root's debugger pause.")
    preserve(ROOT / "LOCAL-INPUTS.json", m)
    print(json.dumps({"prefix": prefix, "inputs_sha256": sha(ROOT / "LOCAL-INPUTS.json"), "commits": commits}))


def authorize(action, grant_path):
    path = Path(grant_path).resolve()
    g = json.loads(path.read_text())
    m = json.loads((ROOT / "LOCAL-INPUTS.json").read_text())
    if (path.parent != CONTROL.resolve() or g.get("grant_path") != str(path)
            or g.get("coordinator") != "root" or g.get("action") != action
            or g.get("repository") != PERSONAL or g.get("prefix") != m["prefix"]
            or not m["prefix"].startswith("exh-1109-ui-stale-debug-")
            or g.get("inputs_sha256") != sha(ROOT / "LOCAL-INPUTS.json")
            or g.get("source_sha256") != sha(__file__) or g.get("helper_sha256") != sha(HELPER)
            or sha(HELPER) != HELPER_SHA256):
        raise ValueError("Exact separate root action/source/input grant required")
    if action == "advance-b":
        evidence = g.get("pause_evidence", {})
        pause_path = Path(evidence.get("path", "/missing")).resolve()
        if not pause_path.is_relative_to(ROOT.parent) or sha(pause_path) != evidence.get("sha256"):
            raise ValueError("Bound root pause evidence required")
        pause = json.loads(pause_path.read_text())
        if (pause.get("coordinator") != "root" or pause.get("prefix") != m["prefix"]
                or pause.get("state") != "paused-before-dispatch"
                or g.get("ready_sha256") != sha(ROOT / "READY.json")):
            raise ValueError("Root has not bound the current debugger pause/fixture")
    return m, g


def current_refs(lab, m, label):
    result = lab.command(label, ["git", "-c", "core.hooksPath=/dev/null", "--git-dir", str(lab.bare), "ls-remote", "--refs", "origin", "refs/heads/" + m["prefix"] + "-*"])
    return {line.split()[1].removeprefix("refs/heads/"): line.split()[0] for line in result["stdout"].splitlines()}


def execute(action, grant_path):
    m, grant = authorize(action, grant_path)
    if (ROOT / "FROZEN.json").exists():
        raise RuntimeError("Frozen; no retry")
    preserve(ROOT / (action + "-START.json"), {"at": stamp(), "grant": grant})
    snapshot = ROOT / (action + "-source")
    snapshot.mkdir()
    shutil.copyfile(__file__, snapshot / "fixture.py")
    shutil.copyfile(HELPER, snapshot / "rootlab.py")
    lab = owned_lab(m)
    c, r = m["commits"], m["refs"]
    expected = {r[key]: c[value] for key, value in [("trunk", "T0"), ("A", "A0"), ("B", "B0"), ("source", "B0"), ("archiveA", "A0"), ("archiveB", "B0")]}
    try:
        if action == "prepare":
            if current_refs(lab, m, "prepare-absence"):
                raise RuntimeError("Fresh namespace is occupied")
            lab.push("prepare-initial", {name: (None, value) for name, value in expected.items()})
            prs, nodes = {}, {}
            for role, parent in [("A", "trunk"), ("B", "A")]:
                pr = lab.api("prepare-pr-" + role, "/pulls", "POST", {"head": r[role], "base": r[parent], "title": m["prefix"] + " " + role, "body": "Authorized synthetic stale-map debugger fixture.\n\n*Authored by an AI agent acting on joshlf's behalf.*"})
                prs[role], nodes[role] = pr["number"], pr["node_id"]
            stack = lab.api("prepare-register", "/stacks", "POST", {"pull_requests": [prs["A"], prs["B"]]})
            lab.push("prepare-advance-trunk", {r["trunk"]: (c["T0"], c["T1"])})
            expected[r["trunk"]] = c["T1"]
            if current_refs(lab, m, "prepare-readback") != expected:
                raise RuntimeError("Prepared exact ref vector differs")
            preserve(ROOT / "READY.json", {**m, "prs": prs, "nodes": nodes, "stack": stack, "current_refs": expected, "top_url": "https://github.com/" + PERSONAL + "/pull/" + str(prs["B"])})
            print(json.dumps({"prs": prs, "stack": stack["number"], "top_url": "https://github.com/" + PERSONAL + "/pull/" + str(prs["B"])}))
        elif action == "advance-b":
            ready = json.loads((ROOT / "READY.json").read_text())
            expected = ready["current_refs"]
            if current_refs(lab, m, "advance-b-before") != expected:
                raise RuntimeError("Paused original full ref vector changed")
            lab.push("advance-b-after-pause", {r["B"]: (c["B0"], c["B2"]), r["archiveB2"]: (None, c["B2"])})
            expected = dict(expected, **{r["B"]: c["B2"], r["archiveB2"]: c["B2"]})
            if current_refs(lab, m, "advance-b-readback") != expected:
                raise RuntimeError("Post-pause B publication readback differs")
            preserve(ROOT / "B-ADVANCED.json", {"at": stamp(), "before": c["B0"], "after": c["B2"], "current_refs": expected, "pause_evidence": grant["pause_evidence"], "range": m["ranges"]["B-v2"]})
            print(json.dumps({"B_before": c["B0"], "B_after": c["B2"], "publication_acknowledged": True}))
        else:
            raise ValueError("Unknown native action")
    except Exception as error:
        preserve(ROOT / "FROZEN.json", {"at": stamp(), "action": action, "error": repr(error), "policy": "No repeated or repaired write; root read-only reconciliation"})
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["local", "prepare", "advance-b"])
    parser.add_argument("--grant")
    args = parser.parse_args()
    if args.action == "local": local()
    elif args.grant: execute(args.action, args.grant)
    else: parser.error("Native actions require an exact root grant")
