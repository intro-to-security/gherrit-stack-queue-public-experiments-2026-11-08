import fcntl
import hashlib
import json
import sys
import time
import harness as h

ROOT = h.ROOT
PREFIX = "exh-1109-target-profile002-e-"
REFS = [PREFIX + suffix for suffix in ("trunk", "A", "B")]
GRANT = ROOT.parent / "control" / "target-grant-002.json"
ORIGINAL_GUARD, ORIGINAL_BEGIN, ORIGINAL_STATE = h.guard, h.begin, h.state


def current():
    return h.read(ROOT / "followup-case.json")


def save_case(case):
    h.save(ROOT / "followup-case.json", case)


def verify():
    grant = h.read(GRANT)
    if grant.get("repository") != h.REPO or grant.get("case") != "explicit-types-contrast" or grant.get("exact_refs") != REFS or grant.get("max_new_refs") != 3 or grant.get("max_new_prs") != 2:
        raise ValueError("followup_grant_mismatch")
    manifest = h.read(ROOT / "FOLLOWUP-SOURCE.json")
    for name, expected in manifest["hashes"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError("followup_source_changed:" + name)
    if grant.get("source_sha256") != manifest["hashes"]["followup.py"]:
        raise ValueError("followup_source_not_granted")
    return manifest


def permitted(method, path, payload, case):
    base = "repos/" + h.REPO
    if method == "GET":
        return ORIGINAL_GUARD(method, path, payload, case)
    if method == "POST" and path == base + "/pulls" and (payload["head"], payload["base"]) in [(REFS[1], REFS[0]), (REFS[2], REFS[1])]:
        return
    if method == "POST" and path == base + "/stacks" and case is not None and payload == dict(pull_requests=[case["prs"]["A"], case["prs"]["B"]]):
        return
    raise ValueError("outside_fresh_followup_policy")


def guarded(method, path, payload, case=None):
    verify()
    return permitted(method, path, payload, case)


def exact_ref(name):
    verify()
    if name not in REFS:
        raise ValueError("outside_fresh_followup_refs")
    return name


def recorded_begin(label, record):
    manifest = verify()
    return ORIGINAL_BEGIN(label, dict(record, followup_source=manifest))


def install_boundary():
    h.guard, h.ref, h.begin = guarded, exact_ref, recorded_begin
    h.state = lambda name: current() if name == "e" else ORIGINAL_STATE(name)


def freeze():
    names = ["followup.py", "FOLLOWUP-PLAN.md", "minimal-ci.yml", "harness.py"]
    manifest = dict(hashes={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names},
                    case="explicit-types-contrast", refs=REFS, time=h.now())
    folder = ROOT / "followup-source" / str(time.time_ns())
    folder.mkdir(parents=True)
    for name in names:
        (folder / name).write_bytes((ROOT / name).read_bytes())
    manifest["snapshot"] = str(folder.relative_to(ROOT))
    h.save(folder / "manifest.json", manifest)
    h.save(ROOT / "FOLLOWUP-SOURCE.json", manifest)
    print(json.dumps(manifest))


def challenges():
    case = dict(prs=dict(A=101, B=102))
    base = "repos/" + h.REPO
    probes = [
        ("owned lower", "POST", base + "/pulls", dict(head=REFS[1], base=REFS[0]), True),
        ("owned upper", "POST", base + "/pulls", dict(head=REFS[2], base=REFS[1]), True),
        ("cross-fixture", "POST", base + "/pulls", dict(head=h.PREFIX + "f-B", base=REFS[1]), False),
        ("wrong adjacency", "POST", base + "/pulls", dict(head=REFS[2], base=REFS[0]), False),
        ("exact membership", "POST", base + "/stacks", dict(pull_requests=[101,102]), True),
        ("foreign membership", "POST", base + "/stacks", dict(pull_requests=[101,103]), False),
        ("reversed membership", "POST", base + "/stacks", dict(pull_requests=[102,101]), False),
        ("merge forbidden", "PUT", base + "/pulls/101/merge-async", {}, False),
        ("policy forbidden", "POST", base + "/rulesets", {}, False),
        ("production forbidden", "POST", "repos/joshlf/gherrit/pulls", dict(head=REFS[1], base=REFS[0]), False)]
    rows = []
    for label, method, path, payload, expected in probes:
        try:
            permitted(method, path, payload, case)
            actual = True
        except ValueError:
            actual = False
        rows.append(dict(label=label, expected=expected, actual=actual, passed=actual == expected))
    h.save(ROOT / "FOLLOWUP-GUARD-CHALLENGE.json", dict(rows=rows, network_effects=0))
    if not all(row["passed"] for row in rows):
        raise RuntimeError("followup_guard_challenge_failed")
    print(json.dumps(dict(passed=len(rows), total=len(rows), network_effects=0)))


def prepare():
    if (ROOT / "followup-case.json").exists():
        raise RuntimeError("followup_already_allocated_reconcile")
    h.initialize()
    template = (ROOT / "minimal-ci.yml").read_text()
    replacement = "  pull_request:\n    branches: [" + REFS[0] + "]\n    types: [opened, synchronize, reopened]\n"
    workflow = template.replace("  pull_request:\n", replacement, 1)
    witness = template.replace("  pull_request:\n", "  pull_request:\n    branches: [" + REFS[0] + "]\n    types: [stacked]\n", 1)
    witness = witness.replace("name: Target profile probe - minimal payload", "name: Stacked event witness - minimal payload").replace("name: Validate and Test", "name: Stacked event witness")
    files = {".github/workflows/ci.yml": workflow, ".github/workflows/witness.yml": witness,
             "fixture.txt": "Fresh explicit activity-type exclusion contrast\n"}
    trunk = h.commit("e-explicit-trunk", files)
    case = dict(name="e", trunk=REFS[0], trunk_sha=trunk, heads={}, prs={}, native=[], phase="local-prepared")
    updates = {"refs/heads/" + REFS[0]: trunk}
    parent = trunk
    for index, layer in enumerate("AB", 1):
        files = dict(files, **{layer + ".txt": "fresh layer " + layer + "\n"})
        sha = h.commit("e-explicit-" + layer, files, parent)
        case["heads"][layer] = dict(ref=REFS[index], sha=sha, files=files)
        updates["refs/heads/" + REFS[index]] = sha
        parent = sha
    save_case(case)
    if h.git("ls-remote", "origin", *updates).stdout.strip():
        raise RuntimeError("followup_namespace_occupied")
    h.push("e-explicit-initial-push", updates, {name:"" for name in updates})
    base = REFS[0]
    for layer, head in case["heads"].items():
        payload = dict(head=head["ref"], base=base, title="Target explicit-types contrast " + layer,
                       body="Fresh synthetic activity-type contrast with a separate positive stacked witness. Minimal payload only.\n\n" + h.NOTICE)
        response = h.require(h.api("e-explicit-create-" + layer, "POST", "repos/" + h.REPO + "/pulls", payload, case), [201])
        case["prs"][layer] = response["number"]
        save_case(case)
        base = head["ref"]
    case["phase"] = "open-before-membership"
    save_case(case)
    print(json.dumps(dict(prs=case["prs"])))


def observe():
    case = current()
    h.wait_ci("e", "explicit-before-membership", "A")
    h.logs("e", "explicit-before-membership")
    if case.get("stack"):
        raise RuntimeError("followup_already_registered")
    response = h.require(h.api("e-explicit-register", "POST", "repos/" + h.REPO + "/stacks", dict(pull_requests=[case["prs"]["A"],case["prs"]["B"]]), case), [201])
    case["stack"] = response["number"]
    save_case(case)
    deadline = time.monotonic() + 180
    number = 0
    while True:
        snapshot = h.observation("e", "explicit-after-" + str(number))
        checks = snapshot["prs"]["B"]["source_checks"]["check_runs"]
        ready = any(check["name"] == "Stacked event witness" and check["status"] == "completed" for check in checks)
        if ready or time.monotonic() >= deadline:
            break
        time.sleep(10)
        number += 1
    h.logs("e", "explicit-after-membership")
    h.save(ROOT / "FOLLOWUP-RESULT.json", dict(snapshot=snapshot, witness_completed=ready,
             validate_checks=[check for check in checks if check["name"] == "Validate and Test"],
             witness_checks=[check for check in checks if check["name"] == "Stacked event witness"],
             PRs_retained=True, refs_retained=True, policy_settings_created=0))
    case["phase"] = "observed-retained"
    save_case(case)
    print(json.dumps(dict(witness_completed=ready, upper_validate_checks=len([check for check in checks if check["name"] == "Validate and Test"]))))


if __name__ == "__main__":
    phase = sys.argv[1]
    if phase == "freeze":
        challenges()
        freeze()
    else:
        with (ROOT / "executor.lock").open("a+") as owner:
            fcntl.flock(owner, fcntl.LOCK_EX)
            verify()
            install_boundary()
            if phase == "prepare":
                prepare()
            elif phase == "observe":
                observe()
            else:
                raise ValueError("unknown_followup_phase")
