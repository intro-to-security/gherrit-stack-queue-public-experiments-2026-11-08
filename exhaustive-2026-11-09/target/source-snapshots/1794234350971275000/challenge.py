import copy
import json
from pathlib import Path
import tempfile
import harness as h


def main():
    case = dict(name="u", prs=dict(A=901, B=902), heads=dict(A=dict(sha="a" * 40), B=dict(sha="b" * 40)))
    root = "repos/" + h.REPO
    checks = []
    def test(label, function, accepted):
        try:
            function()
            actual = True
        except (ValueError, FileNotFoundError, FileExistsError):
            actual = False
        checks.append(dict(label=label, expected=accepted, actual=actual, passed=accepted == actual))
    test("exact lower PR", lambda: h.guard("POST", root + "/pulls", dict(head=h.PREFIX + "u-A", base=h.PREFIX + "u-trunk"), case), True)
    test("cross-fixture PR", lambda: h.guard("POST", root + "/pulls", dict(head=h.PREFIX + "m-A", base=h.PREFIX + "u-trunk"), case), False)
    test("production mutation", lambda: h.guard("PATCH", "repos/joshlf/gherrit", {}, case), False)
    test("repo flags", lambda: h.guard("PATCH", root, dict(allow_auto_merge=True), case), False)
    test("secret read", lambda: h.guard("GET", root + "/actions/secrets", None), False)
    test("queue request", lambda: h.guard("PUT", root + "/pulls/901/merge-async", dict(sha="a" * 40, merge_method="squash", merge_action="enqueue"), case), False)
    test("wrong selected SHA", lambda: h.guard("PUT", root + "/pulls/901/merge-async", dict(sha="b" * 40, merge_method="squash", merge_action="direct_merge"), case), False)
    test("exact direct request", lambda: h.guard("PUT", root + "/pulls/901/merge-async", dict(sha="a" * 40, merge_method="squash", merge_action="direct_merge"), case), True)
    test("exact order", lambda: h.guard("POST", root + "/stacks", dict(pull_requests=[901,902]), case), True)
    test("reversed order", lambda: h.guard("POST", root + "/stacks", dict(pull_requests=[902,901]), case), False)
    test("foreign PR close", lambda: h.guard("PATCH", root + "/pulls/903", {"state":"closed"}, case), False)
    test("main ref", lambda: h.ref("main"), False)
    test("other lane ref", lambda: h.ref("exh-1109-causal-u-A"), False)
    test("extra P layer", lambda: h.ref(h.PREFIX + "p-B"), False)
    test("exact owned ref", lambda: h.ref(h.PREFIX + "u-B"), True)
    test("main policy", lambda: h.guard("PUT", root + "/branches/main/protection", h.POLICY), False)
    test("exact policy payload", lambda: h.guard("PUT", root + "/branches/" + h.PREFIX + "u-trunk/protection", h.POLICY), True)
    changed = copy.deepcopy(h.RULE)
    changed["conditions"]["ref_name"]["include"] = ["~ALL"]
    test("wildcard ruleset", lambda: h.guard("POST", root + "/rulesets", changed), False)
    test("exact ruleset", lambda: h.guard("POST", root + "/rulesets", h.RULE), True)
    test("unowned ruleset removal", lambda: h.guard("DELETE", root + "/rulesets/99999", None), False)
    test("GraphQL mutation", lambda: h.guard("POST", "graphql", dict(query="mutation { nope }")), False)
    test("GraphQL query", lambda: h.guard("POST", "graphql", dict(query="query { viewer { login } }")), True)
    with tempfile.TemporaryDirectory(dir=h.ROOT) as temporary:
        original = h.ROOT
        h.ROOT = Path(temporary)
        try:
            test("first attempt marker", lambda: h.begin("one-attempt", {"effect":"not-dispatched-local-control"}), True)
            test("duplicate attempt marker", lambda: h.begin("one-attempt", {"effect":"must-not-dispatch"}), False)
        finally:
            h.ROOT = original
    result = dict(checks=checks, passed=sum(x["passed"] for x in checks), total=len(checks), network_effects=0)
    h.save(h.ROOT / "GUARD-CHALLENGE.json", result)
    print(json.dumps(dict(passed=result["passed"], total=result["total"], network_effects=0)))
    if result["passed"] != result["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
