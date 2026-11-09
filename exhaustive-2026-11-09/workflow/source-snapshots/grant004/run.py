from __future__ import annotations

import argparse
from dataclasses import asdict
import fcntl
import hashlib
import json
from pathlib import Path
import time
import uuid

from core import (CONSUMERB, CONSUMERBPENDING, Conflict, Git, Layer, MODELA,
                  Range, ZERO, now, save, staged_admission, staged_inputs)
from effects import Effects, NOTICE, REPO, ROOT, UPDATE_QUERY


CASES = ["staged-private", "staged-public-f-only", "gql-standalone",
         "gql-native-wrong", "gql-native-lower", "gql-native-upper",
         "gql-native-conflict"]


def context(name, grant=None, action=None):
    directory = ROOT / "cases" / name
    manifest = json.loads((directory / "case.json").read_text())
    git = Git(directory)
    effects = Effects(directory, git, manifest, grant, action)
    return directory, manifest, git, effects


def persist(directory, manifest):
    save(directory / "case.json", manifest)


def prepare(name):
    directory = ROOT / "cases" / name
    if (directory / "case.json").exists():
        return json.loads((directory / "case.json").read_text())
    prefix = "exh-1109-workflow-" + name + "-" + uuid.uuid4().hex[:8]
    git = Git(directory)
    branches = {"trunk": prefix + "/trunk", "A": prefix + "/A"}
    if name.startswith("staged"):
        inputs = staged_inputs(git)
        branches.update(B=prefix + "/B", F=prefix + "/F")
        if name == "staged-public-f-only":
            branches.update(source=prefix + "/author-source", sourceF=prefix + "/F-only-source")
        git.git("update-ref", "refs/heads/authoring", inputs["B0"], ZERO)
        git.git("update-ref", "refs/heads/" + prefix + "/author-source", inputs["B0"], ZERO)
    else:
        trunk = git.commit("trunk", None, {"gql.txt": "base\n"},
                           "Seed an isolated branch-update fixture")
        inputs = {"trunk": trunk}
        parent = trunk
        layers = ["A"] if name == "gql-standalone" else ["A", "B", "C"]
        for layer in layers:
            branches[layer] = prefix + "/" + layer
            files = {"gql_" + layer + ".txt": layer + "\n"}
            if name == "gql-native-conflict" and layer == "A":
                files["gql.txt"] = "selected branch\n"
            parent = git.commit(layer + "0", parent, files,
                                "Add isolated layer " + layer)
            inputs[layer + "0"] = parent
    manifest = {"case": name, "prefix": prefix, "repository": REPO,
                "created": now(), "branches": branches, "inputs": inputs,
                "prs": {}, "nodes": {}, "phase": "prepared-local-only",
                "native_operations": [], "assertions": []}
    if name.startswith("staged"):
        manifest["local_source_branch"] = prefix + "/author-source"
    manifest["planned_pr_bases"] = {"A": "trunk"}
    if "B" in branches:
        manifest["planned_pr_bases"]["B"] = "A"
    if "C" in branches:
        manifest["planned_pr_bases"]["C"] = "B"
    if "F" in branches:
        manifest["planned_pr_bases"]["F"] = "trunk"
    manifest["archives"] = ({key: archive(manifest, change, version)
                             for key, change, version in [("A1", "A", 1), ("B1", "B", 1),
                                                          ("F1", "F", 1), ("B2", "B", 2)]}
                            if name.startswith("staged") else {})
    save(directory / "case.json", manifest, exclusive=True)
    return manifest


def check(manifest, label, actual, expected):
    result = {"label": label, "actual": actual, "expected": expected,
              "passed": actual == expected}
    manifest["assertions"].append(result)
    if not result["passed"]:
        raise AssertionError(json.dumps(result))


def branch_ref(manifest, layer):
    return "refs/heads/" + manifest["branches"][layer]


