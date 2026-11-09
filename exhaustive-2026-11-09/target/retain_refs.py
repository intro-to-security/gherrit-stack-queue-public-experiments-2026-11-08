import json
import harness as h

names = set()
for name in h.SPECS:
    case = h.state(name)
    names.add(case["trunk"])
    names.update(head["ref"] for head in case["heads"].values())
if (h.ROOT / "followup-case.json").exists():
    case = h.read(h.ROOT / "followup-case.json")
    names.add(case["trunk"])
    names.update(head["ref"] for head in case["heads"].values())
refs = ["refs/heads/" + name for name in sorted(names)]
observed = h.git("ls-remote", "origin", *refs).stdout
mapping = {line.split("\t")[1]:line.split("\t")[0] for line in observed.splitlines()}
if set(mapping) != set(refs):
    raise RuntimeError("missing_owned_remote_ref")
fetch = h.git("fetch", "--no-tags", "origin", *["+" + ref + ":refs/observed/heads/" + ref[len("refs/heads/"):] for ref in refs])
objects = {}
for ref, sha in mapping.items():
    actual = h.git("rev-parse", "refs/observed/heads/" + ref[len("refs/heads/"):]).stdout.strip()
    objects[ref] = dict(ls_remote=sha, fetched=actual, equal=sha == actual,
                       commit=h.git("show", "-s", "--format=%H %T %P", actual).stdout.strip())
result = dict(time=h.now(), count=len(mapping), refs=objects, fetch_stdout=fetch.stdout,
              fetch_stderr=fetch.stderr, read_only_remote=True,
              discrepancies=[ref for ref, row in objects.items() if not row["equal"]])
h.save(h.ROOT / "REF-RETENTION.json", result)
print(json.dumps(dict(refs=len(mapping), discrepancies=result["discrepancies"])))
