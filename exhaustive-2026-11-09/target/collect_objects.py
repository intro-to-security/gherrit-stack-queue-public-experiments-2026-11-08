import json
import re
import harness as h

sha_contexts = {}
for path in sorted(h.ROOT.glob("*-run-mapping.json")):
    for identity, record in h.read(path).items():
        for context in record["contexts"]:
            for key in ("source_sha", "github_sha", "checkout_head", "merge_commit_sha"):
                sha = context.get(key)
                if sha is not None:
                    if not re.fullmatch("[0-9a-f]{40}", sha):
                        raise ValueError("invalid_retained_object_identity")
                    sha_contexts.setdefault(sha, []).append(dict(mapping=path.name, run=identity, role=key, context=context))
rows = []
for sha, contexts in sorted(sha_contexts.items()):
    remote = h.get("git/commits/" + sha, "retained-object-" + sha[:10])
    available = h.git("cat-file", "-e", sha + "^{commit}", allowed=(0, 128)).returncode == 0
    fetched = None
    if not available:
        result = h.git("fetch", "--no-tags", "origin", sha, allowed=(0, 1, 128))
        fetched = dict(exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
        available = result.returncode == 0
    actual_tree = None
    if available:
        h.git("update-ref", "refs/observed/" + sha, sha)
        actual_tree = h.git("rev-parse", sha + "^{tree}").stdout.strip()
    tests = []
    for witness in contexts:
        context = witness["context"]
        if witness["role"] in ("github_sha", "checkout_head"):
            tests.append(dict(run=witness["run"], logged_tree=context["checkout_tree"],
                              actual_tree=actual_tree, equal=actual_tree == context["checkout_tree"]))
    rows.append(dict(sha=sha, remote_http=remote["http"], remote=remote["data"], fetched=fetched,
                     retained_locally=available, contexts=contexts, tree_checks=tests))
    print(json.dumps(dict(sha=sha, remote_http=remote["http"], retained=available)), flush=True)
h.save(h.ROOT / "OBJECT-RETENTION.json", dict(objects=rows, count=len(rows),
       unavailable=[row["sha"] for row in rows if not row["retained_locally"]],
       tree_mismatches=[test for row in rows for test in row["tree_checks"] if not test["equal"]],
       scope="Objects named by owned job/run evidence only; no hosted mutation"))
