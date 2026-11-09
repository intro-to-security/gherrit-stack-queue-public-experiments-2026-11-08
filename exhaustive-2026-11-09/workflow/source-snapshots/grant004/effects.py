from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

from core import ENV, ZERO, now, save, save_text


ROOT = Path(__file__).resolve().parent
CONTROL = ROOT.parent / "control"
REPO = "joshlf/gherrit-native-stack-experiments-2026-11-08"
URL = "https://github.com/" + REPO + ".git"
GH = "/opt/homebrew/bin/gh"
NOTICE = "*Authored by an AI agent acting on joshlf's behalf.*"
UPDATE_QUERY = '''mutation WorkflowUpdate($input: UpdatePullRequestBranchInput!) {
  updatePullRequestBranch(input: $input) {
    clientMutationId
    pullRequest { id number headRefOid baseRefName baseRefOid
      stack { id number size baseRefName } }
  }
}'''
OBSERVE_QUERY = '''query WorkflowObserve($owner:String!,$name:String!,$number:Int!) {
  repository(owner:$owner,name:$name) {
    pullRequest(number:$number) {
      id number state merged headRefName headRefOid baseRefName baseRefOid
      mergeable mergeStateStatus
      stack { id number size baseRefName entries(first:100) {
        nodes { position pullRequest { id number headRefName headRefOid baseRefName } }
        pageInfo { hasNextPage endCursor }
      } }
      timelineItems(first:100) { pageInfo { hasNextPage endCursor } nodes {
        __typename
        ... on HeadRefForcePushedEvent { id createdAt actor { login }
          beforeCommit { oid } afterCommit { oid } ref { name } }
        ... on AutomaticBaseChangeSucceededEvent { id createdAt oldBase newBase actor { login } }
        ... on AutomaticBaseChangeFailedEvent { id createdAt oldBase newBase actor { login } }
      } }
    }
  }
}'''


class Guard:
    def __init__(self, manifest, grant=None, action=None):
        self.manifest = manifest
        self.grant = Path(grant).resolve() if grant else None
        self.action = action
        self.prefix = manifest["prefix"]
        if manifest["repository"] != REPO:
            raise ValueError("Foreign repository")
        if not re.fullmatch(r"exh-1109-workflow-[a-z0-9-]+", self.prefix):
            raise ValueError("Foreign fixture prefix")

    def branch(self, name):
        if not name.startswith(self.prefix + "/"):
            raise ValueError("Cross-fixture branch")
        if not re.fullmatch(re.escape(self.prefix) + r"/[A-Za-z0-9_-]+", name):
            raise ValueError("Invalid fixture branch")
        if name not in self.manifest["branches"].values():
            raise ValueError("Undeclared fixture branch")

    def ref(self, ref, expected):
        if ref.startswith("refs/heads/"):
            self.branch(ref.removeprefix("refs/heads/"))
            return
        pattern = r"refs/tags/gherrit/" + re.escape(self.prefix) + r"-[A-Z]/v[1-9][0-9]*"
        if (not re.fullmatch(pattern, ref) or expected != ZERO or
                ref not in self.manifest.get("archives", {}).values()):
            raise ValueError("Archive must be an owned create-only version")

    def authorize(self, kind):
        if self.grant is None or self.grant.parent != CONTROL.resolve():
            raise ValueError("A root-created control grant is required")
        grant = json.loads(self.grant.read_text())
        if grant.get("coordinator") != "root" or grant.get("repository") != REPO:
            raise ValueError("Invalid grant authority/repository")
        cases = grant.get("cases", {})
        case = cases.get(self.manifest["case"]) if isinstance(cases, dict) else None
        if not case or case.get("prefix") != self.prefix:
            raise ValueError("Case prefix is not granted")
        if self.action not in case.get("actions", []):
            raise ValueError("Harness action is not granted")
        if kind not in case.get("effects", []):
            raise ValueError("Effect kind is not granted: " + kind)
        for name, expected in grant.get("harness_sha256", {}).items():
            path = ROOT / name
            if path.parent != ROOT or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError("Harness differs from reviewed grant: " + name)
        return grant

    def http(self, kind, method, path, payload):
        root = "repos/" + REPO
        if kind == "create-pr" and method == "POST" and path == root + "/pulls":
            if set(payload) != {"title", "body", "head", "base", "draft"}:
                raise ValueError("Unexpected PR payload")
            self.branch(payload["head"])
            self.branch(payload["base"])
            layer = next(key for key, value in self.manifest["branches"].items()
                         if value == payload["head"])
            planned_base = self.manifest.get("planned_pr_bases", {}).get(layer)
            if not planned_base or payload["base"] != self.manifest["branches"][planned_base]:
                raise ValueError("Unexpected PR base relation")
            if NOTICE not in payload["body"]:
                raise ValueError("Missing authorship notice")
        elif kind == "create-stack" and method == "POST" and path == root + "/stacks":
            expected = list(self.manifest["prs"].values())
            if payload != {"pull_requests": expected} or len(expected) < 2:
                raise ValueError("Wrong native member vector")
        elif kind == "merge" and method == "PUT":
            allowed = {str(self.manifest["prs"][x]) for x in ["A", "F"]
                       if x in self.manifest.get("prs", {})}
            if path not in {root + "/pulls/" + n + "/merge-async" for n in allowed}:
                raise ValueError("Wrong selected merge PR")
            if set(payload) != {"merge_method", "merge_action", "sha"}:
                raise ValueError("Unexpected merge fields")
            if payload["merge_method"] != "squash" or payload["merge_action"] != "direct_merge":
                raise ValueError("Only exact direct squash requests are planned")
            if not re.fullmatch(r"[0-9a-f]{40}", payload["sha"]):
                raise ValueError("Missing exact selected SHA")
        elif kind == "update-branch" and method == "POST" and path == "graphql":
            if payload.get("query") != UPDATE_QUERY or set(payload) != {"query", "variables"}:
                raise ValueError("Arbitrary GraphQL mutation is forbidden")
            value = payload["variables"]["input"]
            if set(value) != {"pullRequestId", "expectedHeadOid", "updateMethod", "clientMutationId"}:
                raise ValueError("Unexpected update input")
            if value["pullRequestId"] not in self.manifest.get("nodes", {}).values():
                raise ValueError("Foreign PR node ID")
            if value["updateMethod"] != "REBASE" or not re.fullmatch(r"[0-9a-f]{40}", value["expectedHeadOid"]):
                raise ValueError("Invalid rebase request")
        else:
            raise ValueError("Unplanned HTTP effect")