def archive(manifest, change, version):
    return "refs/tags/gherrit/" + manifest["prefix"] + "-" + change + "/v" + str(version)


def successful(receipt):
    if receipt["http"] is None or receipt["http"] >= 400:
        raise RuntimeError("Request did not return a successful HTTP result")
    if isinstance(receipt["data"], dict) and receipt["data"].get("errors"):
        raise RuntimeError("GraphQL returned errors; fixture remains frozen")
    return receipt["data"]


def create_pr(directory, manifest, effects, layer, base):
    body = "Isolated synthetic " + manifest["case"] + " fixture, layer " + layer + ".\n\n" + NOTICE
    receipt = effects.api("create-pr-" + layer, "POST", "repos/" + REPO + "/pulls",
                          {"title": manifest["prefix"] + " " + layer,
                           "body": body, "head": manifest["branches"][layer],
                           "base": manifest["branches"][base], "draft": False},
                          kind="create-pr")
    result = successful(receipt)
    manifest["prs"][layer] = result["number"]
    manifest["nodes"][layer] = result["node_id"]
    manifest.setdefault("initial_pr_bodies", {})[layer] = body
    persist(directory, manifest)


def setup(name, grant):
    directory, manifest, git, effects = context(name, grant, "setup")
    if manifest["phase"] != "prepared-local-only":
        raise RuntimeError("Setup requires an untouched prepared fixture")
    layers = [key[:-1] for key in manifest["inputs"] if key.endswith("0")]
    updates = {branch_ref(manifest, "trunk"): manifest["inputs"]["trunk"]}
    updates.update({branch_ref(manifest, layer): manifest["inputs"][layer + "0"] for layer in layers})
    if name.startswith("staged"):
        updates.update({archive(manifest, layer, 1): manifest["inputs"][layer + "0"]
                        for layer in layers})
        if "source" in manifest["branches"]:
            updates[branch_ref(manifest, "source")] = manifest["inputs"]["B0"]
    before = effects.namespace_inventory("initial-absence")
    check(manifest, "Every allocated remote ref was absent", before, {})
    save(directory / "initial-publication.json", {"updates": updates,
                                                  "ranges": {"A": asdict(Range(manifest["inputs"]["trunk"], manifest["inputs"]["A0"])),
                                                             **({"B": asdict(Range(manifest["inputs"]["A0"], manifest["inputs"]["B0"]))} if "B0" in manifest["inputs"] else {})},
                                                  "source_export": "initial-full" if "source" in manifest["branches"] else "private"}, exclusive=True)
    effects.push("initial-push", updates, {ref: ZERO for ref in updates})
    check(manifest, "Initial exact ref vector", effects.remote_refs("initial-readback", list(updates)), updates)
    previous = "trunk"
    for layer in layers:
        create_pr(directory, manifest, effects, layer, previous)
        previous = layer
    if len(layers) >= 2:
        result = successful(effects.api("create-stack", "POST", "repos/" + REPO + "/stacks",
                                        {"pull_requests": list(manifest["prs"].values())}, kind="create-stack"))
        manifest["stack"] = result
    manifest["phase"] = "hosted-initial"
    manifest["initial_refs"] = updates
    if name.startswith("staged"):
        manifest["authored_history"] = {
            "A1": {"ref": archive(manifest, "A", 1),
                   **asdict(Range(manifest["inputs"]["trunk"], manifest["inputs"]["A0"]))},
            "B1": {"ref": archive(manifest, "B", 1),
                   **asdict(Range(manifest["inputs"]["A0"], manifest["inputs"]["B0"]))}}
    persist(directory, manifest)
    effects.observe("initial-state")
    return manifest


