import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
import protocol as p

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / str(time.time_ns())
ROWS = []
CHECKS = []


def check(name, actual, expected):
    row = dict(name=name, actual=actual, expected=expected, passed=actual == expected)
    CHECKS.append(row)
    if not row["passed"]:
        raise AssertionError(json.dumps(row))


def case(identity, title, function):
    start = len(CHECKS)
    try:
        details = function()
        row = dict(id=identity, title=title, disposition="performed", status="passed", details=details)
    except Exception as error:
        row = dict(id=identity, title=title, disposition="performed", status="harness-or-candidate-failure",
                   error=str(error), traceback=traceback.format_exc())
    row["checks"] = CHECKS[start:]
    ROWS.append(row)
    p.write(RUN / (identity + ".json"), row)
    print(json.dumps(dict(id=identity, status=row["status"], checks=len(row["checks"]))), flush=True)


def fixture(name):
    directory = RUN / name
    directory.mkdir()
    git = p.Git(directory / "repo", initialize=True)
    old = git.commit("old-input", {"x": "0\n", "z": "0\n"})
    result = git.commit("accepted-intent", {"x": "1\n", "z": "0\n"}, old)
    git.run("update-ref", "refs/retained/input", old)
    git.run("update-ref", "refs/retained/result", result)
    git.run("update-ref", "refs/heads/authoring", result)
    provider = directory / "provider"
    provider.mkdir()
    shutil.copytree(git.root, provider / "repo")
    remote = p.Git(provider / "repo")
    remote.run("update-ref", "refs/heads/A", old)
    p.write(provider / "state.json", dict(requests=[], receipts=[]))
    intent = dict(id="op-" + name, input=old, result=result,
                  continuation="refs/retained/completed-" + name,
                  expected=old, provider=str(provider),
                  binding=dict(repository="local-fixture", change="A", head="A", review=1),
                  captured_checkpoint=dict(incorporated=old, accepted_local=result),
                  scope=["head:A", "archive:" + name])
    authority = directory / "authority.json"
    p.write(authority, dict(owner=str(directory.resolve()), token="epoch-1", mode="native"))
    p.write(directory / "authority-link.json", dict(path=str(authority)))
    p.write(directory / "manifest.json", dict(id=intent["id"], digest=p.digest(intent)))
    p.write(directory / "operation.json", dict(intent=intent, state="planned"))
    p.write(directory / "bindings.json", intent["binding"])
    p.write(directory / "original-checkpoint.json", intent["captured_checkpoint"])
    return directory, intent, git


def invoke(directory, intent, token="epoch-1", **kwargs):
    return p.worker(directory, intent["id"], token, **kwargs)


def provider(directory):
    intent = p.read(directory / "operation.json")["intent"]
    return p.read(Path(intent["provider"]) / "state.json")


def drift_cases():
    directory, intent, git = fixture("late-reversal")
    old, confirmed = intent["input"], intent["result"]
    ordinary = git.merge("ordinary-late-reversal", confirmed, confirmed, old)
    check("ordinary importer silently removes confirmed x=1", git.files(ordinary)["x"], "0\n")
    gate = p.drift_decision(git, confirmed, confirmed, old, True)
    check("candidate requires a decision before incorporation", gate["status"], "needs_explicit_drift_review")
    restored = p.drift_decision(git, confirmed, confirmed, old, True, "restore", old, "restore-late", intent_paths=["x"])
    check("restoration exact tree", git.files(restored["proposed"]), {"x": "1\n", "z": "0\n"})
    effect = dict(kind="same-order-head-amendment", scope=["head:A"])
    pending = [dict(id="older-native-request", input=old, scope=["head:A"], prefix_outcome="lower_landed_suffix_open")]
    strict = p.admit_effect("strict", effect, pending)
    check("strict overlap control", strict["status"], "refused")
    return dict(input=old, confirmed=confirmed, ordinary=ordinary, restored=restored,
                authored_archive=confirmed, incorporated_before_review=confirmed,
                old_operation_unchanged=p.read(directory / "operation.json"), strict_admission=strict,
                costs=dict(temporarily_wrong_hosted_state=True, drift_review_decisions=1,
                           restoration_publications=1, detection_requires_connected_observation=True))


