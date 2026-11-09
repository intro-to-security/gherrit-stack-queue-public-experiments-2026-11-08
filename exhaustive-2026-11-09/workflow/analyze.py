import argparse
import json
from pathlib import Path
import uuid

from core import Range, now, save
from run import branch_ref, context


def analyze(name):
    directory, manifest, git, effects = context(name)
    suffix = uuid.uuid4().hex[:8]
    refs = effects.remote_refs("analysis-refs-" + suffix,
                               [branch_ref(manifest, layer) for layer in manifest["branches"]])
    effects.fetch("analysis-fetch-" + suffix, list(refs))
    observations = []
    for path in sorted((directory / "evidence").glob("update-*.observation.json")):
        observations.append({"file": path.name, **json.loads(path.read_text())})
    relevant = set(refs.values())
    events = {}
    for observation in observations:
        relevant.update(observation["refs"].values())
        for value in observation["prs"].values():
            pr = value["graphql"].get("data", {}).get("repository", {}).get("pullRequest", {})
            for event in pr.get("timelineItems", {}).get("nodes", []):
                if event.get("id"):
                    events[event["id"]] = event
                for key in ["beforeCommit", "afterCommit"]:
                    if event.get(key):
                        relevant.add(event[key]["oid"])
    commits = {}
    for oid in sorted(relevant):
        raw = git.command("cat-file", "commit", oid, allowed=(0, 128))
        if raw.returncode:
            commits[oid] = {"object_available": False}
            continue
        parents = git.git("rev-list", "--parents", "-n", "1", oid).split()[1:]
        commits[oid] = {"object_available": True, "raw_commit": raw.stdout,
                        "tree": git.tree(oid), "parents": parents,
                        "files": git.git("ls-tree", "-r", "--name-only", oid).splitlines(),
                        "parent_patches": {parent: git.patch(Range(parent, oid)) for parent in parents}}
    basis = [row for row in observations if row["file"].startswith("update-basis-")]
    after = [row for row in observations if row["file"].startswith("update-after-")]
    differences = {}
    if basis and after:
        before, last = basis[-1], after[-1]
        for layer in manifest["prs"]:
            a = before["prs"][layer]["rest"]
            b = last["prs"][layer]["rest"]
            ref = branch_ref(manifest, layer)
            differences[layer] = {"before_ref": before["refs"].get(ref),
                                  "after_ref": last["refs"].get(ref),
                                  "head_changed": before["refs"].get(ref) != last["refs"].get(ref),
                                  "before_base": {k: a["base"][k] for k in ["ref", "sha"]},
                                  "after_base": {k: b["base"][k] for k in ["ref", "sha"]},
                                  "canonical_node_unchanged": a["node_id"] == b["node_id"]}
    result = {"case": name, "utc": now(), "phase": manifest["phase"],
              "prs": manifest["prs"], "native_group": manifest.get("stack"),
              "update_response": manifest.get("update_response"),
              "selected_head_before": manifest.get("selected_head_before"),
              "changes_after_mutation_basis": differences, "events": events,
              "current_refs": refs, "commits": commits,
              "observation_files": [row["file"] for row in observations],
              "limit": "Current and bounded observed state, not future-write exclusion; mutation response fields may lag refs."}
    save(directory / ("ANALYSIS-" + suffix + ".json"), result, exclusive=True)
    print(json.dumps({"case": name, "prs": manifest["prs"], "changes": differences,
                      "http": manifest.get("update_response", {}).get("http"),
                      "errors": manifest.get("update_response", {}).get("data", {}).get("errors"),
                      "analysis": "ANALYSIS-" + suffix + ".json"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("case")
    analyze(parser.parse_args().case)
