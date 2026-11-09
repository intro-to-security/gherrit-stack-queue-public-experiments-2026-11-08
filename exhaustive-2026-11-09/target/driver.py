import fcntl
import json
import sys
import time
import harness as h


def main(phase):
    with (h.ROOT / "executor.lock").open("a+") as owner:
        fcntl.flock(owner, fcntl.LOCK_EX)
        if phase == "freeze":
            print(json.dumps(h.freeze_source()))
            return
        h.verify_source()
        if phase == "prepare":
            for name in h.SPECS:
                h.fixture(name)
                print(json.dumps(dict(prepared=name)), flush=True)
        elif phase == "protect":
            h.protect()
        elif phase == "open":
            for name in h.SPECS:
                case = h.create_prs(name)
                print(json.dumps(dict(name=name, prs=case["prs"])), flush=True)
        elif phase == "initial":
            for name in h.SPECS:
                h.wait_ci(name, "initial-" + name, "A" if name in "fp" else "AB")
                h.logs(name, "initial-" + name)
                print(json.dumps(dict(initial_observed=name)), flush=True)
        elif phase == "register":
            for name in "ufmr":
                h.register(name)
            time.sleep(45)
            for name in "ufmr":
                h.observation(name, "post-membership-" + name)
                h.logs(name, "post-membership-" + name)
        elif phase == "amend-u":
            h.amend("u", "B", "u-same-order-amendment")
            h.wait_ci("u", "amended-u", "AB")
            h.logs("u", "amended-u")
        elif phase == "merge-controls":
            for name in "mru":
                result = h.request_merge(name, name + "-direct-method")
                print(json.dumps(dict(name=name, outcome=result.get("terminal"))), flush=True)
                h.observation(name, "after-method-" + name)
            h.wait_ci("u", "rewritten-u", "B")
            h.logs("u", "rewritten-u")
        elif phase == "producer":
            case = h.state("p")
            payload = dict(state="success", context="Validate and Test", description="Synthetic user-producer negative control; no software test claim")
            h.require(h.api("p-user-status", "POST", "repos/" + h.REPO + "/statuses/" + case["heads"]["A"]["sha"], payload, case), [201])
            h.observation("p", "p-wrong-producer")
            first = h.request_merge("p", "p-wrong-producer-merge")
            print(json.dumps(dict(stage="wrong-producer", outcome=first.get("terminal"))), flush=True)
            fresh = h.pr(h.state("p"), "A")
            if fresh["state"] != "open" or first.get("terminal") is None:
                raise RuntimeError("cannot_continue_P_after_unexpected_or_unknown_lifecycle")
            h.amend("p", "A", "p-required-context-pass")
            h.wait_ci("p", "p-required-green", "A")
            h.logs("p", "p-required-green")
            h.amend("p", "A", "p-current-head-fails", fail=True)
            h.wait_ci("p", "p-current-fails", "A")
            h.logs("p", "p-current-fails")
            second = h.request_merge("p", "p-stale-green-merge")
            print(json.dumps(dict(stage="current-fails", outcome=second.get("terminal"))), flush=True)
            h.observation("p", "p-after-stale-control")
        elif phase == "finish":
            for name in h.SPECS:
                h.observation(name, "final-" + name)
                h.logs(name, "final-" + name)
            h.cleanup()
        else:
            raise ValueError("unknown_phase")
        print(json.dumps(dict(completed_phase=phase)), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
