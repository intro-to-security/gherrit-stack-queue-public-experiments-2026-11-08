from dataclasses import asdict
import json
from pathlib import Path
import uuid

from core import (CONSUMERBPENDING, Conflict, Git, Layer, Range, TRAILER, ZERO,
                  now, save, staged_admission, staged_inputs)


ROOT = Path(__file__).resolve().parent


def run():
    directory = ROOT / "local-controls" / uuid.uuid4().hex[:10]
    git = Git(directory)
    inputs = staged_inputs(git)
    checks = []

    def equal(label, actual, expected):
        checks.append({"label": label, "actual": actual, "expected": expected,
                       "passed": actual == expected})
        if actual != expected:
            raise AssertionError(label)

    landed = git.commit_tree("observed-A-landed", inputs["trunk"],
                             git.tree(inputs["A0"]), "Land old A in the local model\n\n" + TRAILER + "\n")
    hosted_b = git.commit_tree("observed-B-rebased", landed, git.tree(inputs["B0"]),
                              git.message(inputs["B0"]))
    f_delta = git.merge("followup-delta", inputs["A0"], landed, inputs["Aprime"])
    f = git.commit_tree("followup-F", landed, git.tree(f_delta),
                        "Add a unit to the item model\n\n" + TRAILER + "\n")
    hosted = Range(landed, hosted_b)
    result = git.integrate("first", [Layer("B", Range(inputs["A0"], inputs["B0"]),
                                           Range(inputs["Aprime"], inputs["Bprime"]), hosted)], f)
    first = Range(**result[0]["accepted_local"])
    git.behavior("F-independent", f, expected="apple", quantity=True)
    git.behavior("dependent-result", first.tip, expected="apple:3 each", quantity=True)
    missing_f = git.merge("B-alone", first.base, landed, first.tip)
    git.behavior("B-without-F", missing_f, expected=None, quantity=True)
    equal("F model-only patch", git.changed_paths(Range(landed, f)), ["workflow_case/model.py"])
    equal("B consumer-only patch", git.changed_paths(first), ["workflow_case/consumer.py"])
    old_operations = [{"id": "retained-older-native-intent", "suffix_settlement": "unknown"}]
    checkpoint = git.checkpoint("first", inputs["Bprime"], first.tip,
                                {"B": asdict(hosted)},
                                {"B": asdict(Range(inputs["A0"], inputs["B0"]))},
                                old_operations)
    equal("Authored submission differs from accepted result",
          checkpoint["authored"]["B"]["tip"] == checkpoint["result"], False)
    equal("Incorporated hosted range differs from pending local range",
          checkpoint["incorporated"]["B"]["tip"] == checkpoint["result"], False)
    equal("Old native intent is retained", checkpoint["old_operations"], old_operations)

    local_pending = git.commit("pending-local-B", first.base,
                               {"workflow_case/consumer.py": CONSUMERBPENDING},
                               "Capitalize the item label in the pending consumer")
    hosted_one = git.commit("hosted-one", first.tip,
                            {"workflow_case/review.txt": "hosted one\n"},
                            "Record the first hosted review adjustment")
    # A confirmed export establishes first as the next hosted baseline here.
    imported_one = git.integrate("repeat-one", [Layer("B", first,
        Range(first.base, local_pending), Range(first.base, hosted_one))], first.base)
    accepted_one = Range(**imported_one[0]["accepted_local"])
    git.behavior("repeat-one", accepted_one.tip, expected="APPLE:3 each", quantity=True)
    hosted_two = git.commit("hosted-two", hosted_one,
                            {"workflow_case/review.txt": "hosted two\n"},
                            "Record the second hosted review adjustment")
    imported_two = git.integrate("repeat-two", [Layer("B", Range(first.base, hosted_one),
        accepted_one, Range(first.base, hosted_two))], first.base)
    accepted_two = Range(**imported_two[0]["accepted_local"])
    git.behavior("repeat-two", accepted_two.tip, expected="APPLE:3 each", quantity=True)
    equal("New hosted adjustment imported", git.git("show", accepted_two.tip + ":workflow_case/review.txt"), "hosted two")
    equal("Only local consumer edit stays pending",
          git.changed_paths(Range(hosted_two, accepted_two.tip)), ["workflow_case/consumer.py"])
    try:
        git.integrate("wrong-old-export-baseline", [Layer("B", first,
            accepted_one, Range(first.base, hosted_two))], first.base)
    except Conflict:
        equal("Wrong repeated-import baseline conflicts", True, True)
    else:
        equal("Wrong repeated-import baseline conflicts", False, True)

    broken_model = git.workload(f)["model.py"].replace("self.name = name", "self.label = name")
    inseparable = git.commit("inseparable-F", landed,
                             {"workflow_case/model.py": broken_model},
                             "Rename the item label before its dependent consumer")
    git.behavior("inseparable-F-negative", inseparable, expected=None, quantity=True)
    proposals = {
        "private": staged_admission(independently_landable=True, joint_review_required=False,
                                     public_source_tip=None, followup_tip=f),
        "public-F-only": staged_admission(independently_landable=True, joint_review_required=False,
                                           public_source_tip=f, followup_tip=f),
        "full-public-source": staged_admission(independently_landable=True, joint_review_required=False,
                                              public_source_tip=first.tip, followup_tip=f),
        "inseparable": staged_admission(independently_landable=False, joint_review_required=False,
                                        public_source_tip=None, followup_tip=inseparable),
        "joint-review": staged_admission(independently_landable=True, joint_review_required=True,
                                        public_source_tip=f, followup_tip=f),
    }
    for name, accepted in [("private", True), ("public-F-only", True),
                           ("full-public-source", False), ("inseparable", False),
                           ("joint-review", False)]:
        equal("Staging admission " + name, proposals[name]["accepted"], accepted)
    equal("Full pending source remains recoverable",
          git.git("rev-parse", "refs/inputs/Bprime"), inputs["Bprime"])
    equal("Hosted network mutation functions absent from local Git object",
          any(hasattr(git, method) for method in ["push", "fetch", "api"]), False)
    integrity = git.command("fsck", "--full", "--no-reflogs")
    equal("Retained object integrity", integrity.returncode, 0)
    report = {"kind": "local-only-control", "utc": now(), "directory": str(directory),
              "inputs": inputs, "F": f, "accepted_first": asdict(first),
              "accepted_second": asdict(accepted_two), "proposals": proposals,
              "checks": checks, "passed": all(row["passed"] for row in checks),
              "provider_behavior_simulated": True, "hosted_mutations": 0,
              "limit": "Local range/import/admission evidence; not native ordering or human workflow evidence."}
    save(directory / "RESULTS.json", report, exclusive=True)
    save(ROOT / "local-controls-latest.json", {"directory": str(directory), "passed": report["passed"]})
    print(json.dumps({"directory": str(directory), "passed": report["passed"], "checks": len(checks)}))


if __name__ == "__main__":
    run()