def coherent(directory, manifest, effects, label, *, layers=None):
    selected = list(layers or manifest["prs"])
    for index in range(20):
        observation = effects.observe(label + "-sample-" + str(index))
        matches = True
        for layer in selected:
            pr = observation["prs"][layer]["rest"]
            if pr["node_id"] != manifest["nodes"][layer]:
                raise RuntimeError("Canonical PR node identity changed")
            matches &= observation["refs"].get(branch_ref(manifest, layer)) == pr["head"]["sha"]
        if matches:
            check(manifest, label + " selected branches/PRs agree", matches, True)
            persist(directory, manifest)
            return observation
        manifest.setdefault("coherence_gaps", []).append({"label": label, "sample": index})
        persist(directory, manifest)
        time.sleep(1)
    raise RuntimeError("No coherent captured branch/PR input in bounded observation")


def merge(directory, manifest, effects, layer, label):
    observation = coherent(directory, manifest, effects, label + "-basis", layers=[layer])
    selected = observation["prs"][layer]["rest"]["head"]["sha"]
    path = "repos/" + REPO + "/pulls/" + str(manifest["prs"][layer]) + "/merge-async"
    receipt = effects.api(label + "-submit", "PUT", path,
                          {"merge_method": "squash", "merge_action": "direct_merge",
                           "sha": selected}, kind="merge")
    result = successful(receipt)
    operation = {"layer": layer, "selected_sha": selected,
                 "submission": label + "-submit", "result": result,
                 "suffix_settlement": "not established by this experiment"}
    manifest["native_operations"].append(operation)
    persist(directory, manifest)
    if result["status"] == "pending":
        token = result["details"]["uuid"]
        for index in range(60):
            result = successful(effects.api(label + "-poll-" + str(index), "GET", path + "/" + token))
            operation["result"] = result
            persist(directory, manifest)
            if result["status"] != "pending":
                break
            time.sleep(2)
    if result["status"] != "merged":
        effects.freeze(label, "Native request did not reach direct merged outcome")
        raise RuntimeError("Native merge did not complete; freeze fixture")
    after = effects.observe(label + "-terminal-state")
    check(manifest, layer + " lifecycle merged", after["prs"][layer]["rest"]["merged"], True)
    persist(directory, manifest)
    return after


def hosted_b_range(directory, manifest, git, effects, label):
    observed = None
    for index in range(20):
        candidate = effects.observe(label + "-sample-" + str(index))
        pr = candidate["prs"]["B"]["rest"]
        if (pr["node_id"] == manifest["nodes"]["B"] and
                pr["head"]["sha"] == candidate["refs"].get(branch_ref(manifest, "B")) and
                pr["base"]["ref"] == manifest["branches"]["trunk"]):
            observed = candidate
            break
        manifest.setdefault("coherence_gaps", []).append({"label": label, "sample": index})
        persist(directory, manifest)
        time.sleep(1)
    if observed is None:
        raise RuntimeError("No usable exact hosted B range in the bounded observation")
    effects.fetch(label + "-fetch", [branch_ref(manifest, "B"), branch_ref(manifest, "trunk")])
    tip = observed["refs"][branch_ref(manifest, "B")]
    parent = git.git("rev-parse", tip + "^")
    check(manifest, label + " hosted own patch is only the consumer",
          git.changed_paths(Range(parent, tip)), ["workflow_case/consumer.py"])
    return Range(parent, tip), observed["refs"][branch_ref(manifest, "trunk")], observed