def legitimate_edits():
    directory, intent, git = fixture("legitimate-edits")
    old, confirmed = intent["input"], intent["result"]
    legitimate = git.commit("late-with-independent-remote-edit", {"x": "0\n", "z": "2\n"}, old)
    proposal = p.drift_decision(git, confirmed, confirmed, legitimate, True, "restore", old, "independent-restoration", intent_paths=["x"])
    check("reviewed restoration preserves independent legitimate edit", git.files(proposal["proposed"]), {"x": "1\n", "z": "2\n"})
    conflicting = git.commit("legitimate-conflicting-remote-edit", {"x": "2\n", "z": "0\n"}, old)
    conflict = p.drift_decision(git, confirmed, confirmed, conflicting, True, "restore", old, "conflicting-restoration", intent_paths=["x"])
    check("conflicting restoration cannot be accepted", conflict["status"], "conflict")
    accepted = p.drift_decision(git, confirmed, confirmed, conflicting, True, "accept_remote")
    check("explicit remote acceptance changes current intent", git.files(accepted["proposed"])["x"], "2\n")
    check("authored archive remains original submitted x=1", git.files(confirmed)["x"], "1\n")
    check("blind latest-tree restoration loses legitimate z=2", git.files(confirmed)["z"] != git.files(legitimate)["z"], True)
    return dict(independent=proposal, conflicting=conflict, explicit_remote_acceptance=accepted,
                decision_cost="one per changed observation; same-line conflicts require content resolution",
                attribution="No inference whether edit is legitimate or an old native effect")


def repetition():
    directory, intent, git = fixture("repetition")
    old = intent["input"]
    authored = []
    decisions = []
    for n, value in enumerate(["1\n", "2\n", "1\n"], 1):
        tip = git.commit("submission-v" + str(n), {"x": value, "z": "0\n"}, old)
        git.run("update-ref", "refs/archives/v" + str(n), tip, p.ZERO)
        authored.append(tip)
        gate = p.drift_decision(git, tip, tip, old, True)
        decisions.append(gate)
        restore = p.drift_decision(git, tip, tip, old, True, "restore", old, "repeat-restoration-" + str(n), intent_paths=["x"])
        check("round current intent survives late reversal " + str(n), git.files(restore["proposed"])["x"], value)
    check("A/B/A keeps separate exact archived positions", len(set(authored)), 3)
    current = git.commit("author-moved-after-capture", {"x": "1\n", "z": "3\n"}, authored[-1])
    no_op = p.drift_decision(git, authored[-1], authored[-1], authored[-1], True, label="noop")
    check("no-op output exact tree", git.tree(no_op["proposed"]), git.tree(authored[-1]))
    check("no-op creates no fourth archive", len(git.run("for-each-ref", "--format=%(refname)", "refs/archives/").stdout.splitlines()), 3)
    check("later current source remains pending relative to captured export", git.files(current)["z"], "3\n")
    reset = git.commit("explicit-reset-to-old-value", {"x": "0\n", "z": "0\n"}, old)
    v1 = git.merge("v1-reset-restoration-loses-intent", old, reset, authored[0])
    check("first candidate clean restoration violates accepted reset", git.files(v1)["x"], "1\n")
    guarded = p.drift_decision(git, reset, reset, authored[0], True, "restore", old, "guarded-reset-restoration", intent_paths=["x"])
    check("revised guard detects clean but intent-losing proposal", guarded["status"], "needs_explicit_path_resolution")
    explicit = p.drift_decision(git, reset, reset, authored[0], True, "restore_paths", old, "explicit-reset-resolution", intent_paths=["x"])
    check("explicit path choice preserves accepted reset", git.files(explicit["proposed"])["x"], "0\n")
    return dict(authored=authored, current=current, incorporated=authored[-1], accepted_intent=authored[-1],
                drift_decisions=3, no_op=no_op, scratch_commit_identity_is_not_submission_identity=True,
                candidate_v1_failure=dict(proposed=v1, intended=reset, actual_x="1", intended_x="0"),
                revised_candidate=guarded, explicit_resolution=explicit)


