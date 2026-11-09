import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
RUN = Path(json.loads((ROOT / "latest-run.json").read_text())["run"])
ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_TERMINAL_PROMPT="0")
rows = []
for git_directory in sorted(RUN.rglob(".git")):
    repository = git_directory.parent
    result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "fsck", "--full", "--no-reflogs"],
                            cwd=repository, env=ENV, text=True, capture_output=True)
    expected_corruption = "damage-missing-result-object/repo/.git" in str(git_directory)
    rows.append(dict(repository=str(repository.relative_to(ROOT)), exit=result.returncode,
                     stdout=result.stdout, stderr=result.stderr,
                     intentionally_corrupt_fixture=expected_corruption,
                     expected_disposition=expected_corruption or result.returncode == 0))
report = dict(run=str(RUN), repositories=len(rows), rows=rows,
              unexpected_failures=[row for row in rows if not row["expected_disposition"]],
              scope="Object connectivity/integrity only; one intentionally removed result commit is an invalid-evidence control")
(ROOT / "OBJECT-VERIFICATION.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(dict(repositories=len(rows), unexpected_failures=len(report["unexpected_failures"]),
                      expected_corrupt=sum(row["intentionally_corrupt_fixture"] for row in rows))))
raise SystemExit(bool(report["unexpected_failures"]))
