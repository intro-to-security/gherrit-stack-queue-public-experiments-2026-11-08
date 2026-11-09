import argparse
import fcntl
import json
import time

from core import Range, now, save
from effects import UPDATE_QUERY
from run import branch_ref, check, coherent, context, persist, successful


CASE = "gql-native-lower"


def membership(observation):
    value = observation["prs"]["A"]["graphql"]["data"]["repository"]["pullRequest"]["stack"]
    if value is None or value["entries"]["pageInfo"]["hasNextPage"]:
        raise RuntimeError("Native membership is unavailable or incomplete")
    return {"id": value["id"], "number": value["number"], "size": value["size"],
            "base": value["baseRefName"],
            "members": [(entry["position"], entry["pullRequest"]["number"], entry["pullRequest"]["id"])
                        for entry in value["entries"]["nodes"]]}


def run(grant):
    directory, manifest, git, effects = context(CASE, grant, "cascade-followup")
    if manifest["phase"] != "update-observed-no-retry" or (directory / "FREEZE.json").exists():
        raise RuntimeError("Cascade needs the successful, unfrozen lower fixture")
    effects.guard.authorize("update-branch")
    before = coherent(directory, manifest, effects, "cascade-initial", layers=["A", "B", "C"])
    original_membership = membership(before)
    manifest.update(phase="cascade-followup-in-progress", cascade_requests=[], cascade_outputs=[])
    persist(directory, manifest)
    for layer, parent in [("B", "A"), ("C", "B")]:
        label = "cascade-" + layer
        basis = coherent(directory, manifest, effects, label + "-basis", layers=[layer, parent])
        check(manifest, label + " membership before request", membership(basis), original_membership)
        selected = basis["refs"][branch_ref(manifest, layer)]
        parent_tip = basis["refs"][branch_ref(manifest, parent)]
        already_current = git.command("merge-base", "--is-ancestor", parent_tip, selected,
                                       allowed=(0, 1, 128)).returncode == 0
        payload = {"query": UPDATE_QUERY, "variables": {"input": {
            "pullRequestId": manifest["nodes"][layer], "expectedHeadOid": selected,
            "updateMethod": "REBASE", "clientMutationId": manifest["prefix"] + "-" + label}}}
        try:
            receipt = effects.api(label + "-once", "POST", "graphql", payload, kind="update-branch")
        except Exception as error:
            manifest.update(phase="cascade-followup-limited",
                            cascade_limit={"layer": layer, "reason": str(error),
                                           "disposition": "request outcome unavailable; no next request"})
            persist(directory, manifest)
            raise
        manifest["cascade_requests"].append({"layer": layer, "selected": selected,
                                              "parent_tip": parent_tip, "receipt": receipt})
        persist(directory, manifest)
        observed = None
        for sample in range(20):
            candidate = effects.observe(label + "-after-" + str(sample))
            tip = candidate["refs"].get(branch_ref(manifest, layer))
            if tip == candidate["prs"][layer]["rest"]["head"]["sha"] and (tip != selected or already_current):
                observed = candidate
                break
            if receipt["http"] >= 400 or receipt["data"].get("errors"):
                break
            time.sleep(1)
        if receipt["http"] >= 400 or receipt["data"].get("errors") or observed is None:
            manifest.update(phase="cascade-followup-limited",
                            cascade_limit={"layer": layer, "disposition": "response refused or usable updated range unavailable; no next request"})
            persist(directory, manifest)
            if not (directory / "FREEZE.json").exists():
                effects.freeze(label, "No usable cascade result; no next member request")
            successful(receipt)
            raise RuntimeError("Cascade range unavailable")
        effects.fetch(label + "-fetch", [branch_ref(manifest, layer), branch_ref(manifest, parent)])
        tip = observed["refs"][branch_ref(manifest, layer)]
        check(manifest, label + " contains captured parent",
              git.git("merge-base", parent_tip, tip), parent_tip)
        check(manifest, label + " contains only its own layer delta",
              git.changed_paths(Range(parent_tip, tip)), ["gql_" + layer + ".txt"])
        check(manifest, label + " preserves membership/order", membership(observed), original_membership)
        check(manifest, label + " preserves open canonical review",
              observed["prs"][layer]["rest"]["state"], "open")
        manifest["cascade_outputs"].append({"layer": layer, "before": selected, "after": tip,
                                            "parent_tip": parent_tip, "already_current_before_request": already_current,
                                            "raw_commit": git.command("cat-file", "commit", tip).stdout,
                                            "patch": git.patch(Range(parent_tip, tip)),
                                            "observation": observed})
        persist(directory, manifest)
    final = coherent(directory, manifest, effects, "cascade-final", layers=["A", "B", "C"])
    refs = final["refs"]
    for parent, child in [("A", "B"), ("B", "C")]:
        check(manifest, "Final ancestry " + parent + " before " + child,
              git.git("merge-base", refs[branch_ref(manifest, parent)], refs[branch_ref(manifest, child)]),
              refs[branch_ref(manifest, parent)])
    manifest["phase"] = "cascade-followup-complete"
    save(directory / "CASCADE-RESULT.json",
         {"utc": now(), "requests": manifest["cascade_requests"],
          "outputs": manifest["cascade_outputs"], "membership": original_membership,
          "final": final, "limits": "Two separate guarded requests and observed composition; no all-stack transaction or future-write fence."}, exclusive=True)
    persist(directory, manifest)
    print(json.dumps({"case": CASE, "phase": manifest["phase"],
                      "requested_members": [row["layer"] for row in manifest["cascade_requests"]]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grant", required=True)
    args = parser.parse_args()
    directory, _, _, _ = context(CASE)
    with (directory / "worker.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.grant)