def layers():
    directory = RUN / "layer-import"
    directory.mkdir()
    git = p.Git(directory / "repo", initialize=True)
    trunk = git.commit("trunk", {"trunk": "0\n"})
    a = git.commit("A-incorporated", {"trunk": "0\n", "a": "0\n"}, trunk)
    b = git.commit("B-incorporated", {"trunk": "0\n", "a": "0\n", "b": "0\n"}, a)
    al = git.commit("A-local", {"trunk": "0\n", "a": "1\n"}, trunk)
    bl = git.commit("B-local", {"trunk": "0\n", "a": "1\n", "b": "1\n"}, al)
    t1 = git.commit("new-trunk", {"trunk": "2\n"}, trunk)
    ah = git.commit("A-hosted", {"trunk": "2\n", "a": "0\n", "remote-a": "yes\n"}, t1)
    bh = git.commit("B-hosted", {"trunk": "2\n", "a": "0\n", "remote-a": "yes\n", "b": "0\n", "remote-b": "yes\n"}, ah)
    output = t1
    results = []
    for name, ib, it, lb, lt, hb, ht in [("A", trunk, a, trunk, al, t1, ah), ("B", a, b, al, bl, ah, bh)]:
        ni = git.merge(name + "-normalize-incorporated", ib, hb, it)
        nl = git.merge(name + "-normalize-local", lb, hb, lt)
        integrated = git.merge(name + "-integrated", ni, nl, ht)
        replay = git.merge(name + "-replayed", hb, output, integrated)
        message = git.run("cat-file", "commit", lt).stdout.split("\n\n", 1)[1]
        accepted = git.commit_tree(name + "-accepted", git.tree(replay), output, message)
        changed = git.run("diff", "--name-only", output, accepted).stdout.splitlines()
        check(name + " layer ownership", changed, ["a", "remote-a"] if name == "A" else ["b", "remote-b"])
        check(name + " message bytes", git.run("cat-file", "commit", accepted).stdout.split("\n\n", 1)[1], message)
        results.append(dict(change=name, incorporated=dict(base=hb, tip=ht), accepted=accepted, changed=changed))
        output = accepted
    check("cumulative independently specified tree", git.files(output), {"trunk": "2\n", "a": "1\n", "b": "1\n", "remote-a": "yes\n", "remote-b": "yes\n"})
    return dict(results=results, bounds="Two linear one-commit layers; net trees and tip message only")


def observations():
    directory, intent, git = fixture("observation-limits")
    old, latest = intent["input"], intent["result"]
    observations = [dict(pr_head=latest, git_head=old), dict(pr_head=latest, git_head=latest), dict(pr_head=old, git_head=old)]
    statuses = []
    for observed in observations:
        status = "incoherent_no_checkpoint" if observed["pr_head"] != observed["git_head"] else p.drift_decision(git, latest, latest, observed["git_head"], True)["status"]
        statuses.append(status)
    check("incoherent observation does not advance baseline", statuses[0], "incoherent_no_checkpoint")
    check("stale coherent read can miss actual late write", statuses[1], "ordinary_proposal")
    check("fresh coherent reversal triggers review", statuses[2], "needs_explicit_drift_review")
    remote = p.Git(directory / "provider" / "repo")
    remote.run("update-ref", "refs/heads/A", latest, old)
    remote.run("update-ref", "refs/heads/A", old, latest)
    push = git.run("push", "--porcelain", "--force-with-lease=refs/heads/A:" + old,
                   str(remote.root), latest + ":refs/heads/A")
    check("actual Git explicit lease admits ABA-returned value", remote.ref("refs/heads/A"), latest)
    return dict(observations=observations, statuses=statuses, actual_latest=old,
                push_stdout=push.stdout, aba_unobserved=True,
                bound="Finite reads detect present disagreement, not all transient states or origin")


def explore():
    initial = (1, 1, 1, False, 1, False, 0)
    frontier = {initial: ()}
    seen = {initial}
    transitions = 0
    witnesses = {}
    for depth in range(7):
        following = {}
        for state, trace in frontier.items():
            intent, remote, observed, review, incorporated, legitimate, publications = state
            events = []
            if publications < 3 and not review:
                for value in (1, 2):
                    events.append(("publish-" + str(value), (value, value, observed, False, value, False, publications + 1)))
            events += [("old-effect-0", (intent, 0, observed, review, incorporated, False, publications)),
                       ("legitimate-edit-2", (intent, 2, observed, review, incorporated, True, publications)),
                       ("observe-current", (intent, remote, remote, remote != incorporated, incorporated, legitimate, publications)),
                       ("observe-stale", (intent, remote, incorporated, False, incorporated, legitimate, publications)),
                       ("crash-recover", state)]
            if review:
                events.append(("accept-remote", (observed, remote, observed, False, observed, legitimate, publications)))
                if not legitimate:
                    events.append(("reviewed-restore", (intent, intent, intent, False, intent, False, publications)))
                elif intent != remote:
                    witnesses.setdefault("blind_restore_loses_legitimate_edit", trace + ("blind-restore",))
            if remote != incorporated and not review:
                witnesses.setdefault("drift_not_yet_observed", trace)
            for event, new in events:
                transitions += 1
                if event.startswith("observe"):
                    check_intent = new[0] == intent
                    if not check_intent:
                        raise AssertionError("observation consumed confirmed intent")
                    if event == "observe-current" and remote != incorporated and not new[3]:
                        raise AssertionError("fresh observed drift accepted without review")
                if event == "observe-current" and remote != intent and incorporated == intent:
                    witnesses.setdefault("ordinary_import_silent_loss", trace + (event, "ordinary-import"))
                if new not in seen:
                    seen.add(new)
                    following[new] = trace + (event,)
        frontier = following
    check("ordinary-import mutant witness exists", "ordinary_import_silent_loss" in witnesses, True)
    check("blind-restore mutant witness exists", "blind_restore_loses_legitimate_edit" in witnesses, True)
    check("unobserved drift limit witnessed", "drift_not_yet_observed" in witnesses, True)
    return dict(depth=7, states=len(seen), transitions=transitions, witnesses=witnesses,
                dimensions="intent/remote/observed values 0,1,2; pending old input 0; up to 3 publications; one layer",
                invariant="Observation and crash preserve accepted intent; current coherent drift requires review",
                excluded="Provider ordering guarantee, arbitrary Git content, lifecycle, uncooperative writers, human decisions")


