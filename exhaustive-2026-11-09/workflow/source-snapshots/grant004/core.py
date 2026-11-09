from __future__ import annotations

from dataclasses import asdict, dataclass
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


USER = {"name": "Josh Liebow-Feeser", "email": "hello@joshlf.com"}
TRAILER = "Agent-authored-by: AI agent acting on joshlf's behalf"
ZERO = "0" * 40
ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
           GIT_TERMINAL_PROMPT="0", LC_ALL="C")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def fsync_directory(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def save(path, value, *, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if exclusive:
        with path.open("x") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    else:
        temporary = path.with_name(path.name + ".tmp")
        with temporary.open("w") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    fsync_directory(path.parent)
    if path.read_text() != encoded:
        raise RuntimeError("Durable evidence readback differs: " + str(path))


def save_text(path, text):
    path = Path(path)
    with path.open("x") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    fsync_directory(path.parent)
    if path.read_text() != text:
        raise RuntimeError("Evidence text readback differs: " + str(path))


@dataclass(frozen=True)
class Range:
    base: str
    tip: str


@dataclass(frozen=True)
class Layer:
    change: str
    incorporated: Range
    local: Range
    hosted: Range


class Conflict(Exception):
    pass


class Git:
    """Construct and integrate retained objects in an owned local bare repo.

    Network commands are deliberately absent; effects.py owns every hosted
    operation. Caller-supplied refs never replace the immutable range inputs.
    """

    def __init__(self, directory):
        self.root = Path(directory).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.repo = self.root / "git"
        self.hooks = self.root / "empty-hooks"
        self.hooks.mkdir(exist_ok=True)
        self.transcript = self.root / "git-commands.jsonl"
        if not self.repo.exists():
            subprocess.run(["git", "init", "--bare", str(self.repo)],
                           env=ENV, capture_output=True, check=True)
            self.git("config", "core.hooksPath", str(self.hooks))
            self.git("config", "user.name", USER["name"])
            self.git("config", "user.email", USER["email"])
            self.git("config", "commit.gpgsign", "false")
        if self.git("config", "--get", "core.hooksPath") != str(self.hooks):
            raise RuntimeError("Owned Git hooks are not disabled")

    def command(self, *args, input=None, env=None, allowed=(0,)):
        if args and args[0] in {"push", "fetch", "pull", "clone", "remote"}:
            raise ValueError("Network commands belong to the effects boundary")
        argv = ["git", "-c", "core.hooksPath=" + str(self.hooks),
                "--git-dir=" + str(self.repo), *args]
        result = subprocess.run(argv, input=input, text=True, capture_output=True,
                                env=env or ENV)
        with self.transcript.open("a") as stream:
            stream.write(json.dumps({"utc": now(), "args": list(args),
                                     "stdin": input, "returncode": result.returncode,
                                     "stdout": result.stdout, "stderr": result.stderr}) + "\n")
        if result.returncode not in allowed:
            raise RuntimeError("Local Git failed: " + result.stderr)
        return result

    def git(self, *args, **kwargs):
        return self.command(*args, **kwargs).stdout.strip()

    def commit(self, label, parent, updates, subject, *, message=None):
        if not label.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Unsafe local input label")
        index = self.root / (label + ".index")
        if index.exists():
            raise RuntimeError("Input label already has an index: " + label)
        environment = dict(ENV, GIT_INDEX_FILE=str(index))
        self.git("read-tree", parent if parent else "--empty", env=environment)
        for path, value in sorted(updates.items()):
            if Path(path).is_absolute() or ".." in Path(path).parts:
                raise ValueError("Unsafe synthetic file path")
            if value is None:
                self.git("update-index", "--force-remove", path, env=environment)
            else:
                blob = self.git("hash-object", "-w", "--stdin", input=value)
                self.git("update-index", "--add", "--cacheinfo", "100644", blob,
                         path, env=environment)
        tree = self.git("write-tree", env=environment)
        text = message or (subject + "\n\n" + TRAILER + "\n")
        args = ["commit-tree", tree]
        if parent:
            args += ["-p", parent]
        oid = self.git(*args, input=text)
        self.git("update-ref", "refs/inputs/" + label, oid, ZERO)
        save(self.root / "inputs" / (label + ".json"),
             {"oid": oid, "parent": parent, "tree": tree, "updates": updates,
              "message": text}, exclusive=True)
        index.unlink()
        return oid

    def commit_tree(self, label, parent, tree, message):
        oid = self.git("commit-tree", tree, "-p", parent, input=message)
        self.git("update-ref", "refs/inputs/" + label, oid, ZERO)
        return oid

    def message(self, oid):
        return self.command("cat-file", "commit", oid).stdout.split("\n\n", 1)[1]

    def tree(self, oid):
        return self.git("rev-parse", oid + "^{tree}")

    def merge(self, label, base, ours, theirs):
        result = self.command("merge-tree", "--write-tree", "--merge-base=" + base,
                              ours, theirs, allowed=(0, 1))
        tree = result.stdout.splitlines()[0]
        save(self.root / "merges" / (label + ".json"),
             {"base": base, "ours": ours, "theirs": theirs, "tree": tree,
              "returncode": result.returncode, "stdout": result.stdout,
              "stderr": result.stderr}, exclusive=True)
        self.git("update-ref", "refs/merge-inputs/" + label, tree, ZERO)
        if result.returncode:
            raise Conflict(label)
        return self.commit_tree(label, ours, tree,
                                label + "\n\n" + TRAILER + "\n")

    def integrate(self, label, layers, output_parent):
        result = []
        for layer in layers:
            prefix = label + "-" + layer.change
            old = self.merge(prefix + "-old", layer.incorporated.base,
                             layer.hosted.base, layer.incorporated.tip)
            local = self.merge(prefix + "-local", layer.local.base,
                               layer.hosted.base, layer.local.tip)
            joined = self.merge(prefix + "-joined", old, local, layer.hosted.tip)
            replay = self.merge(prefix + "-replay", layer.hosted.base,
                                output_parent, joined)
            tip = self.commit_tree(prefix + "-accepted", output_parent,
                                   self.tree(replay), self.message(layer.local.tip))
            result.append({"change": layer.change,
                           "incorporated": asdict(layer.hosted),
                           "accepted_local": asdict(Range(output_parent, tip)),
                           "old_normalized": old, "local_normalized": local,
                           "joined": joined})
            output_parent = tip
        return result

    def patch(self, revision):
        return self.command("diff", "--no-ext-diff", "--binary", revision.base,
                            revision.tip).stdout

    def changed_paths(self, revision):
        return self.git("diff", "--name-only", revision.base,
                        revision.tip).splitlines()

    def snapshot(self, revision):
        return {**asdict(revision), "base_tree": self.tree(revision.base),
                "tip_tree": self.tree(revision.tip), "patch": self.patch(revision),
                "message": self.message(revision.tip)}

    def checkpoint(self, name, source, result, incorporated, authored, old_operations):
        ref = "refs/continuations/" + name
        intent = {"kind": "local-import", "source": source, "result": result,
                  "continuation": ref, "incorporated": incorporated,
                  "authored": authored, "old_operations": old_operations}
        save(self.root / "checkpoints" / (name + ".intent.json"), intent,
             exclusive=True)
        self.git("update-ref", ref, result, ZERO)
        save(self.root / "checkpoints" / (name + ".json"), intent, exclusive=True)
        return intent

    def workload(self, oid):
        files = {}
        for name in ["model.py", "consumer.py"]:
            files[name] = self.command("show", oid + ":workflow_case/" + name).stdout
        return files

    def behavior(self, label, oid, *, expected, quantity=False):
        directory = self.root / "behavior" / label
        directory.mkdir(parents=True)
        for name, text in self.workload(oid).items():
            (directory / name).write_text(text)
        arguments = "'apple', 3" if quantity else "'apple'"
        script = ("from model import Item\nfrom consumer import describe\n"
                  "print(describe(Item(" + arguments + ")))\n")
        process = subprocess.run([sys.executable, "-c", script], cwd=directory,
                                 env=ENV, text=True, capture_output=True)
        result = {"oid": oid, "expected": expected,
                  "returncode": process.returncode, "stdout": process.stdout,
                  "stderr": process.stderr}
        save(directory / "result.json", result)
        passed = (process.returncode == 0 and process.stdout.strip() == expected)
        if expected is None:
            passed = process.returncode != 0
        if not passed:
            raise AssertionError(json.dumps(result))
        return result


MODEL0 = "class Item:\n    def __init__(self, name):\n        self.name = name\n"
MODELA = ("class Item:\n    def __init__(self, name, quantity=1):\n"
          "        self.name = name\n        self.quantity = quantity\n")
MODELF = ("class Item:\n    def __init__(self, name, quantity=1, unit='each'):\n"
          "        self.name = name\n        self.quantity = quantity\n"
          "        self.unit = unit\n")
CONSUMER0 = "from model import Item\n\ndef describe(item):\n    return item.name\n"
CONSUMERB = ("from model import Item\n\ndef describe(item):\n"
             "    return item.name + ':' + str(item.quantity)\n")
CONSUMERBP = ("from model import Item\n\ndef describe(item):\n"
              "    return item.name + ':' + str(item.quantity) + ' ' + item.unit\n")
CONSUMERBPENDING = CONSUMERBP.replace("item.name +", "item.name.upper() +")


def staged_inputs(git, seed=None):
    trunk = git.commit("trunk", seed,
                       {"workflow_case/model.py": MODEL0,
                        "workflow_case/consumer.py": CONSUMER0},
                       "Seed the isolated staged-workflow fixture")
    a = git.commit("A0", trunk, {"workflow_case/model.py": MODELA},
                   "Add quantity to the item model")
    b = git.commit("B0", a, {"workflow_case/consumer.py": CONSUMERB},
                   "Report item quantities")
    ap = git.commit("Aprime", trunk, {"workflow_case/model.py": MODELF},
                    "Add quantity and unit to the item model")
    bp = git.commit("Bprime", ap, {"workflow_case/consumer.py": CONSUMERBP},
                    "Report item quantities with their unit")
    return {"trunk": trunk, "A0": a, "B0": b, "Aprime": ap, "Bprime": bp}


def staged_admission(*, independently_landable, joint_review_required,
                     public_source_tip, followup_tip):
    if joint_review_required:
        return {"accepted": False, "reason": "Joint dependent review was requested"}
    if not independently_landable:
        return {"accepted": False, "reason": "F cannot land independently"}
    if public_source_tip is not None and public_source_tip != followup_tip:
        return {"accepted": False, "reason": "The accepted public export includes deferred work"}
    return {"accepted": True, "reason": "F-only staging was explicitly selected"}
