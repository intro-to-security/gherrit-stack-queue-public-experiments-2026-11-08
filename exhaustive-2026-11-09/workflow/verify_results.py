"""Read-only final provider audit; retain local objects and check export custody."""

import argparse
import fcntl
import json
import re
import uuid

from core import Range, ZERO, now, save
from run import CASES, branch_ref, context


def object_ids(value):
    if isinstance(value, dict):
        return set().union(*(object_ids(v) for v in value.values()), set())
    if isinstance(value, list):
        return set().union(*(object_ids(v) for v in value), set())
    if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) and value != ZERO:
        return {value}
    return set()


def verify(name):
    directory, manifest, git, effects = context(name)
    checks = []

    def check(label, actual, expected):
        checks.append({"label": label, "actual": actual, "expected": expected,
                       "passed": actual == expected})

    label = "verification-" + uuid.uuid4().hex[:8]
    observation = effects.observe(label)
    inventory = effects.namespace_inventory(label + "-inventory")
    effects.fetch(label + "-fetch", list(inventory))
    check("Recorded experiment assertions", all(a["passed"] for a in manifest["assertions"]), True)
    for layer, node in manifest["nodes"].items():
        pr = observation["prs"][layer]["rest"]
        check(layer + " canonical node", pr["node_id"], node)
        check(layer + " canonical prose", pr["body"], manifest["initial_pr_bodies"][layer])
        check(layer + " PR head agrees with ref", pr["head"]["sha"],
              observation["refs"][branch_ref(manifest, layer)])
        expected_state = "closed" if name.startswith("staged-") and layer in {"A", "F"} else "open"
        check(layer + " expected final lifecycle", pr["state"], expected_state)
    if manifest.get("authored_history"):
        expected_archives = {entry["ref"]: entry["tip"] for entry in manifest["authored_history"].values()}
        actual_archives = {ref: oid for ref, oid in inventory.items() if ref.startswith("refs/tags/")}
        check("Exact archive vector with no native-only version", actual_archives, expected_archives)
        expected_sources = {branch_ref(manifest, key): manifest["exported_B"]["tip"]
                            if key == "source" else manifest["F"]
                            for key in ["source", "sourceF"] if key in manifest["branches"]}
        check("Exact public source vector", {ref: oid for ref, oid in inventory.items()
                                             if ref.endswith(("/author-source", "/F-only-source"))},
              expected_sources)
        check("Original full pending local source", git.git("rev-parse", "refs/heads/authoring"),
              manifest["inputs"]["Bprime"])
        check("Named original local source", git.git("rev-parse", "refs/heads/" + manifest["local_source_branch"]),
              manifest["inputs"]["Bprime"])

    checkpoints = {}
    relevant = object_ids(manifest) | set(inventory.values())
    for path in (directory / "checkpoints").glob("*.json"):
        if path.name.endswith(".intent.json"):
            continue
        value = json.loads(path.read_text())
        checkpoints[path.name] = value
        relevant |= object_ids(value)
        check(path.name + " exact durable intent", value,
              json.loads(path.with_name(path.stem + ".intent.json").read_text()))
        check(path.name + " exact continuation ref", git.git("rev-parse", value["continuation"]), value["result"])
    objects = {}
    for oid in sorted(relevant):
        kind = git.command("cat-file", "-t", oid, allowed=(0, 128))
        record = {"available": kind.returncode == 0, "type": kind.stdout.strip()}
        if kind.returncode == 0 and record["type"] == "commit":
            parents = git.git("rev-list", "--parents", "-n", "1", oid).split()[1:]
            record.update(raw_commit=git.command("cat-file", "commit", oid).stdout,
                          tree=git.tree(oid), parents=parents,
                          parent_patches={p: git.patch(Range(p, oid)) for p in parents})
        objects[oid] = record
    check("Every referenced local object retained", [oid for oid, row in objects.items() if not row["available"]], [])

    attempts = []
    for path in (directory / "evidence").glob("*.intent.json"):
        intent = json.loads(path.read_text())
        if intent["kind"] in {"read", "git-read"}:
            continue
        receipt = path.with_name(path.name.replace(".intent.json", ".receipt.json"))
        result = json.loads(receipt.read_text()) if receipt.exists() else None
        attempts.append({"label": path.name, "kind": intent["kind"],
                         "receipt": receipt.name if receipt.exists() else None,
                         "http": result.get("http") if result else None,
                         "exit": result.get("exit") if result else None,
                         "errors": result.get("data", {}).get("errors")
                                   if result and isinstance(result.get("data"), dict) else None})
    check("Every dispatched mutation has a retained receipt", [a["label"] for a in attempts if a["receipt"] is None], [])
    behavior = {}
    for path in (directory / "behavior").glob("*/result.json"):
        row = json.loads(path.read_text())
        passed = row["returncode"] != 0 if row["expected"] is None else (
            row["returncode"] == 0 and row["stdout"].strip() == row["expected"])
        behavior[path.parent.name] = row
        check("Behavior " + path.parent.name, passed, True)
    fsck = git.command("fsck", "--full", "--no-reflogs", allowed=(0, 1, 128))
    check("Git object graph integrity", fsck.returncode, 0)
    result = {"case": name, "utc": now(), "phase": manifest["phase"],
              "passed": all(row["passed"] for row in checks), "checks": checks,
              "experiment_assertion_count": len(manifest["assertions"]),
              "fresh_observation": observation, "namespace": inventory,
              "objects": objects, "checkpoints": checkpoints, "behaviors": behavior,
              "mutations": attempts,
              "freeze": json.loads((directory / "FREEZE.json").read_text())
                        if (directory / "FREEZE.json").exists() else None,
              "fsck": {"exit": fsck.returncode, "stdout": fsck.stdout, "stderr": fsck.stderr},
              "limit": "Fresh bounded readback and retained object evidence; no future-write exclusion or automatic retry."}
    output = directory / (label.upper() + ".json")
    save(output, result, exclusive=True)
    print(json.dumps({"case": name, "passed": result["passed"], "checks": len(checks),
                      "objects": len(objects), "report": str(output),
                      "failed": [row["label"] for row in checks if not row["passed"]]}))
    if not result["passed"]:
        raise RuntimeError("Final read-only verification found a mismatch")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=CASES)
    args = parser.parse_args()
    directory, _, _, _ = context(args.case)
    with (directory / "worker.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        verify(args.case)
