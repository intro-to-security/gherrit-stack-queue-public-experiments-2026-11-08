#!/usr/bin/python3
"""Record CLI Git calls and refuse pushes beyond one granted active-ref vector."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness


def validate_push(args, allowed):
    if "push" not in args:
        return False
    push = args[args.index("push") + 1:]
    if not push or push[0] != "origin" or "--atomic" not in push:
        raise ValueError("CLI push must target origin atomically")
    refspecs = [value for value in push[1:] if not value.startswith("-")]
    targets = set()
    for spec in refspecs:
        if spec.count(":") != 1:
            raise ValueError("CLI push must use fully qualified source/destination refs")
        source, target = spec.split(":")
        if source != target or target not in allowed:
            raise ValueError("CLI push escapes its active ref allocation")
        targets.add(target)
    leases = {}
    for value in push:
        if value.startswith("--force-with-lease="):
            ref, expected = value[len("--force-with-lease="):].split(":", 1)
            if not re.fullmatch("[0-9a-f]{40}", expected):
                raise ValueError("CLI lease must bind an existing exact head")
            leases[ref] = expected
        elif value.startswith("-") and value != "--atomic":
            raise ValueError("Unexpected CLI push option")
    if not targets or set(leases) != targets:
        raise ValueError("CLI push needs an exact lease for every active ref")
    return True


def main():
    args = sys.argv[1:]
    allowed = set(json.loads(os.environ["CAUSAL_SYNC_ALLOWED_REFS"]))
    name = os.environ["CAUSAL_SYNC_CASE"]
    try:
        pushing = validate_push(args, allowed)
        if pushing:
            # An exact duplicate or unsupported-option fallback cannot dispatch twice.
            harness.begin(name + "-cli-push-single-dispatch", {"kind": "push-gate", "args": args, "allowed": sorted(allowed)})
        label = name + "-cli-git-" + uuid.uuid4().hex[:12]
        record = harness.begin(label, {"kind": "cli-git", "args": args, "push": pushing})
        result = subprocess.run(["/usr/bin/git", "-c", "core.hooksPath=" + str(harness.HOOKS), *args], text=True, capture_output=True)
        record.update(end=harness.stamp(), exit=result.returncode)
        if pushing:
            record.update(stdout=result.stdout, stderr=result.stderr)
        harness.save(harness.EVIDENCE / (label + ".receipt.json"), record)
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        sys.exit(result.returncode)
    except Exception as error:
        sys.stderr.write("Causal Git gate refused dispatch: " + str(error) + "\n")
        sys.exit(93)


if __name__ == "__main__":
    main()