def structural():
    directory, intent, git = fixture("structural-witness")
    old_b = intent["result"]
    new_base = git.commit("new-C-base-contains-old-B", {"x": "1\n", "z": "0\n", "c": "yes\n"}, old_b)
    ancestor = git.run("merge-base", "--is-ancestor", old_b, new_base, allowed=(0, 1)).returncode == 0
    check("old canonical B commits become reachable from proposed base", ancestor, True)
    pending = [dict(id="old-B-C", input=old_b, scope=["head:B", "head:C"], prefix_outcome="lower_landed_suffix_open")]
    for kind in ["reorder", "landing"]:
        result = p.admit_effect("weaker", dict(kind=kind, scope=["head:B"]), pending, True)
        check("candidate excludes overlapping " + kind, result["status"], "refused")
    return dict(git_ancestry_witness=True, canonical_terminalization="provider-dependent consequence documented elsewhere; not observed here",
                recovery_cost="If allowed, replacement review/follow-up can be necessary; restoring bytes cannot reopen a merged PR")


def start(directory, intent, selected=None):
    stdout = (directory / ("child-" + str(time.time_ns()) + ".stdout")).open("w")
    stderr = (directory / ("child-" + str(time.time_ns()) + ".stderr")).open("w")
    args = [sys.executable, str(ROOT / "protocol.py"), str(directory), intent["id"], "epoch-1"]
    if selected:
        args.append(selected)
    process = subprocess.Popen(args, env=p.ENV, stdout=stdout, stderr=stderr)
    return process, stdout, stderr


def finish(child):
    process, stdout, stderr = child
    code = process.wait(timeout=15)
    stdout.close()
    stderr.close()
    return code


def concurrency():
    directory, intent, git = fixture("concurrent-workers")
    cached = p.read(directory / "operation.json")
    first, second = start(directory, intent), start(directory, intent)
    exits = [finish(first), finish(second)]
    check("both cooperating entry points complete", exits, [0, 0])
    check("simultaneous workers send one provider request", len(provider(directory)["requests"]), 1)
    check("stale cached planned invocation reloads complete under owner", cached["state"], "planned")
    result = invoke(directory, intent)
    check("stale direct invocation remains complete", result["status"], "complete")
    check("stale direct invocation does not resend", len(provider(directory)["requests"]), 1)
    return dict(exits=exits, requests=provider(directory)["requests"], cached_ignored=cached,
                bound="One authoritative local filesystem lock and cooperating entry points; no cross-host fence")


