import argparse
import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("reviewed_app_fixture_runner", ROOT / "fixture_runner.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def snapshot(label):
    runner.require(re.fullmatch(r"after-(?:0|30)", label), "Only the two bounded read cohorts are allowed")
    prepared = json.loads((runner.RUN / "PREPARED.json").read_bytes())
    ready = json.loads((runner.RUN / "RUNNER-READY.json").read_bytes())
    runner.require(ready["sources"] == runner.sources(), "Reviewed execution source changed")
    helper, Lab = runner.load_helper()
    output = runner.RUN / "readback" / (label + ".json")
    helper.preserve(runner.RUN / "readback" / (label + ".read-intent.json"), {"at": helper.stamp(), "scope": runner.PREFIX, "read_only": True})
    lab = runner.owned_lab(Lab)
    started = helper.stamp()
    refs = runner.read_refs(lab, label + "-refs")
    lab.command(label + "-fetch", ["git", "-c", "core.hooksPath=/dev/null", "--git-dir", str(lab.bare), "fetch", "--no-tags", "origin", "+refs/heads/" + runner.PREFIX + "/*:refs/observed/app/*"])
    stack = lab.api(label + "-stack", "/stacks/656")
    runner.require(ready["stack"]["number"] == 656 and stack.get("node_id") == ready["stack"]["node_id"], "Canonical group mismatch")
    event_fields = """__typename
... on HeadRefForcePushedEvent { id createdAt actor { login __typename } beforeCommit { oid } afterCommit { oid } ref { name target { oid } } }
... on BaseRefChangedEvent { id createdAt actor { login __typename } previousRefName currentRefName }
... on AutomaticBaseChangeSucceededEvent { id createdAt actor { login __typename } oldBase newBase }
... on AutomaticBaseChangeFailedEvent { id createdAt actor { login __typename } oldBase newBase }
"""
    fields = [letter + ":pullRequest(number:" + str(ready["prs"][letter]["number"]) + "){number id state merged mergedAt headRefName headRefOid baseRefName baseRefOid timelineItems(last:100,itemTypes:[HEAD_REF_FORCE_PUSHED_EVENT,BASE_REF_CHANGED_EVENT,AUTOMATIC_BASE_CHANGE_SUCCEEDED_EVENT,AUTOMATIC_BASE_CHANGE_FAILED_EVENT]){pageInfo{hasPreviousPage}nodes{" + event_fields + "}}}" for letter in ["A", "B"]]
    query = 'query {repository(owner:"joshlf",name:"gherrit-native-stack-experiments-2026-11-08"){' + " ".join(fields) + "}}"
    runner.require("mutation" not in query.lower(), "Read query unexpectedly contains mutation")
    helper.preserve(runner.RUN / "readback" / (label + ".query.json"), {"operation": "read_only_GraphQL_query", "query": query})
    response = lab.command(label + "-events", ["gh", "api", "graphql", "--input", "-"], data=json.dumps({"query": query}))
    graphql = json.loads(response["stdout"])
    runner.require(not graphql.get("errors"), "GraphQL observation unavailable")
    prs = graphql["data"]["repository"]
    headers, patches = {}, {}
    for name, branch in runner.REFS.items():
        oid = refs.get("refs/heads/" + branch)
        runner.require(oid is not None, "Captured owned ref absent")
        raw = lab.git("show", "-s", "--format=%H%x00%T%x00%P", oid)
        actual, tree, parents = raw.split("\0")
        headers[name] = {"oid": actual, "tree": tree, "parents": parents.split(), "commit_header": lab.git("cat-file", "-p", oid)}
    for letter in ["A", "B"]:
        pr = prs[letter]
        runner.require(pr["number"] == ready["prs"][letter]["number"] and pr["id"] == ready["prs"][letter]["node_id"], "Canonical PR mismatch")
        runner.require(pr["timelineItems"]["pageInfo"]["hasPreviousPage"] is False, "Timeline evidence incomplete")
        runner.require(len(headers[letter]["parents"]) == 1, "Own-layer comparison needs one declared parent")
        original_parent = prepared["commits"]["trunk" if letter == "A" else "A"]
        original = lab.git("diff", "--binary", original_parent, prepared["commits"][letter])
        observed = lab.git("diff", "--binary", headers[letter]["parents"][0], headers[letter]["oid"])
        patches[letter] = {"original_patch": original, "observed_own_patch": observed, "equal": original == observed}
    expected = runner.expected_refs(prepared)
    expected["refs/heads/" + runner.REFS["runner"]] = ready["commit"]
    result = {"label": label, "started": started, "ended": helper.stamp(), "refs": refs, "stack": stack, "graphql": graphql, "headers": headers, "patches": patches, "exact_expected_refs_match": refs == expected, "all_PR_heads_and_lifecycles_match": all(prs[letter]["state"] == "OPEN" and prs[letter]["headRefOid"] == prepared["commits"][letter] for letter in ["A", "B"]), "limits": "Separate timed reads, not one atomic snapshot or a future-write fence. Event object timestamps do not establish physical ref-write timing. The scope stays frozen; no native mutation is dispatched by this reader."}
    helper.preserve(output, result)
    print(json.dumps({"snapshot": str(output), "started": started, "ended": result["ended"], "exact_refs_match": result["exact_expected_refs_match"], "PR_heads_and_lifecycles_match": result["all_PR_heads_and_lifecycles_match"], "event_counts": {letter: len(prs[letter]["timelineItems"]["nodes"]) for letter in ["A", "B"]}, "own_patches_equal": all(value["equal"] for value in patches.values())}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Two fixed read-only cohorts for the single granted App-token case")
    parser.add_argument("label", choices=["after-0", "after-30"])
    snapshot(parser.parse_args().label)
