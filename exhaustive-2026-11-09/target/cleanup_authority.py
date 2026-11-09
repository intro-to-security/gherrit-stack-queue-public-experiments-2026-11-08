import hashlib
import json
import harness as h


def prove():
    owned = h.read(h.ROOT / "policy-owned.json")
    expected = [h.SPECS[name]["trunk"] for name in "umrp"]
    if owned["protections"] != expected or owned["ruleset_id"] != 26858731:
        raise ValueError("unexpected_cleanup_scope")
    receipts = [(path, h.read(path)) for path in (h.ROOT / "evidence").glob("policy-*.receipt.json")]
    proof = dict(repository=h.REPO, grant="../control/target-grant-001.json#policy_delegation/cleanup",
                 planned_PR_changes=[], protections=[], ruleset=None, native_outcomes=[])
    for name in "umrp":
        trunk = h.SPECS[name]["trunk"]
        endpoint = "repos/" + h.REPO + "/branches/" + trunk + "/protection"
        apply = h.read(h.ROOT / "evidence" / ("policy-apply-" + name + ".receipt.json"))
        if apply["method"] != "PUT" or apply["path"] != endpoint or apply["http"] != 200 or apply["payload"] != h.POLICY:
            raise ValueError("missing_exact_create_receipt")
        before = [(path, data) for path, data in receipts if data["method"] == "GET" and data["path"] == endpoint and data["http"] == 404 and data["end"] < apply["start"]]
        if len(before) != 1:
            raise ValueError("missing_unique_precreate_absence")
        path, data = before[0]
        proof["protections"].append(dict(trunk=trunk, initial_status=404,
                  before_receipt=str(path.relative_to(h.ROOT)), before_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  create_receipt="evidence/policy-apply-" + name + ".receipt.json", create_status=200))
    create = h.read(h.ROOT / "evidence" / "policy-create-ruleset.receipt.json")
    if create["http"] != 201 or create["data"]["id"] != 26858731 or create["payload"] != h.RULE:
        raise ValueError("missing_exact_ruleset_create_receipt")
    before = [(path, data) for path, data in receipts if data["method"] == "GET" and data["path"].endswith("/rulesets?per_page=100") and data["http"] == 200 and data["end"] < create["start"]]
    if len(before) != 1 or any(item["name"] == h.RULE["name"] for item in before[0][1]["data"]):
        raise ValueError("named_rule_not_previously_absent")
    proof["ruleset"] = dict(id=26858731, name=h.RULE["name"], initial_named_absence=True,
                            exact_refs=h.RULE["conditions"]["ref_name"]["include"],
                            before_receipt=str(before[0][0].relative_to(h.ROOT)),
                            create_receipt="evidence/policy-create-ruleset.receipt.json")
    for name in h.SPECS:
        case = h.state(name)
        for operation in case["native"]:
            terminal = operation.get("terminal")
            if not terminal or terminal.get("status") not in ("merged", "failed", "request-rejected"):
                raise ValueError("unresolved_native_outcome")
            proof["native_outcomes"].append(dict(fixture=name, uuid=operation.get("uuid"), terminal=terminal))
    h.policy_snapshot("restoration-authority-fresh")
    proof["meaning"] = "Restore only controls newly created for fresh synthetic trunks to their captured initial absence; retain all fixture PRs and refs; no preexisting/default/production protection changes"
    h.save(h.ROOT / "CLEANUP-AUTHORITY.json", proof)
    return proof


if __name__ == "__main__":
    print(json.dumps(prove(), indent=2))
