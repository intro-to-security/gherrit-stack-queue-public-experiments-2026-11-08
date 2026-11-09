import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def evaluate(snapshot, layer, captured_sha, context="Validate and Test", app=15368):
    observed = snapshot["prs"][layer]
    if observed["pr"]["head"]["sha"] != captured_sha:
        return dict(ready=False, reason="observed_head_differs_from_captured_input")
    checks = [check for check in observed["source_checks"]["check_runs"]
              if check["name"] == context and check["app"]["id"] == app and check["head_sha"] == captured_sha]
    if not checks:
        return dict(ready=False, reason="missing_exact_context_SHA_producer")
    if any(check["status"] != "completed" for check in checks):
        return dict(ready=False, reason="current_check_incomplete")
    if any(check["conclusion"] != "success" for check in checks):
        return dict(ready=False, reason="current_check_not_successful")
    return dict(ready=True, reason="exact_current_context_SHA_producer_success")


def load(name):
    value = json.loads((ROOT / "observations" / (name + ".json")).read_text())
    return value.get("snapshot", value)


def main():
    case = json.loads((ROOT / "cases" / "p.json").read_text())
    expected = case["heads"]["A"]["sha"]
    stale = load("p-current-fails-final")
    green = load("p-required-green-final")
    failed = load("p-after-stale-control")
    green_sha = green["prs"]["A"]["pr"]["head"]["sha"]
    probes = [
        dict(name="stale-returned-green-is-not-current", result=evaluate(stale, "A", expected), expected=False),
        dict(name="exact-prior-green-positive-control", result=evaluate(green, "A", green_sha), expected=True),
        dict(name="actual-current-failure-is-not-ready", result=evaluate(failed, "A", expected), expected=False),
        dict(name="wrong-producer-control", result=evaluate(green, "A", green_sha, app=-1), expected=False),
        dict(name="wrong-context-control", result=evaluate(green, "A", green_sha, context="other"), expected=False)]
    unsafe_ready = all(check["status"] == "completed" and check["conclusion"] == "success"
                       for check in stale["prs"]["A"]["source_checks"]["check_runs"])
    report = dict(captured_input=expected, stale_returned_head=stale["prs"]["A"]["pr"]["head"]["sha"],
                  old_ready_helper_claim=True, unsafe_returned_green_control=unsafe_ready,
                  corrected_boundary_rejects_stale=evaluate(stale, "A", expected), probes=probes,
                  all_expected=all(row["result"]["ready"] == row["expected"] for row in probes),
                  meaning="Corrected exact-input acceptance over retained actual observations; no new hosted request; not production integration")
    (ROOT / "EXACT-CI-ACCEPTANCE.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(probes=len(probes), all_expected=report["all_expected"], captured=expected,
                          stale=report["stale_returned_head"])))
    if not report["all_expected"] or not unsafe_ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
