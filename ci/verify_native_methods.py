#!/usr/bin/env python3
"""Verify frozen native-method and event-collection evidence locally."""

import hashlib
import json
from pathlib import Path

CI = Path(__file__).resolve().parent
ROOT = CI.parent
CASES = ("native-no-manual-gate", "native-no-manual-gate-merge", "native-no-manual-gate-rebase")
verified = []
for name in CASES:
    home = CI / name
    data = json.loads((home / "frozen-summary.json").read_text())
    comparison = data["B_comparison"]
    before, after = (home / "original-B-exact.patch").read_bytes(), (home / "current-B-exact.patch").read_bytes()
    assert before == after
    assert hashlib.sha256(before).hexdigest() == comparison["old_patch_sha256"] == comparison["new_patch_sha256"]
    old, new = data["commits"]["original_B"], data["commits"]["current_B"]
    assert old["tree"]["sha"] == new["tree"]["sha"] and old["author"] == new["author"] and old["message"] == new["message"]
    assert not data["status_write_receipts"] and all(not rows for rows in data["commit_status_lists"].values())
    assert not data["last_queue_observation"]["data"]["mergeQueue"]["entries"]["nodes"]
    bindings = []
    for group in data["groups"]:
        sha = group["event"]["head_sha"]
        members = [letter for letter, events in data["removals"].items()
                   if any((event.get("beforeCommit") or {}).get("oid") == sha for event in events)]
        assert len(members) == 1
        member = members[0]
        source_tree = data["commits"]["original_" + member]["tree"]["sha"]
        assert group["commit"]["tree"]["sha"] == group["context"]["tree"] == source_tree
        assert sha == group["context"]["head"] == group["context"]["env"]["GITHUB_SHA"]
        assert all(item["head_sha"] == sha and item["conclusion"] == "success" for item in group["check_runs"])
        assert not any(group["context"]["tracked_markers"].values())
        bindings.append({"member": member, "run_id": group["run_id"], "group_sha": sha,
                         "source_and_candidate_tree": source_tree, "check_ids": [r["id"] for r in group["check_runs"]]})
    verified.append({"method": data["method"], "groups": bindings, "B_patch_sha256": comparison["old_patch_sha256"],
                     "A_merged": data["fresh_prs"]["A"]["merged"], "B_merged": data["fresh_prs"]["B"]["merged"],
                     "all_queue_entries_null": True, "status_writes_observed": False})

collection = ROOT / "merge-group-artifacts"
summary_path = Path(json.loads((collection / "final-latest.json").read_text())["summary"])
summary = json.loads(summary_path.read_text())
for run in summary["runs"]:
    assert run["latest_status"] == "completed" and run["artifact_capture"] == "downloaded" and run["log_exit"] == 0
    assert len(run["captures"]) == 1
    capture = run["captures"][0]
    assert capture["action"] == "checks_requested" and all(value is True for value in capture["matches"].values())
    assert capture["check_runs"] and all(row["event_head_match"] for row in capture["check_runs"])
result = {"scope": "Artifact fidelity and recorded outcomes only; not provider settlement or universal behavior",
          "native_method_cases": verified, "final_collection": str(summary_path),
          "collection_started": summary["started"], "collection_finished": summary["finished"],
          "completed_group_runs": len(summary["runs"]),
          "group_conclusions": {name: sum(run["latest_conclusion"] == name for run in summary["runs"])
                                for name in {run["latest_conclusion"] for run in summary["runs"]}}}
(CI / "native-method-verification.json").write_text(json.dumps(result, indent=2) + "\n")
(collection / "final-verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
