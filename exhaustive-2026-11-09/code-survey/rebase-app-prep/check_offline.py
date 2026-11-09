import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name):
    path = ROOT / name
    namespace = {"__name__": "offline_source_check", "__file__": str(path)}
    exec(compile(path.read_bytes(), str(path), "exec"), namespace)
    return namespace


def main():
    probe = load("probe.py")
    runner = load("fixture_runner.py")
    checks = []
    def rejects(name, operation):
        try:
            operation()
        except ValueError:
            checks.append({"check": name, "passed": True})
        else:
            raise RuntimeError("Unsafe input accepted: " + name)
    helper, ScopedLab = runner["load_helper"]()
    for ref in runner["REFS"].values():
        assert ScopedLab.refname(None, ref) == "refs/heads/" + ref
    checks.append({"check": "exact_four_ref_allowlist", "passed": True})
    for ref in ["main", "exh-1109-causal-rb-capability/A", runner["PREFIX"] + "/C", runner["PREFIX"] + "/A:main"]:
        rejects("foreign_ref_" + ref, lambda ref=ref: ScopedLab.refname(None, ref))
    class FakeLab:
        push_url = "https://github.com/" + runner["REPO"] + ".git"
        def __init__(self, *args):
            pass
        def git(self, *args):
            if args == ("config", "--get", "core.hooksPath"):
                return "/dev/null"
            if args == ("remote", "get-url", "origin"):
                return "https://github.com/" + runner["REPO"] + ".git"
            if args == ("remote", "get-url", "--push", "origin"):
                return self.push_url
            raise RuntimeError("Unexpected command in fake-only control")
    runner["owned_lab"](FakeLab)
    checks.append({"check": "matching_fetch_and_push_URLs", "passed": True})
    FakeLab.push_url = "https://github.com/foreign/fixture.git"
    rejects("different_push_URL_refuses", lambda: runner["owned_lab"](FakeLab))
    class FakeFile:
        def __init__(self, data, path=None):
            self.data, self.path = data, path
        def read_bytes(self):
            return self.data
        def resolve(self):
            return self.path
    effects = [{"kind": "atomic_create_only_push", "updates": {"only": "own"}}]
    frozen = FakeFile(b"frozen-local-plan\n")
    grant_path = runner["CONTROL"].resolve() / "offline-never-created-grant.json"
    grant = {"coordinator": "root", "grant_path": str(grant_path), "phase": "create-fixture", "repository": runner["REPO"], "repository_id": runner["REPO_ID"], "prefix": runner["PREFIX"], "run_directory": str(runner["RUN"].resolve()), "sources": runner["sources"](), "frozen_record_sha256": runner["digest"](frozen.read_bytes()), "effects": effects}
    fake_grant = lambda value: FakeFile(json.dumps(value).encode(), grant_path)
    runner["grant_check"](fake_grant(grant), "create-fixture", frozen, effects)
    checks.append({"check": "exact_in_memory_root_grant_binding", "passed": True})
    for key, value in {"coordinator": "worker", "phase": "launch", "repository": "foreign/repository", "sources": {}, "frozen_record_sha256": "0" * 64, "effects": []}.items():
        changed = {**grant, key: value}
        rejects("grant_rejects_changed_" + key, lambda changed=changed: runner["grant_check"](fake_grant(changed), "create-fixture", frozen, effects))
    config = json.loads((ROOT / "fixture.template.json").read_bytes())
    config.update(root_reviewed=True, stack_number=900, stack_node_id="group-own")
    config["trunk"]["sha"] = "a" * 40
    for index, member in enumerate(config["members"]):
        member.update(number=901 + index, node_id="pr-own-" + str(index), head_oid=str(index + 1) * 40)
    env = {"GITHUB_REPOSITORY": probe["REPOSITORY"], "GITHUB_REF": probe["RUNNER_REF"], "GITHUB_EVENT_NAME": "push", "GITHUB_RUN_ATTEMPT": "1", "GITHUB_ACTOR": "joshlf", "GITHUB_SHA": "c" * 40}
    event = {"created": True, "deleted": False, "before": "0" * 40, "after": "c" * 40, "repository": {"id": probe["REPOSITORY_ID"]}}
    code = (ROOT / "probe.py").read_bytes()
    def validate(value, context):
        raw = json.dumps(value).encode()
        return probe["validate_config"](value, {**context, "PROBE_CONFIG_SHA256": hashlib.sha256(raw).hexdigest()}, event, raw, code)
    assert validate(config, env) == {"expected_head_oid_by_pr_number": {"901": "1" * 40, "902": "2" * 40}}
    checks.append({"check": "exact_two_member_payload", "passed": True})
    rejects("rerun_refuses", lambda: validate(config, {**env, "GITHUB_RUN_ATTEMPT": "2"}))
    changed = copy.deepcopy(config)
    changed["stack_number"] = 653
    rejects("frozen_old_group_refuses", lambda: validate(changed, env))
    for path in ["/repos/" + probe["REPOSITORY"] + "/stacks/900/rebase", "/repositories/1450723431/pulls/900", "/repositories/999/stacks/900/rebase"]:
        rejects("wrong_PUT_route_" + path, lambda path=path: probe["request_once"]("PUT", path, {}, "offline-noncredential", None))
    assert probe["sanitize"]({"Authorization": "offline-secret", "body": "offline-secret ghp_" + "a" * 24}, "offline-secret") == {"Authorization": "<redacted>", "body": "<redacted> <redacted>"}
    checks.append({"check": "exact_token_and_header_redaction", "passed": True})
    assert runner["PERMISSIONS"] == {"contents": "write", "pull-requests": "write"}
    assert '"requested_permissions": {"contents": "write", "pull-requests": "write"}' in code.decode()
    checks.append({"check": "scoped_write_permissions_in_runner_and_context", "passed": True})
    result = {"status": "current_source_and_pure_controls_only", "checks": checks, "source_hashes": runner["sources"](), "effects": "Compiled source and pure/in-memory controls only. Fake grant was never written; no Git, HTTP, fixture construction, workflow, container or hosted effect ran. Earlier mocked driver checks remain frozen with prior prep; they are not relabelled as current-source results."}
    (ROOT / "OFFLINE-CHECKS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pure_checks_passed": len(checks)}))


if __name__ == "__main__":
    main()
