import argparse
from dataclasses import asdict
import fcntl
import json
import time

from core import CONSUMERBPENDING, Layer, Range, ZERO, now, save
from effects import UPDATE_QUERY
from run import (archive, branch_ref, check, coherent, context, persist,
                 successful)


def run(name, grant):
    directory, manifest, git, effects = context(name, grant, "native-repeat")
    if not name.startswith("staged-") or manifest["phase"] != "B-amended-awaiting-repeated-import":
        raise RuntimeError("Native repetition requires a completed staged B export")
    effects.guard.authorize("push")
    effects.guard.authorize("update-branch")
    exported = Range(**manifest["exported_B"])
    pending = git.commit("native-repeat-local-pending", exported.base,
                         {"workflow_case/consumer.py": CONSUMERBPENDING},
                         "Capitalize the pending item label")
    git.git("update-ref", "refs/heads/native-repeat-authoring", pending, ZERO)
    local = Range(exported.base, pending)
    incorporated = exported
    manifest.update(phase="native-repeat-in-progress",
                    native_repeat_input=asdict(local), native_rebase_operations=[])
    persist(directory, manifest)
    outputs = []
    for index in [1, 2]:
        label = "native-repeat-" + str(index)
        before = coherent(directory, manifest, effects, label + "-before", layers=["B"])
        previous_trunk = before["refs"][branch_ref(manifest, "trunk")]
        new_trunk = git.commit(label + "-trunk", previous_trunk,
                               {"workflow_case/trunk-progress.txt": "advance " + str(index) + "\n"},
                               "Advance the isolated trunk for native import " + str(index))
        effects.push(label + "-trunk-push", {branch_ref(manifest, "trunk"): new_trunk},
                     {branch_ref(manifest, "trunk"): previous_trunk})
        basis = coherent(directory, manifest, effects, label + "-basis", layers=["B"])
        selected = basis["refs"][branch_ref(manifest, "B")]
        payload = {"query": UPDATE_QUERY, "variables": {"input": {
            "pullRequestId": manifest["nodes"]["B"], "expectedHeadOid": selected,
            "updateMethod": "REBASE", "clientMutationId": manifest["prefix"] + "-" + label}}}
        receipt = effects.api(label + "-update", "POST", "graphql", payload, kind="update-branch")
        operation = {"kind": "generic-public-REBASE", "selected_pr": manifest["prs"]["B"],
                     "selected_head": selected, "request_label": label + "-update",
                     "response": receipt["data"], "suffix_settlement": "not established"}
        manifest["native_rebase_operations"].append(operation)
        persist(directory, manifest)
        observed = None
        for sample in range(20):
            candidate = effects.observe(label + "-after-" + str(sample))
            tip = candidate["refs"].get(branch_ref(manifest, "B"))
            pr = candidate["prs"]["B"]["rest"]
            if tip != selected and tip == pr["head"]["sha"]:
                observed = candidate
                break
            if receipt["http"] >= 400 or receipt["data"].get("errors"):
                break
            time.sleep(1)
        successful(receipt)
        if observed is None:
            effects.freeze(label, "No changed coherent native B input was observed")
            raise RuntimeError("Native B range remains unavailable; no mutation retry")
        effects.fetch(label + "-fetch", [branch_ref(manifest, "B"), branch_ref(manifest, "trunk")])
        tip = observed["refs"][branch_ref(manifest, "B")]
        check(manifest, label + " B targets the synthetic trunk",
              observed["prs"]["B"]["rest"]["base"]["ref"], manifest["branches"]["trunk"])
        check(manifest, label + " native head contains the exact advanced trunk",
              git.git("merge-base", new_trunk, tip), new_trunk)
        hosted = Range(new_trunk, tip)
        check(manifest, label + " own layer excludes trunk changes",
              git.changed_paths(hosted), ["workflow_case/consumer.py"])
        integrated = git.integrate(label + "-import", [Layer("B", incorporated, local, hosted)], new_trunk)
        accepted = Range(**integrated[0]["accepted_local"])
        git.behavior(label + "-accepted", accepted.tip, expected="APPLE:3 each", quantity=True)
        check(manifest, label + " local edit remains pending only in the consumer",
              git.changed_paths(Range(hosted.tip, accepted.tip)), ["workflow_case/consumer.py"])
        checkpoint = git.checkpoint(label, local.tip, accepted.tip,
                                    {"B": asdict(hosted)}, manifest["checkpoint"]["authored"],
                                    manifest["native_operations"] + manifest["native_rebase_operations"])
        outputs.append({"hosted": asdict(hosted), "accepted": asdict(accepted),
                        "checkpoint": checkpoint, "captured_observation": observed,
                        "native_commit": git.command("cat-file", "commit", tip).stdout})
        incorporated, local = hosted, accepted
        manifest.update(native_repeated_imports=outputs, incorporated_B=asdict(hosted),
                        local_B=asdict(accepted), checkpoint=checkpoint)
        persist(directory, manifest)
    retained = {archive(manifest, "A", 1): manifest["inputs"]["A0"],
                archive(manifest, "B", 1): manifest["inputs"]["B0"],
                archive(manifest, "B", 2): exported.tip,
                archive(manifest, "F", 1): manifest["F"]}
    if "source" in manifest["branches"]:
        retained[branch_ref(manifest, "source")] = exported.tip
        retained[branch_ref(manifest, "sourceF")] = manifest["F"]
    check(manifest, "Native-only imports create no authored archive",
          effects.remote_refs("native-repeat-archives", list(retained)), retained)
    inventory = effects.namespace_inventory("native-repeat-inventory")
    check(manifest, "Original captured pending source remains recoverable",
          git.git("rev-parse", "refs/heads/authoring"), manifest["inputs"]["Bprime"])
    final = effects.observe("native-repeat-final")
    check(manifest, "Canonical B node survives both native imports",
          final["prs"]["B"]["rest"]["node_id"], manifest["nodes"]["B"])
    check(manifest, "Canonical B prose survives both native imports",
          final["prs"]["B"]["rest"]["body"], manifest["initial_pr_bodies"]["B"])
    save(directory / "archive-history.json",
         {name: {**entry, **git.snapshot(Range(entry["base"], entry["tip"]))}
          for name, entry in manifest["authored_history"].items()}, exclusive=True)
    manifest.update(phase="staged-trace-complete-with-actual-native-repetition",
                    final_inventory=inventory)
    persist(directory, manifest)
    print(json.dumps({"case": name, "phase": manifest["phase"],
                      "native_imports": len(outputs), "utc": now()}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=["staged-private", "staged-public-f-only"])
    parser.add_argument("--grant", required=True)
    args = parser.parse_args()
    directory, _, _, _ = context(args.case)
    with (directory / "worker.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.case, args.grant)
