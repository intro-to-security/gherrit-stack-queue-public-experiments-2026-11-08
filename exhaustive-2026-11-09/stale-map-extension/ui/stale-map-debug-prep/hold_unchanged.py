"""Measure one held request while sampling only its seven unchanged refs."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture-held-fresh-prep"
SOURCE_SHA = "769b6e0348898e142b983f17d37ef3b07aa5220bb0a110edb1b5d6b57c4c5549"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(seconds):
    if not 420 <= seconds <= 900 or digest(FIXTURE / "fixture.py") != SOURCE_SHA:
        raise ValueError("Frozen source and bounded conservative hold required")
    if not (FIXTURE / "objects.git").is_dir():
        raise ValueError("Prepared owned Git store required")
    spec = importlib.util.spec_from_file_location("held_fixture", FIXTURE / "fixture.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ready = json.loads((FIXTURE / "READY.json").read_bytes())
    pause_path = HERE / "PAUSE-HELD-FRESH.json"
    pause = json.loads(pause_path.read_bytes())
    expected_map = {str(ready["prs"]["A"]): ready["commits"]["A2"], str(ready["prs"]["B"]): ready["commits"]["B0"]}
    if (pause.get("coordinator") != "root" or pause.get("prefix") != ready["prefix"]
            or pause.get("state") != "paused-before-dispatch"
            or pause.get("body") != {"expectedHeadOids": expected_map}):
        raise ValueError("Exact held fresh initiation required")
    output = HERE / "held-timer"
    output.mkdir(exist_ok=False)
    module.preserve(output / "START.json", {"at": module.stamp(), "seconds": seconds,
                    "source_sha256": digest(Path(__file__)), "ready_sha256": digest(FIXTURE / "READY.json"),
                    "pause_sha256": digest(pause_path), "authority": "Root-owned read-only timer; never resumes UI or writes remote refs"})
    lab = module.owned_lab(ready)
    clock_start = time.monotonic()
    samples = []
    for index, target in enumerate([0, seconds / 2, seconds]):
        while True:
            remaining = target - (time.monotonic() - clock_start)
            if remaining <= 0:
                break
            time.sleep(min(15, remaining))
        before = module.stamp()
        refs = module.current_refs(lab, ready, "held-unchanged-" + str(index))
        sample = {"index": index, "target_seconds": target, "before": before,
                  "after": module.stamp(), "elapsed_monotonic_seconds": time.monotonic() - clock_start,
                  "refs": refs, "matches": refs == ready["current_refs"]}
        module.preserve(output / ("sample-" + str(index) + ".json"), sample)
        if not sample["matches"]:
            raise ValueError("Ref changed during control; freeze before Resume")
        samples.append(sample)
        print(json.dumps({"sample": index, "elapsed": sample["elapsed_monotonic_seconds"], "seven_refs_unchanged": True}), flush=True)
    result = {"at": module.stamp(), "seconds_requested": seconds,
              "elapsed_monotonic_seconds": time.monotonic() - clock_start,
              "all_samples_match": True, "samples": samples,
              "limits": "Sampled unchanged vector, not a continuous ref lock. Root must reobserve the same paused request and actual body before one Resume."}
    module.preserve(output / "HOLD-VERIFIED.json", result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=420)
    main(parser.parse_args().seconds)