def interruptions():
    prefixes = ["validated", "marked", "request_logged", "provider_head", "provider_archive", "provider_receipt", "acknowledged", "result_ref", "result_checkpoint", "complete"]
    rows = []
    for prefix in prefixes:
        directory, intent, git = fixture("kill-" + prefix)
        child = start(directory, intent, prefix)
        deadline = time.monotonic() + 15
        marker = directory / "paused.json"
        while not marker.exists():
            if child[0].poll() is not None or time.monotonic() > deadline:
                child[0].kill()
                finish(child)
                raise RuntimeError("pause not reached " + prefix)
            time.sleep(.01)
        child[0].kill()
        killed = finish(child)
        check("real SIGKILL " + prefix, killed, -9)
        before = len(provider(directory)["requests"])
        first = invoke(directory, intent, reconcile=True)
        second = invoke(directory, intent, reconcile=True)
        complete = prefix in ["validated", "provider_receipt", "acknowledged", "result_ref", "result_checkpoint", "complete"]
        expected = "complete" if complete else "blocked_unknown_no_resend"
        check("prefix recovery disposition " + prefix, first["status"], expected)
        check("repeat recovery disposition " + prefix, second["status"], expected)
        check("prefix no duplicated provider request " + prefix, len(provider(directory)["requests"]), 1 if prefix == "validated" else before)
        if complete:
            p.validate(directory, intent["id"], "epoch-1")
            check("exact retained completed ref " + prefix, git.ref(intent["continuation"]), intent["result"])
        row = dict(prefix=prefix, killed=killed, marker=p.read(marker), before_requests=before,
                   first=first, second=second, final_operation=p.read(directory / "operation.json"),
                   actual_provider_head=p.Git(directory / "provider" / "repo").ref("refs/heads/A"),
                   provider=provider(directory))
        p.write(directory / "interruption.json", row)
        rows.append(row)
    return dict(prefixes=rows, power_loss_claim=False)


def damage():
    rows = []
    for name in ["missing-operation", "missing-manifest", "missing-authority-link", "malformed-operation", "foreign-id", "changed-intent", "missing-original-checkpoint", "wrong-result-checkpoint", "missing-result-checkpoint", "missing-result-ref", "wrong-result-ref", "missing-retained-input", "missing-result-object", "wrong-receipt", "wrong-binding"]:
        directory, intent, git = fixture("damage-" + name)
        check("prepare completed fixture " + name, invoke(directory, intent)["status"], "complete")
        operation = p.read(directory / "operation.json")
        if name == "missing-operation": (directory / "operation.json").unlink()
        elif name == "missing-manifest": (directory / "manifest.json").unlink()
        elif name == "missing-authority-link": (directory / "authority-link.json").unlink()
        elif name == "malformed-operation": (directory / "operation.json").write_text('{"state":')
        elif name == "foreign-id":
            operation["intent"]["id"] = "foreign"
            p.write(directory / "operation.json", operation)
        elif name == "changed-intent":
            operation["intent"]["result"] = intent["input"]
            p.write(directory / "operation.json", operation)
        elif name == "missing-original-checkpoint": (directory / "original-checkpoint.json").unlink()
        elif name == "wrong-result-checkpoint": p.write(directory / "result-checkpoint.json", {"result": intent["input"]})
        elif name == "missing-result-checkpoint": (directory / "result-checkpoint.json").unlink()
        elif name == "missing-result-ref": git.run("update-ref", "-d", intent["continuation"])
        elif name == "wrong-result-ref": git.run("update-ref", intent["continuation"], intent["input"])
        elif name == "missing-retained-input": git.run("update-ref", "-d", "refs/retained/input")
        elif name == "missing-result-object": (git.root / ".git" / "objects" / intent["result"][:2] / intent["result"][2:]).unlink()
        elif name == "wrong-receipt":
            operation["receipt"]["id"] = "foreign"
            p.write(directory / "operation.json", operation)
        elif name == "wrong-binding": p.write(directory / "bindings.json", {"review": 999})
        before = len(p.read(directory / "provider" / "state.json")["requests"])
        result = invoke(directory, intent, reconcile=True)
        check("direct completed recovery refuses damaged evidence " + name, result["status"], "refused")
        check("damaged record never dispatches " + name, len(p.read(directory / "provider" / "state.json")["requests"]), before)
        rows.append(dict(name=name, result=result))
    directory, intent, git = fixture("ordinary-authoring")
    check("complete before normal authoring", invoke(directory, intent)["status"], "complete")
    current = git.commit("ordinary-amendment", {"x": "4\n", "z": "0\n"}, intent["input"])
    git.run("update-ref", "refs/heads/authoring", current)
    check("later authoring does not invalidate retained completion", invoke(directory, intent)["status"], "complete")
    check("later authoring branch remains unchanged by recovery", git.ref("refs/heads/authoring"), current)
    return dict(damage=rows, current_authoring=current, retained_result=intent["result"])


def partial():
    directory, intent, git = fixture("partial-provider")
    result = invoke(directory, intent, effect="partial")
    check("partial outcome remains unknown", result["status"], "unknown_partial")
    remote = p.Git(directory / "provider" / "repo")
    check("actual head changed", remote.ref("refs/heads/A"), intent["result"])
    check("actual archive absent", remote.ref("refs/archives/" + intent["id"]), "")
    check("matching head alone does not complete", invoke(directory, intent, reconcile=True)["status"], "blocked_unknown_no_resend")
    check("partial outcome no duplicate request", len(provider(directory)["requests"]), 1)
    return dict(result=result, provider=provider(directory), state=p.read(directory / "operation.json"),
                missing_archive=True, scope="Injected separate effects; not evidence that Git atomic push is partial")