def stage_f(name, grant):
    directory, manifest, git, effects = context(name, grant, "stage-f")
    if manifest["phase"] not in {"hosted-initial", "old-A-merged-awaiting-import"}:
        raise RuntimeError("F stage requires initial publication")
    if not manifest.get("local_edits_captured"):
        inputs = manifest["inputs"]
        save(directory / "local-edits-after-publication.json",
             {"utc": now(), "source_ref": "refs/heads/" + manifest["local_source_branch"],
              "before": inputs["B0"], "after": inputs["Bprime"],
              "A_local_range": asdict(Range(inputs["trunk"], inputs["Aprime"])),
              "B_local_range": asdict(Range(inputs["Aprime"], inputs["Bprime"])),
              "initial_publication_receipt": "initial-push.receipt.json"}, exclusive=True)
        git.git("update-ref", "refs/heads/authoring", inputs["Bprime"], inputs["B0"])
        git.git("update-ref", "refs/heads/" + manifest["local_source_branch"],
                inputs["Bprime"], inputs["B0"])
        manifest["local_edits_captured"] = True
        persist(directory, manifest)
    if manifest["phase"] == "hosted-initial":
        merge(directory, manifest, effects, "A", "land-old-A")
        manifest["phase"] = "old-A-merged-awaiting-import"
        persist(directory, manifest)
    hosted, trunk, observation = hosted_b_range(directory, manifest, git, effects, "first-import-basis")
    inputs = manifest["inputs"]
    f_merge = git.merge("F-pending-delta", inputs["A0"], trunk, inputs["Aprime"])
    f = git.commit_tree("F-authored", trunk, git.tree(f_merge),
                        "Add a unit to the item model\n\nAgent-authored-by: AI agent acting on joshlf's behalf\n")
    result = git.integrate("first-import", [Layer("B", Range(inputs["A0"], inputs["B0"]),
                                                Range(inputs["Aprime"], inputs["Bprime"]), hosted)], f)
    local = Range(**result[0]["accepted_local"])
    independent = git.behavior("F-independent", f, expected="apple", quantity=True)
    git.behavior("F-B-dependent", local.tip, expected="apple:3 each", quantity=True)
    without_f = git.merge("B-without-F", local.base, trunk, local.tip)
    git.behavior("B-without-F-negative", without_f, expected=None, quantity=True)
    check(manifest, "F owns only the pending model delta", git.changed_paths(Range(trunk, f)), ["workflow_case/model.py"])
    check(manifest, "B owns only its consumer amendment", git.changed_paths(local), ["workflow_case/consumer.py"])
    checkpoint = git.checkpoint("after-old-A", inputs["Bprime"], local.tip,
                                {"B": asdict(hosted)},
                                {"A": asdict(Range(inputs["trunk"], inputs["A0"])),
                                 "B": asdict(Range(inputs["A0"], inputs["B0"]))},
                                manifest["native_operations"])
    manifest.update(F=f, first_import=result, checkpoint=checkpoint,
                    incorporated_B=asdict(hosted), local_B=asdict(local),
                    landed_A_trunk=trunk)
    admission = staged_admission(independently_landable=independent["returncode"] == 0,
                                 joint_review_required=False,
                                 public_source_tip=f if "sourceF" in manifest["branches"] else None,
                                 followup_tip=f)
    check(manifest, "Explicit F-only staging admission", admission["accepted"], True)
    save(directory / "F-only-accepted-intent.json",
         {"publish": ["F"], "defer": ["B"], "full_pending_source": inputs["Bprime"],
          "accepted_continuation": local.tip, "source_export": "F-only" if "sourceF" in manifest["branches"] else "private",
          "admission": admission,
          "older_native_operations_retained": manifest["native_operations"],
          "scope_limit": "Fresh F refs/PR are disjoint from old A/B suffix targets; this does not clear later B's overlap gate."}, exclusive=True)
    updates = {branch_ref(manifest, "F"): f, archive(manifest, "F", 1): f}
    if "sourceF" in manifest["branches"]:
        updates[branch_ref(manifest, "sourceF")] = f
    check(manifest, "F-only refs were absent", effects.remote_refs("F-absence", list(updates)), {})
    effects.push("F-only-push", updates, {ref: ZERO for ref in updates})
    check(manifest, "F-only exact ref vector", effects.remote_refs("F-readback", list(updates)), updates)
    manifest["authored_history"]["F1"] = {"ref": archive(manifest, "F", 1), **asdict(Range(trunk, f))}
    persist(directory, manifest)
    unchanged = {branch_ref(manifest, "B"): hosted.tip, archive(manifest, "B", 1): inputs["B0"]}
    if "source" in manifest["branches"]:
        unchanged[branch_ref(manifest, "source")] = inputs["B0"]
    check(manifest, "F-only publication leaves B and prior source alone",
          effects.remote_refs("F-custody-readback", list(unchanged)), unchanged)
    create_pr(directory, manifest, effects, "F", "trunk")
    manifest["phase"] = "F-only-published"
    persist(directory, manifest)
    return manifest