class Effects:
    """Record exact attempts before dispatch and freeze ambiguous fixture scopes.

    A root grant is coordination authority for this experiment, not a native
    server fence. Unknown attempts are never retried through this object.
    """

    def __init__(self, directory, git, manifest, grant=None, action=None):
        self.root = Path(directory).resolve()
        self.evidence = self.root / "evidence"
        self.evidence.mkdir(exist_ok=True)
        self.git = git
        self.manifest = manifest
        self.guard = Guard(manifest, grant, action)
        self.env = dict(ENV, GH_HOST="github.com", GH_DEBUG="")

    def intent(self, label, record, *, mutation=False):
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", label):
            raise ValueError("Unsafe attempt label")
        if mutation and (self.root / "FREEZE.json").exists():
            raise RuntimeError("Fixture is frozen")
        if mutation:
            for old in self.evidence.glob("*.intent.json"):
                prior = json.loads(old.read_text())
                if prior.get("kind") not in {"read", "git-read"}:
                    receipt = old.with_name(old.name.replace(".intent.json", ".receipt.json"))
                    if not receipt.exists():
                        raise RuntimeError("Unresolved earlier write intent: " + old.name)
        path = self.evidence / (label + ".intent.json")
        save(path, {**record, "started": now(), "monotonic": time.monotonic()},
             exclusive=True)
        return json.loads(path.read_text())

    def freeze(self, label, reason):
        save(self.root / "FREEZE.json", {"attempt": label, "reason": reason,
                                         "utc": now()}, exclusive=True)

    def api(self, label, method, path, payload=None, *, kind=None):
        mutation = kind is not None
        if mutation:
            self.guard.authorize(kind)
            self.guard.http(kind, method, path, payload)
        else:
            pr_roots = {"repos/" + REPO + "/pulls/" + str(number)
                        for number in self.manifest.get("prs", {}).values()}
            rest_read = method == "GET" and (path == "repos/" + REPO or path in pr_roots or
                        any(path.startswith(root + "/merge-async/") for root in pr_roots))
            variables = payload.get("variables", {}) if payload else {}
            graph_read = (method == "POST" and path == "graphql" and payload and
                          payload.get("query") == OBSERVE_QUERY and
                          variables.get("owner") == "joshlf" and
                          variables.get("name") == REPO.split("/")[1] and
                          variables.get("number") in self.manifest.get("prs", {}).values())
            if not (rest_read or graph_read):
                raise ValueError("Unplanned read request")
        record = self.intent(label, {"kind": kind or "read", "method": method,
                                     "path": path, "payload": payload}, mutation=mutation)
        args = [GH, "api", "--include", "--hostname", "github.com", "-X", method,
                "-H", "X-GitHub-Api-Version: 2026-03-10", path]
        if payload is not None:
            request = self.evidence / (label + ".request.json")
            save(request, payload, exclusive=True)
            args += ["--input", str(request)]
        try:
            process = subprocess.run(args, text=True, capture_output=True, env=self.env,
                                     timeout=90)
        except subprocess.TimeoutExpired:
            if mutation:
                self.freeze(label, "HTTP process timed out without a retained result")
            raise
        response = re.sub(r"(?im)^(set-cookie|authorization):.*$", r"\1: [redacted]",
                          process.stdout)
        save_text(self.evidence / (label + ".response.txt"), response)
        save_text(self.evidence / (label + ".stderr.txt"), process.stderr)
        status_match = re.search(r"^HTTP/\S+\s+(\d+)", response)
        status = int(status_match.group(1)) if status_match else None
        parts = re.split(r"\r?\n\r?\n", response, maxsplit=1)
        try:
            body = json.loads(parts[1]) if len(parts) > 1 and parts[1].strip() else None
        except json.JSONDecodeError:
            body = None
        record.update(ended=now(), exit=process.returncode, http=status, data=body)
        record["disposition"] = "response-retained" if status else "unknown-outcome"
        save(self.evidence / (label + ".receipt.json"), record, exclusive=True)
        errors = isinstance(body, dict) and body.get("errors")
        if mutation and (status is None or status >= 400 or errors):
            self.freeze(label, "Unknown/rejected request requires read-only reconciliation")
        if status is None or (not mutation and (status >= 400 or errors)):
            raise RuntimeError("Observation unavailable: " + label)
        return record

    def network_git(self, label, args, *, mutation=False, updates=None, expected=None):
        if not args or args[0] not in {"push", "fetch", "ls-remote"}:
            raise ValueError("Unplanned Git network command")
        if (args[0] == "push") != mutation:
            raise ValueError("Git push must use the mutation guard")
        if URL not in args or any(arg.startswith("https://") and arg != URL for arg in args):
            raise ValueError("Foreign Git transport destination")
        if mutation:
            self.guard.authorize("push")
            if set(updates) != set(expected):
                raise ValueError("Every pushed ref needs an explicit expectation")
            for ref in updates:
                self.guard.ref(ref, expected[ref])
        record = self.intent(label, {"kind": "push" if mutation else "git-read",
                                     "args": args, "updates": updates,
                                     "expected": expected}, mutation=mutation)
        argv = ["git", "-c", "core.hooksPath=" + str(self.git.hooks),
                "-c", "credential.helper=!" + GH + " auth git-credential",
                "--git-dir=" + str(self.git.repo), *args]
        try:
            process = subprocess.run(argv, env=self.env, text=True, capture_output=True,
                                     timeout=120)
        except subprocess.TimeoutExpired:
            if mutation:
                self.freeze(label, "Git process timed out without a retained result")
            raise
        record.update(ended=now(), exit=process.returncode, stdout=process.stdout,
                      stderr=process.stderr)
        record["disposition"] = "command-acknowledged" if not process.returncode else "requires-reconciliation"
        save(self.evidence / (label + ".receipt.json"), record, exclusive=True)
        if process.returncode:
            if mutation:
                self.freeze(label, "Git write failed or outcome unknown")
            raise RuntimeError("Git network operation failed: " + label)
        return record

    def push(self, label, updates, expected):
        args = ["push", "--porcelain", "--atomic"]
        args += ["--force-with-lease=" + ref + ":" + expected[ref] for ref in updates]
        args += [URL] + [oid + ":" + ref for ref, oid in updates.items()]
        return self.network_git(label, args, mutation=True, updates=updates, expected=expected)

    def remote_refs(self, label, refs):
        for ref in refs:
            self.guard.ref(ref, ZERO)
        result = self.network_git(label, ["ls-remote", "--refs", URL, *refs])
        return {line.split()[1]: line.split()[0] for line in result["stdout"].splitlines()}

    def namespace_inventory(self, label):
        prefix = self.manifest["prefix"]
        patterns = ["refs/heads/" + prefix, "refs/heads/" + prefix + "/*",
                    "refs/tags/gherrit/" + prefix + "-*"]
        result = self.network_git(label, ["ls-remote", "--refs", URL, *patterns])
        return {line.split()[1]: line.split()[0] for line in result["stdout"].splitlines()}

    def fetch(self, label, refs):
        for ref in refs:
            self.guard.ref(ref, ZERO)
        return self.network_git(label, ["fetch", "--no-tags", URL,
                                       *["+" + ref + ":refs/observed/" + ref.removeprefix("refs/")
                                         for ref in refs]])

    def observe(self, label):
        prs = {}
        for layer, number in self.manifest.get("prs", {}).items():
            raw = self.api(label + "-pr-" + layer, "GET",
                           "repos/" + REPO + "/pulls/" + str(number))
            value = raw["data"]
            if value["head"]["repo"]["full_name"] != REPO:
                raise RuntimeError("Foreign head repository")
            self.guard.branch(value["head"]["ref"])
            self.guard.branch(value["base"]["ref"])
            payload = {"query": OBSERVE_QUERY,
                       "variables": {"owner": "joshlf", "name": REPO.split("/")[1],
                                     "number": number}}
            events = self.api(label + "-events-" + layer, "POST", "graphql", payload)
            prs[layer] = {"rest": value, "graphql": events["data"]}
        refs = ["refs/heads/" + name for name in self.manifest["branches"].values()]
        references = self.remote_refs(label + "-refs", refs)
        result = {"utc": now(), "prs": prs, "refs": references}
        save(self.evidence / (label + ".observation.json"), result, exclusive=True)
        return result
