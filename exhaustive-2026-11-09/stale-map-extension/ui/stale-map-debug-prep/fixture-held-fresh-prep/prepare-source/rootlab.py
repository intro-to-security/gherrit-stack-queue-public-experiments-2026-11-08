"""Small, explicitly scoped fixture tools for root's synthetic experiments."""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

PERSONAL = "joshlf/gherrit-native-stack-experiments-2026-11-08"
PUBLIC = "intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08"
NOTICE = "*Authored by an AI agent acting on joshlf's behalf.*"
TRAILER = "Agent-authored-by: AI agent acting on joshlf's behalf"


def stamp() -> dict:
    return {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "monotonic_ns": time.monotonic_ns()}


def preserve(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    if path.read_bytes() != raw:
        raise OSError(f"Evidence readback failed: {path}")


class Lab:
    def __init__(self, root: Path, prefix: str, repo: str = PERSONAL):
        if repo not in {PERSONAL, PUBLIC} or not prefix.startswith("exh-1109-"):
            raise ValueError("Unallocated repository or namespace")
        self.root = root.resolve()
        self.repo = repo
        self.prefix = prefix
        self.bare = self.root / "objects.git"
        self.records = self.root / "records"
        self.records.mkdir(parents=True, exist_ok=True)
        if not self.bare.exists():
            self.root.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "init", "--bare", str(self.bare)], check=True, capture_output=True)
            self.git("config", "core.hooksPath", "/dev/null")
            self.git("config", "user.name", "Josh Liebow-Feeser")
            self.git("config", "user.email", "hello@joshlf.com")
            self.git("config", "commit.gpgsign", "false")
            self.git("remote", "add", "origin", f"https://github.com/{repo}.git")

    def git(self, *args: str, data: str | None = None, allowed=(0,)) -> str:
        result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "--git-dir", str(self.bare), *args],
                                input=data, text=True, capture_output=True)
        if result.returncode not in allowed:
            raise RuntimeError(f"Git {args[0]} failed: {result.stderr}")
        return result.stdout.strip()

    def command(self, label: str, args: list[str], data: str | None = None, mutation=False, allowed=(0,)) -> dict:
        if not label or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in label):
            raise ValueError("Unsafe evidence label")
        intent = self.records / f"{label}.intent.json"
        if mutation:
            # Exclusive evidence creation makes repeating a named dispatch fail.
            preserve(intent, {"time": stamp(), "repo": self.repo, "prefix": self.prefix,
                              "argv": args, "input": data, "outcome": "may be dispatched"})
        started = stamp()
        result = subprocess.run(args, input=data, text=True, capture_output=True)
        receipt = {"started": started, "finished": stamp(), "returncode": result.returncode,
                   "stdout": result.stdout, "stderr": result.stderr}
        preserve(self.records / f"{label}.receipt.json", receipt)
        if result.returncode not in allowed:
            raise RuntimeError(f"{label} failed/unknown; inspect retained receipt before any continuation: {result.stderr}")
        return receipt

    def api(self, label: str, suffix: str, method="GET", body=None, allowed=(0,)):
        if not suffix.startswith("/"):
            raise ValueError("Expected a repository-relative API path")
        args = ["gh", "api", "--method", method, f"repos/{self.repo}{suffix}"]
        data = None
        if body is not None:
            args += ["--input", "-"]
            data = json.dumps(body)
        receipt = self.command(label, args, data, mutation=method != "GET", allowed=allowed)
        if receipt["returncode"] != 0:
            return {"command_error": receipt}
        text = receipt["stdout"]
        return json.loads(text) if text.strip() else None

    def refname(self, branch: str) -> str:
        if not branch.startswith(self.prefix + "-") or any(c in branch for c in " \t\r\n:"):
            raise ValueError("Ref outside allocated namespace")
        return "refs/heads/" + branch

    def push(self, label: str, updates: dict[str, tuple[str | None, str]]):
        args = ["git", "-c", "core.hooksPath=/dev/null", "--git-dir", str(self.bare), "push", "--atomic"]
        for branch, (expected, target) in updates.items():
            ref = self.refname(branch)
            if expected is not None and len(expected) != 40 or len(target) != 40:
                raise ValueError("Expected exact Git object IDs")
            args.append(f"--force-with-lease={ref}:{expected or ''}")
        args.append("origin")
        args += [f"{target}:{self.refname(branch)}" for branch, (_, target) in updates.items()]
        return self.command(label, args, mutation=True)

    def commit(self, files: dict[str, str], parent: str | None, message: str) -> str:
        entries = []
        for name, content in sorted(files.items()):
            if "/" in name or "\n" in name:
                raise ValueError("This fixture tree supports flat filenames only")
            blob = self.git("hash-object", "-w", "--stdin", data=content)
            entries.append(f"100644 blob {blob}\t{name}\n")
        tree = self.git("mktree", data="".join(entries))
        args = ["commit-tree", tree]
        if parent:
            args += ["-p", parent]
        return self.git(*args, data=message + "\n\n" + TRAILER + "\n")

    def fixture(self, key: str, layers=2) -> dict:
        path = self.root / f"fixture-{key}.json"
        if path.exists():
            raise ValueError("Fixture already recorded; reconcile it instead of recreating")
        tag = f"{self.prefix}-{key}-{uuid.uuid4().hex[:8]}"
        files = {"root.txt": "Synthetic native-stack experiment.\n"}
        trunk = self.commit(files, None, "Record the isolated synthetic trunk")
        refs = {"trunk": tag + "-trunk"}
        commits = {"trunk": trunk}
        trees = {"trunk": dict(files)}
        parent = trunk
        for i in range(layers):
            name = chr(65 + i)
            files[name.lower() + ".txt"] = f"Synthetic layer {name}.\n"
            parent = self.commit(files, parent, f"Record synthetic layer {name}")
            refs[name] = tag + "-" + name.lower()
            commits[name] = parent
            trees[name] = dict(files)
        result = {"key": key, "repo": self.repo, "refs": refs, "commits": commits, "trees": trees}
        preserve(path, result)
        self.push(key + "-initial-push", {refs[n]: (None, oid) for n, oid in commits.items()})
        prs = {}
        for i in range(layers):
            name = chr(65 + i)
            base = "trunk" if i == 0 else chr(64 + i)
            pr = self.api(key + "-create-" + name.lower(), "/pulls", "POST",
                          {"head": refs[name], "base": refs[base], "title": f"Synthetic {key}: layer {name}",
                           "body": "Authorized synthetic evidence fixture.\n\n" + NOTICE})
            prs[name] = pr["number"]
        preserve(self.root / f"prs-{key}.json", prs)
        result["prs"] = prs
        if layers >= 2:
            result["stack"] = self.api(key + "-register", "/stacks", "POST", {"pull_requests": list(prs.values())})
            preserve(self.root / f"stack-{key}.json", result["stack"])
        return result