def local_acceptance():
    directory, intent, git = fixture("local-while-pending")
    invoke(directory, intent, effect="partial")
    old = p.read(directory / "operation.json")
    new_local = git.commit("fresh-local-successor", {"x": "1\n", "z": "7\n"}, intent["input"])
    git.run("update-ref", "refs/retained/local-successor", new_local, p.ZERO)
    p.write(directory / "successor-checkpoint.json", dict(result=new_local, incorporated=intent["result"], predecessor=intent["result"]))
    check("fresh local acceptance retains old frozen pending input", p.read(directory / "operation.json"), old)
    check("local successor does not settle old request", invoke(directory, intent, reconcile=True)["status"], "blocked_unknown_no_resend")
    check("local successor retained exact", git.ref("refs/retained/local-successor"), new_local)
    return dict(old=old, successor=p.read(directory / "successor-checkpoint.json"),
                strict_hosted_authority=False, weaker_authority="requires separately accepted exact new request, never inherited from local acceptance")


def transfer():
    directory, intent, git = fixture("transfer-source")
    invoke(directory, intent, effect="partial")
    destination = RUN / "transfer-destination"
    shutil.copytree(directory, destination)
    old_authority = directory / "authority.json"
    p.write(old_authority, dict(owner=str(destination.resolve()), token="epoch-2", mode="native"))
    check("stale source custody blocked", invoke(directory, intent)["reason"], "stale_custody")
    check("new owner preserves unresolved outcome without resend", invoke(destination, intent, token="epoch-2", reconcile=True)["status"], "blocked_unknown_no_resend")
    check("transfer exact original checkpoint", p.read(destination / "original-checkpoint.json"), intent["captured_checkpoint"])
    check("transfer frozen operation input", p.read(destination / "operation.json")["intent"], intent)
    check("transfer provider request count", len(provider(directory)["requests"]), 1)
    remote = Path(intent["provider"]) / "repo"
    base = dict(directory=destination, identity=intent["id"], token="epoch-2", destination=remote,
                api_repository="local-fixture", adopted_heads={"refs/heads/A": intent["result"]}, archives={}, legacy_records=[])
    admissions = []
    for name, changed in [("wrong-api-repository", dict(api_repository="other-repository")),
                          ("wrong-git-destination", dict(destination=destination / "repo")),
                          ("occupied-without-adoption", dict(adopted_heads={})),
                          ("stale-adoption-value", dict(adopted_heads={"refs/heads/A": intent["input"]})),
                          ("unknown-old-writer", dict(legacy_records=[dict(id="old-cascade", state="unknown")])),
                          ("lost-archive-history", dict(archives={"refs/archives/missing": intent["input"]})),
                          ("full-custody", {})]:
        result = p.admit_migration(**dict(base, **changed))
        check("adoption outcome " + name, result["status"], "enrolled" if name == "full-custody" else "refused")
        check("adoption has no new mutation authority " + name, result["mutation_authority"], False)
        admissions.append(dict(name=name, result=result))
    bindings_only = RUN / "bindings-only"
    bindings_only.mkdir()
    shutil.copyfile(destination / "bindings.json", bindings_only / "bindings.json")
    result = p.admit_migration(**dict(base, directory=bindings_only))
    check("bindings-only directory cannot adopt custody", result["status"], "refused")
    admissions.append(dict(name="bindings-only", result=result))
    return dict(destination=str(destination), provider=provider(directory), admissions=admissions,
                bound="Same-host stable authority path; cross-host transfer still needs quiescence and coordinated authority handoff")


def rollback():
    directory, intent, git = fixture("rollback")
    invoke(directory, intent, effect="partial")
    pending = p.read(directory / "operation.json")["state"] != "complete"
    check("rollback cannot enable old publisher while native outcome unresolved", not pending, False)
    settled, settled_intent, settled_git = fixture("rollback-settled")
    check("settle owned fixture", invoke(settled, settled_intent)["status"], "complete")
    p.validate(settled, settled_intent["id"], "epoch-1")
    bundle = settled / "retained-export.bundle"
    settled_git.run("bundle", "create", str(bundle), "--all")
    verify = settled_git.run("bundle", "verify", str(bundle))
    before = settled_git.ref("refs/retained/result")
    exported = dict(binding=p.read(settled / "bindings.json"), operation=p.read(settled / "operation.json"), checkpoint=p.read(settled / "result-checkpoint.json"), bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest())
    p.write(settled / "rollback-export.json", exported)
    p.write(settled / "authority.json", dict(owner=str(settled.resolve()), token="legacy-epoch-2", mode="legacy-export-only"))
    check("old native worker invalid after deliberate handoff", invoke(settled, settled_intent)["reason"], "stale_custody")
    check("rollback preserves exact retained result", settled_git.ref("refs/retained/result"), before)
    return dict(export=exported, bundle_verify=verify.stderr,
                bound="Local export/handoff rehearsal; not production enrollment or proof legacy Actions are excluded")


