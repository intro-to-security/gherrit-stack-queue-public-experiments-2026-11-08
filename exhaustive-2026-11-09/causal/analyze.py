"""Summarize retained observations without making any network request."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"


def read(path):
    return json.loads(path.read_text())


def summarize(case):
    name = case["name"]
    samples = list(EVIDENCE.glob(name + "-after-*.observation.json")) + list(EVIDENCE.glob(name + "-reconcile-*.observation.json"))
    samples.sort(key=lambda path: read(path)["refs"]["start"]["utc"])
    before_path = EVIDENCE / (name + "-before.observation.json")
    before = read(before_path) if before_path.exists() else None
    final = read(samples[-1]) if samples else None
    marker = case.get("marker")
    marker_attempt = EVIDENCE / (name + "-marker.marker-before-dispatch.json")
    if not marker and marker_attempt.exists():
        marker = {key: read(marker_attempt)[key] for key in ("target", "ref", "before", "marker", "nonce")}
    terminal = case.get("terminal")
    result = {"name": name, "phase": case["phase"], "prs": case["prs"], "stack": case.get("stack"), "merge_uuid": case.get("merge_uuid"), "method": case["method"], "terminal": terminal["data"] if terminal else None, "marker": marker, "marker_publication_acknowledged": case.get("marker") is not None, "samples": len(samples), "members": {}, "events": []}
    seen = set()
    if final:
        initial_prs = before["graphql"]["data"]["data"]["repository"]
        final_prs = final["graphql"]["data"]["data"]["repository"]
        for letter, pr in final_prs.items():
            ref = "refs/heads/" + case["heads"][letter]["ref"]
            initial_sha = before["refs"]["refs"][ref]
            final_sha = final["refs"]["refs"][ref]
            result["members"][letter] = {"number": pr["number"], "initial_ref": initial_sha, "final_ref": final_sha, "initial_object": before["refs"]["objects"][initial_sha], "final_object": final["refs"]["objects"][final_sha], "initial_base": initial_prs[letter]["baseRefName"], "final_base": pr["baseRefName"], "final_pr_state": pr["state"], "final_pr_head": pr["headRefOid"], "pr_ref_agree_in_final_separate_reads": pr["headRefOid"] == final_sha}
    for sample_path in samples:
        sample = read(sample_path)
        for letter, pr in sample["graphql"]["data"]["data"]["repository"].items():
            for event in pr["timelineItems"]["nodes"]:
                if event["id"] not in seen:
                    seen.add(event["id"])
                    result["events"].append({"member": letter, "first_observed_response_interval": {"start": sample["graphql"]["start"], "end": sample["graphql"]["end"]}, **event})
    if marker:
        record = read(EVIDENCE / (name + "-marker.commit.json"))
        push = read(EVIDENCE / (name + "-marker-push.receipt.json"))
        result["marker_commit_interval"] = {"start": record["start"], "end": record["end"]}
        result["marker_push_interval"] = {"start": push["start"], "end": push["end"]}
        result["marker_is_final_git_head"] = bool(final) and final["refs"]["refs"].get(marker["ref"]) == marker["marker"]
        result["force_events_from_marker"] = [event for event in result["events"] if event["__typename"] == "HeadRefForcePushedEvent" and (event.get("beforeCommit") or {}).get("oid") == marker["marker"]]
        if terminal:
            result["marker_creation_after_terminal_receipt_seconds"] = record["start"]["monotonic"] - terminal["end"]["monotonic"]
        if samples:
            # Reconciliation may use another process; compare absolute captured UTC.
            from datetime import datetime
            result["last_git_read_start_after_marker_push_seconds"] = (datetime.fromisoformat(final["refs"]["start"]["utc"]) - datetime.fromisoformat(push["end"]["utc"])).total_seconds()
    return result


if __name__ == "__main__":
    results = [summarize(read(path)) for path in sorted(ROOT.glob("*.case.json"))]
    (ROOT / "summary.json").write_text(json.dumps(results, indent=2) + "\n")
    for result in results:
        print(json.dumps({key: result.get(key) for key in ("name", "phase", "prs", "stack", "method", "terminal", "samples", "marker_is_final_git_head", "marker_creation_after_terminal_receipt_seconds", "last_git_read_start_after_marker_push_seconds", "force_events_from_marker")}))
