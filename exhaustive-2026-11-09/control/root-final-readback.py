"""Root-only readback and artifact checks; no native writes or old driver run."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
from types import SimpleNamespace
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PARTIAL = ROOT / "workflow/partial-prep"
APP = ROOT / "code-survey/rebase-app-prep"
OUT = ROOT / "publication/root-final-readback-001"


def main():
    source = PARTIAL / "partial_once.py"
    if hashlib.sha256(source.read_bytes()).hexdigest() != "ac332861f99eac829c8bd8419ad765f07ddf29e5cbcd254a5e065de3acfdd7a6":
        raise RuntimeError("Reviewed read-only helper changed")
    sys.path.insert(0, str(PARTIAL))
    spec = importlib.util.spec_from_file_location("reviewed_partial", source)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    OUT.mkdir(exist_ok=False)
    state = json.loads((PARTIAL / "continuation-001/RESULTS.json").read_text())
    if state["prs"] != {"A": 657, "B": 658, "C": 659} or state["stack"]["number"] != 660:
        raise RuntimeError("Unexpected independent fixture")
    git = SimpleNamespace(repo=PARTIAL / "continuation-001/git",
                          hooks=PARTIAL / "continuation-001/empty-hooks")
    effects = driver.e.Effects(OUT, git, state)
    observation = effects.observe("root-current")
    driver.validate_observation(state, observation, state["final_refs"], base_current=False)
    refs = effects.remote_refs("root-full-nine", list(state["final_refs"]))
    if refs != state["final_refs"]:
        raise RuntimeError("Final actual vector drifted")
    app = json.loads((APP / "RESULT.json").read_text())
    archive = APP / "run-001/readback/artifact.zip"
    if hashlib.sha256(archive.read_bytes()).hexdigest() != app["artifact"]["ZIP_sha256"]:
        raise RuntimeError("Artifact digest changed")
    extracted, names = {}, []
    with zipfile.ZipFile(archive) as container:
        for info in container.infolist():
            path = Path(info.filename)
            mode = info.external_attr >> 16
            if (path.is_absolute() or ".." in path.parts or path.suffix != ".json"
                    or stat.S_ISLNK(mode) or info.file_size > 262144
                    or info.filename in names):
                raise RuntimeError("Unsafe or unexpected artifact member")
            data = container.read(info)
            json.loads(data.decode("utf-8"))
            if data != (APP / "run-001/readback/artifact" / path).read_bytes():
                raise RuntimeError("Extracted artifact bytes differ")
            extracted[path.name] = json.loads(data)
            names.append(info.filename)
    if len(names) != 10:
        raise RuntimeError("Unexpected artifact cardinality")
    response = extracted["put-result.json"]
    context = extracted["context.json"]
    if (response != app["exact_request_and_result"] or response["status"] != 404
            or context["runner"]["GITHUB_SHA"] != app["runner"]["commit"]
            or context["runner"]["GITHUB_RUN_ID"] != str(app["runner"]["workflow_run_id"])
            or context["requested_permissions"] != {"contents": "write", "pull-requests": "write"}):
        raise RuntimeError("Actual App artifact identity/outcome mismatch")
    driver.c.save(OUT / "ROOT-VERIFICATION.json", {
        "partial_fresh_native_vector_and_canonical_membership_verified": True,
        "partial_PRs": state["prs"], "partial_group": 660, "refs": refs,
        "app_artifact_digest_and_all_ten_extracted_JSON_members_verified": True,
        "app_actual_PUT_status": 404, "app_run": app["runner"]["workflow_run_id"],
        "limits": "Fresh scoped reads and independent artifact byte checks; no native writes, replay, global snapshot or future-write guarantee."
    }, exclusive=True)
    print(json.dumps({"partial_actual_refs": len(refs), "app_artifact_members": len(names),
                      "status": "verified", "native_writes": 0}))


if __name__ == "__main__":
    main()