def repeated_hosted_control(name, grant):
    directory, manifest, git, effects = context(name, grant, "repeat-hosted-control")
    if manifest["phase"] != "B-amended-awaiting-repeated-import":
        raise RuntimeError("Repeated import requires the confirmed B v2 export")
    exported = Range(**manifest["exported_B"])
    pending = git.commit("repeat-pending-B", exported.base,
                         {"workflow_case/consumer.py": CONSUMERBPENDING},
                         "Capitalize the item label in the pending consumer")
    git.git("update-ref", "refs/heads/repeated-authoring", pending, ZERO)
    save(directory / "repeat-producer.json",
         {"producer": "ordinary Git synthetic collaborator control",
          "not_native_rebase_evidence": True,
          "pending_local": asdict(Range(exported.base, pending)),
          "native_operations_retained": manifest["native_operations"]}, exclusive=True)
    local = Range(exported.base, pending)
    incorporated = exported
    remote_head = exported.tip
    results = []
    for index, text in [(1, "hosted one\n"), (2, "hosted two\n")]:
        hosted_tip = git.commit("repeat-hosted-" + str(index), remote_head,
                                {"workflow_case/review.txt": text},
                                "Record hosted review adjustment " + str(index))
        effects.push("repeat-hosted-push-" + str(index),
                     {branch_ref(manifest, "B"): hosted_tip},
                     {branch_ref(manifest, "B"): remote_head})
        observation = coherent(directory, manifest, effects,
                               "repeat-hosted-" + str(index), layers=["B"])
        check(manifest, "Hosted adjustment visible " + str(index),
              observation["refs"][branch_ref(manifest, "B")], hosted_tip)
        effects.fetch("repeat-fetch-" + str(index), [branch_ref(manifest, "B")])
        hosted = Range(exported.base, hosted_tip)
        result = git.integrate("repeat-" + str(index), [Layer("B", incorporated, local, hosted)], exported.base)
        accepted = Range(**result[0]["accepted_local"])
        git.behavior("repeat-" + str(index), accepted.tip, expected="APPLE:3 each", quantity=True)
        check(manifest, "Imported current hosted adjustment " + str(index),
              git.git("show", accepted.tip + ":workflow_case/review.txt"), text.strip())
        check(manifest, "Only the pending consumer remains unsubmitted " + str(index),
              git.changed_paths(Range(hosted_tip, accepted.tip)), ["workflow_case/consumer.py"])
        checkpoint = git.checkpoint("repeat-" + str(index), local.tip, accepted.tip,
                                    {"B": asdict(hosted)},
                                    {**manifest["checkpoint"]["authored"], "B": asdict(exported)},
                                    manifest["native_operations"])
        results.append({"hosted": asdict(hosted), "accepted": asdict(accepted),
                        "checkpoint": checkpoint})
        if index == 2:
            try:
                git.integrate("wrong-repeated-baseline", [Layer("B", exported, local, hosted)], exported.base)
            except Conflict:
                check(manifest, "Using old authored export as repeated baseline conflicts", True, True)
            else:
                check(manifest, "Using old authored export as repeated baseline conflicts", False, True)
        incorporated, local, remote_head = hosted, accepted, hosted_tip
        manifest["repeated_imports"] = results
        persist(directory, manifest)
    retained = {archive(manifest, "A", 1): manifest["inputs"]["A0"],
                archive(manifest, "B", 1): manifest["inputs"]["B0"],
                archive(manifest, "B", 2): exported.tip,
                archive(manifest, "F", 1): manifest["F"]}
    if "source" in manifest["branches"]:
        retained[branch_ref(manifest, "source")] = exported.tip
        retained[branch_ref(manifest, "sourceF")] = manifest["F"]
    check(manifest, "Authored archives and public source targets stay exact",
          effects.remote_refs("final-retained-refs", list(retained)), retained)
    inventory = effects.namespace_inventory("final-namespace-inventory")
    actual_source_refs = sorted(ref for ref in inventory if "source" in ref)
    planned_source_refs = sorted(branch_ref(manifest, name) for name in ["source", "sourceF"]
                                 if name in manifest["branches"])
    check(manifest, "Actual private/public source-ref scope", actual_source_refs, planned_source_refs)
    check(manifest, "Original full pending source remains local and exact",
          git.git("rev-parse", "refs/heads/authoring"), manifest["inputs"]["Bprime"])
    check(manifest, "Canonical B review identity retained",
          effects.observe("final-state")["prs"]["B"]["rest"]["node_id"], manifest["nodes"]["B"])
    final_pr = effects.api("final-B-prose", "GET", "repos/" + REPO + "/pulls/" + str(manifest["prs"]["B"]))["data"]
    check(manifest, "Canonical B prose was not rewritten", final_pr["body"], manifest["initial_pr_bodies"]["B"])
    save(directory / "archive-history.json",
         {name: {**entry, **git.snapshot(Range(entry["base"], entry["tip"]))}
          for name, entry in manifest["authored_history"].items()}, exclusive=True)
    manifest.update(phase="staged-trace-complete-with-labeled-hosted-control",
                    incorporated_B=asdict(incorporated), local_B=asdict(local),
                    checkpoint=results[-1]["checkpoint"], final_inventory=inventory)
    persist(directory, manifest)
    return manifest