def persistence():
    outcomes = []
    for prefix in ["temp-write", "temp-fsync", "rename", "directory-fsync"]:
        durable = {"old", "new"} if prefix == "rename" else {"new"} if prefix == "directory-fsync" else {"old"}
        outcomes.append(dict(prefix=prefix, modeled_recovered_generations=sorted(durable),
                             assumption="temp file fsync orders data; directory fsync orders rename; prior old record durable"))
    check("model never accepts torn JSON as completion", all(set(r["modeled_recovered_generations"]) <= {"old", "new"} for r in outcomes), True)
    return dict(model=outcomes, observed_hardware_behavior=False,
                runtime=dict(context="orbstack", server="29.4.0", architecture="aarch64", owned_guest="pending root decision; VM-PLAN.md"),
                actual_machine_power_loss="not performed", limit="Model outcome sets are assumed and do not validate a filesystem")


def mutants():
    rows = []
    real_validate = p.validate
    for name, suppressed in [("identity", "operation_identity"), ("result", "invalid_completed_attachment"), ("owner", "stale_custody")]:
        directory, intent, git = fixture("mutant-" + name)
        if name != "owner":
            check("valid fixture completes before mutation " + name, invoke(directory, intent)["status"], "complete")
        if name == "identity":
            operation = p.read(directory / "operation.json")
            operation["intent"]["id"] = "foreign"
            p.write(directory / "operation.json", operation)
        if name == "result":
            git.run("update-ref", "-d", intent["continuation"])
        token = "stale-token" if name == "owner" else "epoch-1"
        check("unmodified dispatcher rejects mutation " + name, invoke(directory, intent, token=token)["reason"], suppressed)
        def unsafe_validate(path, identity, passed_token, complete=True):
            if name == "owner":
                return real_validate(path, identity, "epoch-1", complete)
            try:
                return real_validate(path, identity, passed_token, complete)
            except p.Refusal as error:
                if str(error) == suppressed:
                    return p.read(Path(path) / "operation.json")
                raise
        p.validate = unsafe_validate
        try:
            unsafe = invoke(directory, intent, token=token)
        finally:
            p.validate = real_validate
        check("known-bad dispatcher reports completion " + name, unsafe["status"], "complete")
        independent_bad = (p.read(directory / "operation.json")["intent"]["id"] != intent["id"] if name == "identity"
                           else git.ref(intent["continuation"]) != intent["result"] if name == "result"
                           else len(provider(directory)["requests"]) == 1 and token != p.read(directory / "authority.json")["token"])
        check("independent artifact/request oracle catches unsafe completion " + name, independent_bad, True)
        rows.append(dict(mutation=name, unsafe_result=unsafe, invariant_violated=independent_bad,
                         provider_requests=len(provider(directory)["requests"])))
    return dict(controls=rows, limitation="Protocol source and checks share edit authority; experimental falsification is not an enforced production gate")


def explicit_only():
    directory, intent, git = fixture("explicit-only")
    old, confirmed = intent["input"], intent["result"]
    reset = git.commit("accepted-reset", {"x": "0\n", "z": "0\n"}, old)
    remote = git.commit("late-plus-legitimate-edit", {"x": "1\n", "z": "2\n"}, old)
    gate = p.drift_decision(git, reset, reset, remote, True)
    check("explicit-only boundary stops every changed overlapping observation", gate["status"], "needs_explicit_drift_review")
    exact_choice = git.commit("explicitly-chosen-reviewed-result", {"x": "0\n", "z": "2\n"}, remote)
    decision = dict(observed=remote, previous_intent=reset, exact_accepted_result=exact_choice,
                    acceptance="Restore x=0 and retain legitimate remote z=2; exact test-supplied decision, not inferred intent")
    p.write(directory / "explicit-decision.json", decision)
    check("explicit result preserves reset and legitimate edit", git.files(exact_choice), {"x": "0\n", "z": "2\n"})
    check("explicit-only acceptance does not complete old operation", p.read(directory / "operation.json")["state"], "planned")
    return dict(decision=decision, automatic_restoration=False, inferred_intent=False,
                comparison=dict(explicit_only="Exact accepted result/observation plus decision; full drift review every time",
                                guarded_proposal="Additional accepted intent-path set and validator; may provide clean proposal but still needs review; reset can require extra resolution"),
                human_cost="Not measured; a programmatically supplied correct decision is not evidence a person notices every lost edit")


