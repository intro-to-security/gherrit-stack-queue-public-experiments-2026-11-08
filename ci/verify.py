#!/usr/bin/env python3
"""Check retained queue outcomes locally without replaying remote effects."""

import hashlib
import json
from pathlib import Path

HOME = Path(__file__).resolve().parent
DATA = json.loads((HOME / "results.json").read_text())
FIXTURES = json.loads((HOME / "fixtures.json").read_text())
EVIDENCE = HOME / "evidence"
PROPOSAL = HOME.parent / "ci-workflow-proposal"


def refs(snapshot):
    return {line.split("\t")[1]: line.split("\t")[0] for line in snapshot["refs"].splitlines()}


def receipt(name, suffix):
    matches = list(EVIDENCE.glob(name + "-final-" + suffix + "*.receipt.json"))
    assert len(matches) == 1
    value = json.loads(matches[0].read_text())
    assert value["http"] == 200
    return value["data"]


def blob(path):
    content = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


checks = []
for name, value in DATA.items():
    fixture = FIXTURES[name]
    group = value["group"]
    context = group["context"]
    sha = group["event"]["head_sha"]
    source = json.loads((EVIDENCE / (name + "-A.commit.json")).read_text())
    commit = receipt(name, "git-commit")
    check_runs = receipt(name, "check-runs")["check_runs"]
    observe = [r for r in check_runs if r["name"] == "queue-observe"]
    expected = "success" if name == "single-held-release" else "failure"
    assert len(observe) == 1 and observe[0]["head_sha"] == sha
    assert observe[0]["conclusion"] == expected and observe[0]["app"]["id"] == 15368
    assert sha == context["head"] == context["env"]["GITHUB_SHA"] == group["run"]["head_sha"]
    assert commit["tree"]["sha"] == context["tree"] == source["tree"]
    assert [p["sha"] for p in commit["parents"]] == [fixture["trunk_sha"]]
    assert context["workflow_blob"] == blob(PROPOSAL / ".github/workflows/queue-observe.yml")
    assert context["observer_blob"] == blob(PROPOSAL / ".github/scripts/queue_observe.py")
    assert value["ruleset"]["request"]["bypass_actors"] == []
    assert value["ruleset"]["request"]["conditions"]["ref_name"]["include"] == ["refs/heads/" + fixture["trunk"]]
    final = value["released-second-read"] if name == "single-held-release" else value["failure-observation"]
    final_refs = refs(final["snapshot"])
    assert final["pr"]["mergeQueueEntry"] is None
    assert final_refs["refs/heads/" + fixture["heads"]["A"]["ref"]] == fixture["heads"]["A"]["sha"]
    assert final_refs["refs/tags/" + fixture["prefix"] + "/authored/A/v1"] == fixture["heads"]["A"]["sha"]
    if name == "single-held-release":
        held = value["held-confirmation"]
        assert not held["pr"]["merged"] and held["pr"]["mergeQueueEntry"]["state"] == "AWAITING_CHECKS"
        assert refs(held["snapshot"])["refs/heads/" + fixture["trunk"]] == fixture["trunk_sha"]
        assert value["release"]["sha"] == sha
        assert final["pr"]["merged"] and final_refs["refs/heads/" + fixture["trunk"]] == sha
    else:
        assert not final["pr"]["merged"] and final["pr"]["state"] == "OPEN"
        assert final_refs["refs/heads/" + fixture["trunk"]] == fixture["trunk_sha"]
        events = value["removal_reasons"]["data"]["node"]["timelineItems"]["nodes"]
        removal = [e for e in events if e["__typename"] == "RemovedFromMergeQueueEvent"]
        assert len(removal) == 1 and removal[0]["reason"] == "failed_checks"
        assert removal[0]["beforeCommit"]["oid"] == sha
    checks.append({"fixture": name, "pr": fixture["prs"]["A"], "group_sha": sha,
                   "workflow_conclusion": expected, "final_merged": final["pr"]["merged"],
                   "last_queue_entry": final["pr"]["mergeQueueEntry"], "final_observed_at": final["at"]})

(EVIDENCE / "verification.json").write_text(json.dumps({"scope": "retained observations only; no future-write guarantee",
    "checks": checks}, indent=2) + "\n")
print(json.dumps(checks, indent=2))