def amend_b(name, grant):
    directory, manifest, git, effects = context(name, grant, "amend-b")
    if manifest["phase"] != "F-only-published":
        raise RuntimeError("B amendment requires a separately published F")
    merge(directory, manifest, effects, "F", "land-F")
    hosted, trunk, _ = hosted_b_range(directory, manifest, git, effects, "after-F-basis")
    result = git.integrate("after-F-import", [Layer("B", Range(**manifest["incorporated_B"]),
                                                  Range(**manifest["local_B"]), hosted)], trunk)
    local = Range(**result[0]["accepted_local"])
    git.behavior("after-F-import", local.tip, expected="apple:3 each", quantity=True)
    check(manifest, "After F, B owns no model changes", git.changed_paths(local), ["workflow_case/consumer.py"])
    checkpoint = git.checkpoint("after-F", manifest["checkpoint"]["result"], local.tip,
                                {"B": asdict(hosted)}, manifest["checkpoint"]["authored"],
                                manifest["native_operations"])
    updates = {branch_ref(manifest, "B"): local.tip, archive(manifest, "B", 2): local.tip}
    expected = {branch_ref(manifest, "B"): hosted.tip, archive(manifest, "B", 2): ZERO}
    if "source" in manifest["branches"]:
        updates[branch_ref(manifest, "source")] = local.tip
        expected[branch_ref(manifest, "source")] = manifest["inputs"]["B0"]
    save(directory / "B-amendment-accepted-intent.json",
         {"updates": updates, "expected": expected, "canonical_pr": manifest["prs"]["B"],
          "captured_local": asdict(local), "incorporated_hosted": asdict(hosted),
          "experimental_overlap": True, "older_native_scope_not_cleared": manifest["native_operations"]}, exclusive=True)
    effects.push("B-v2-push", updates, expected)
    check(manifest, "Canonical B v2 exact publication", effects.remote_refs("B-v2-readback", list(updates)), updates)
    final = coherent(directory, manifest, effects, "after-B-v2", layers=["B"])
    check(manifest, "Canonical B review remains open", final["prs"]["B"]["rest"]["state"], "open")
    manifest["authored_history"]["B2"] = {"ref": archive(manifest, "B", 2), **asdict(local)}
    export_checkpoint = git.checkpoint("B-v2-confirmed-export", local.tip, local.tip,
                                       {"B": asdict(local)},
                                       {**checkpoint["authored"], "B": asdict(local),
                                        "F": asdict(Range(manifest["landed_A_trunk"], manifest["F"]))},
                                       manifest["native_operations"])
    manifest.update(phase="B-amended-awaiting-repeated-import", Bv2=local.tip,
                    incorporated_B=asdict(local), local_B=asdict(local), checkpoint=export_checkpoint)
    manifest["exported_B"] = asdict(local)
    persist(directory, manifest)
    return manifest