def scope_admission():
    pending = [dict(id="old-A-B", input="frozen-object-A-B", scope=["head:A", "head:B", "base:B", "review:B", "source:AB", "checkpoint:AB"], prefix_outcome="lower_landed_suffix_open")]
    rows = []
    for name, mode, effect, accepted, expected in [
        ("strict-B", "strict", dict(kind="same-order-head-amendment", scope=["head:B"]), False, "refused"),
        ("weaker-B-explicit", "weaker", dict(kind="same-order-head-amendment", scope=["head:B"]), True, "admitted"),
        ("weaker-B-unaccepted", "weaker", dict(kind="same-order-head-amendment", scope=["head:B"]), False, "refused"),
        ("fresh-F-only", "strict", dict(kind="first-publication", scope=["head:F", "review:F", "source:F", "checkpoint:F"]), False, "admitted"),
        ("fresh-F-broad-source", "strict", dict(kind="first-publication", scope=["head:F", "source:AB"]), False, "refused"),
        ("fresh-F-shared-checkpoint", "strict", dict(kind="first-publication", scope=["head:F", "checkpoint:AB"]), False, "refused"),
        ("fresh-F-managed-trunk", "strict", dict(kind="first-publication", scope=["head:F", "head:A"]), False, "refused")]:
        result = p.admit_effect(mode, effect, pending, accepted)
        check("scope admission " + name, result["status"], expected)
        rows.append(dict(name=name, effect=effect, result=result))
    unknown = copy.deepcopy(pending)
    unknown[0]["scope"] = None
    check("unknown old scope cannot be called disjoint", p.admit_effect("strict", dict(kind="first-publication", scope=["head:F"]), unknown)["status"], "refused")
    return dict(rows=rows, evidence_bound="Scope sets supplied explicitly by experiment; this does not establish GitHub's complete future effect scope or arbitrate later writes")


def main():
    RUN.mkdir(parents=True)
    for name in ["PLAN.md", "protocol.py", "run.py"]:
        shutil.copyfile(ROOT / name, RUN / name)
    cases = [("R01", "Late reversal and candidate comparison", drift_cases),
             ("R02", "Legitimate remote edits and conflicts", legitimate_edits),
             ("R03", "Repeated changes, no-op and moving source", repetition),
             ("R04", "Per-layer range import", layers),
             ("R05", "Inconsistent reads, stale reads and ABA", observations),
             ("R06", "Bounded event exploration", explore),
             ("R07", "Structural lifecycle domain limit", structural),
             ("R08", "Concurrent and stale direct workers", concurrency),
             ("R09", "Every new durable interruption prefix", interruptions),
             ("R10", "Damaged completion and frozen evidence", damage),
             ("R11", "Partial and unknown effect", partial),
             ("R12", "Fresh local result while old pending", local_acceptance),
             ("R13", "Custody transfer and adoption", transfer),
             ("R14", "Deliberate rollback export", rollback),
             ("R15", "Capability and persistence model", persistence),
             ("R16", "Acceptance oracle mutation controls", mutants),
             ("R17", "Explicit-only drift acceptance control", explicit_only),
             ("R18", "Concrete effect-scope admission", scope_admission)]
    for identity, title, function in cases:
        case(identity, title, function)
    result = dict(run=str(RUN), cases=ROWS, checks_passed=sum(c["passed"] for c in CHECKS),
                  checks_total=len(CHECKS), failed=[r["id"] for r in ROWS if r["status"] != "passed"],
                  source_hashes={n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in ["PLAN.md", "protocol.py", "run.py"]},
                  scope="Fresh experimental local protocol and injected effects, not production or provider guarantees")
    p.write(RUN / "RESULTS.json", result)
    p.write(ROOT / "latest-run.json", {key: value for key, value in result.items() if key != "cases"})
    print(json.dumps({key: value for key, value in result.items() if key not in ("cases", "source_hashes")}))
    return bool(result["failed"])


if __name__ == "__main__":
    sys.exit(main())