def gql_probe(name, grant):
    directory, manifest, git, effects = context(name, grant, "gql-probe")
    if manifest["phase"] != "hosted-initial":
        raise RuntimeError("GraphQL probe requires an untouched hosted fixture")
    target = "B" if name == "gql-native-upper" else "A"
    moved = "A" if target == "B" else "trunk"
    old = manifest["inputs"][moved + "0"] if moved == "A" else manifest["inputs"]["trunk"]
    updates = {"gql_advance.txt": "new parent state\n"}
    if name == "gql-native-conflict":
        updates = {"gql.txt": "new trunk conflict\n"}
    advanced = git.commit("advance-parent", old, updates, "Advance the selected update branch's parent")
    effects.push("advance-parent", {branch_ref(manifest, moved): advanced}, {branch_ref(manifest, moved): old})
    basis = coherent(directory, manifest, effects, "update-basis", layers=[target])
    selected = basis["prs"][target]["rest"]["head"]["sha"]
    expected = ZERO if name == "gql-native-wrong" else selected
    payload = {"query": UPDATE_QUERY, "variables": {"input": {
        "pullRequestId": manifest["nodes"][target], "expectedHeadOid": expected,
        "updateMethod": "REBASE", "clientMutationId": manifest["prefix"] + "-once"}}}
    response = effects.api("update-branch-once", "POST", "graphql", payload, kind="update-branch")
    manifest["update_response"] = response
    manifest["update_target"] = target
    manifest["selected_head_before"] = selected
    persist(directory, manifest)
    offsets = [0, 2, 10, 30, 60]
    start = time.monotonic()
    observations = []
    for index, offset in enumerate(offsets):
        delay = offset - (time.monotonic() - start)
        if delay > 0:
            time.sleep(delay)
        observations.append(effects.observe("update-after-" + str(index)))
    manifest["update_observations"] = ["update-after-" + str(i) for i in range(len(observations))]
    manifest["phase"] = "update-observed-no-retry"
    persist(directory, manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "setup", "stage-f", "amend-b", "repeat-hosted-control", "gql-probe", "observe"])
    parser.add_argument("case", choices=CASES)
    parser.add_argument("--grant")
    args = parser.parse_args()
    directory = ROOT / "cases" / args.case
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "worker.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.action == "prepare":
            result = prepare(args.case)
        elif args.action == "setup":
            result = setup(args.case, args.grant)
        elif args.action == "stage-f":
            result = stage_f(args.case, args.grant)
        elif args.action == "amend-b":
            result = amend_b(args.case, args.grant)
        elif args.action == "gql-probe":
            result = gql_probe(args.case, args.grant)
        elif args.action == "repeat-hosted-control":
            result = repeated_hosted_control(args.case, args.grant)
        else:
            _, _, _, effects = context(args.case)
            result = effects.observe("manual-observation-" + uuid.uuid4().hex[:8])
        print(json.dumps({"case": args.case, "phase": result.get("phase"),
                          "prefix": result.get("prefix"), "utc": now()}))


if __name__ == "__main__":
    main()
