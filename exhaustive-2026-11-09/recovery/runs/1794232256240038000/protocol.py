import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
           GIT_TERMINAL_PROMPT="0", LC_ALL="C", PYTHONDONTWRITEBYTECODE="1")
ZERO = "0" * 40
TRAILER = "Agent-authored-by: AI agent acting on joshlf's behalf"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-" + str(os.getpid()))
    with temporary.open("w") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


@contextlib.contextmanager
def owner(path):
    with Path(path).open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


class Git:
    def __init__(self, root, initialize=False):
        self.root = Path(root).resolve()
        self.log = self.root.parent / (self.root.name + "-commands.jsonl")
        self.serial = 0
        if initialize:
            self.root.mkdir(parents=True)
            self.run("init", "-q", "--initial-branch=source")
            for key, value in [("user.name", "Josh Liebow-Feeser"),
                               ("user.email", "hello@joshlf.com"),
                               ("core.hooksPath", "/dev/null"),
                               ("commit.gpgsign", "false")]:
                self.run("config", "--local", key, value)

    def run(self, *args, stdin=None, allowed=(0,), env=None):
        result = subprocess.run(["git", *args], cwd=self.root, input=stdin,
                                text=True, capture_output=True, env=env or ENV)
        entry = dict(argv=["git", *args], cwd=str(self.root), stdin=stdin,
                     exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
        with self.log.open("a") as stream:
            stream.write(json.dumps(entry, sort_keys=True) + "\n")
        if result.returncode not in allowed:
            raise RuntimeError(json.dumps(entry))
        return result

    def commit(self, label, files, parent=None, message=None):
        self.serial += 1
        index = self.root.parent / ("index-" + str(os.getpid()))
        if index.exists():
            index.unlink()
        env = dict(ENV, GIT_INDEX_FILE=str(index))
        self.run("read-tree", "--empty", env=env)
        for name, content in sorted(files.items()):
            blob = self.run("hash-object", "-w", "--stdin", stdin=content).stdout.strip()
            self.run("update-index", "--add", "--cacheinfo", "100644", blob, name, env=env)
        tree = self.run("write-tree", env=env).stdout.strip()
        result = self.commit_tree(label, tree, parent, message)
        index.unlink()
        return result

    def commit_tree(self, label, tree, parent, message=None):
        args = ["commit-tree", tree] + (["-p", parent] if parent else [])
        message = message or label + "\n\n" + TRAILER + "\n"
        result = self.run(*args, stdin=message).stdout.strip()
        self.run("update-ref", "refs/fixtures/" + label, result)
        return result

    def files(self, commit):
        names = self.run("ls-tree", "-r", "--name-only", commit).stdout.splitlines()
        return {name: self.run("show", commit + ":" + name).stdout for name in names}

    def tree(self, commit):
        return self.run("rev-parse", commit + "^{tree}").stdout.strip()

    def ref(self, name):
        return self.run("rev-parse", "--verify", name, allowed=(0, 128)).stdout.strip()

    def valid_commit(self, value):
        return self.run("cat-file", "-e", value + "^{commit}", allowed=(0, 128)).returncode == 0

    def merge(self, label, base, local, remote):
        result = self.run("merge-tree", "--write-tree", "--merge-base=" + base,
                          local, remote, allowed=(0, 1))
        tree = result.stdout.splitlines()[0]
        write(self.root.parent / (label + "-merge.json"),
              dict(base=base, local=local, remote=remote, tree=tree,
                   exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
        self.run("update-ref", "refs/merge-trees/" + label, tree)
        if result.returncode:
            return None
        return self.commit_tree(label, tree, local)


def drift_decision(git, incorporated, accepted_intent, observed, pending_overlap,
                   action=None, prior_input=None, label="review"):
    changed = git.tree(incorporated) != git.tree(observed)
    if pending_overlap and changed and action is None:
        return dict(status="needs_explicit_drift_review", proposed=None)
    if pending_overlap and changed and action == "restore":
        if prior_input is None:
            return dict(status="missing_old_input", proposed=None)
        proposed = git.merge(label, prior_input, accepted_intent, observed)
        return dict(status="restoration_proposal" if proposed else "conflict", proposed=proposed)
    if action == "accept_remote":
        return dict(status="remote_explicitly_accepted", proposed=observed)
    proposed = git.merge(label, incorporated, accepted_intent, observed)
    return dict(status="ordinary_proposal" if proposed else "conflict", proposed=proposed)


def pause(directory, prefix, selected):
    if prefix == selected:
        write(directory / "paused.json", dict(prefix=prefix, pid=os.getpid()))
        while True:
            signal.pause()


class Refusal(Exception):
    pass


def validate(directory, identity, token, complete=True):
    directory = Path(directory)
    required = ["authority-link.json", "manifest.json", "operation.json", "bindings.json", "original-checkpoint.json"]
    for name in required:
        if not (directory / name).exists():
            raise Refusal("missing:" + name)
    authority = read(read(directory / "authority-link.json")["path"])
    if authority["token"] != token or authority["owner"] != str(directory.resolve()):
        raise Refusal("stale_custody")
    manifest, operation, binding = (read(directory / name) for name in ["manifest.json", "operation.json", "bindings.json"])
    intent = operation["intent"]
    if identity != manifest["id"] or identity != intent["id"]:
        raise Refusal("operation_identity")
    if digest(intent) != manifest["digest"]:
        raise Refusal("frozen_intent_changed")
    if binding != intent["binding"]:
        raise Refusal("binding_changed")
    if operation["state"] not in ("planned", "indeterminate", "acknowledged", "complete"):
        raise Refusal("invalid_state")
    git = Git(directory / "repo")
    if read(directory / "original-checkpoint.json") != intent["captured_checkpoint"]:
        raise Refusal("captured_checkpoint_changed")
    for key in ["input", "result"]:
        if not git.valid_commit(intent[key]) or git.ref("refs/retained/" + key) != intent[key]:
            raise Refusal("missing_retained_" + key)
    if complete and operation["state"] == "complete":
        verify_result(directory, operation)
    return operation


def expected_checkpoint(intent):
    return {key: intent[key] for key in ("id", "input", "result", "continuation", "captured_checkpoint")}


def verify_result(directory, operation):
    intent = operation["intent"]
    path = directory / "result-checkpoint.json"
    if not path.exists() or read(path) != expected_checkpoint(intent):
        raise Refusal("invalid_completed_checkpoint")
    git = Git(directory / "repo")
    if git.ref(intent["continuation"]) != intent["result"]:
        raise Refusal("invalid_completed_attachment")
    expected = dict(id=intent["id"], digest=digest(intent), head=intent["result"])
    if operation.get("receipt") != expected:
        raise Refusal("invalid_completed_receipt")


def worker(directory, identity, token, selected=None, reconcile=False, effect="full"):
    directory = Path(directory).resolve()
    authority_path = Path(read(directory / "authority-link.json")["path"])
    with owner(authority_path.with_suffix(".lock")):
        try:
            operation = validate(directory, identity, token)
            intent = operation["intent"]
            pause(directory, "validated", selected)
            if operation["state"] == "planned":
                operation["state"] = "indeterminate"
                write(directory / "operation.json", operation)
                pause(directory, "marked", selected)
                provider = Path(intent["provider"])
                with owner(provider / "store.lock"):
                    store = read(provider / "state.json")
                    remote = Git(provider / "repo")
                    if remote.ref("refs/heads/A") != intent["expected"]:
                        raise Refusal("lease_mismatch_after_intent_mark")
                    store["requests"].append(dict(id=identity, digest=digest(intent)))
                    write(provider / "state.json", store)
                    pause(directory, "request_logged", selected)
                    remote.run("update-ref", "refs/heads/A", intent["result"], intent["expected"])
                    pause(directory, "provider_head", selected)
                    if effect == "partial":
                        return dict(status="unknown_partial")
                    remote.run("update-ref", "refs/archives/" + identity, intent["result"], ZERO)
                    pause(directory, "provider_archive", selected)
                    receipt = dict(id=identity, digest=digest(intent), head=intent["result"])
                    store["receipts"].append(receipt)
                    write(provider / "state.json", store)
                    pause(directory, "provider_receipt", selected)
                operation["state"], operation["receipt"] = "acknowledged", receipt
                write(directory / "operation.json", operation)
            elif operation["state"] == "indeterminate":
                receipt = dict(id=identity, digest=digest(intent), head=intent["result"])
                store = read(Path(intent["provider"]) / "state.json")
                if not reconcile or store["receipts"].count(receipt) != 1:
                    return dict(status="blocked_unknown_no_resend")
                operation["state"], operation["receipt"] = "acknowledged", receipt
                write(directory / "operation.json", operation)
            pause(directory, "acknowledged", selected)
            if operation["state"] == "acknowledged":
                git = Git(directory / "repo")
                actual = git.ref(intent["continuation"])
                if actual and actual != intent["result"]:
                    raise Refusal("result_attachment_collision")
                if not actual:
                    git.run("update-ref", intent["continuation"], intent["result"], ZERO)
                pause(directory, "result_ref", selected)
                checkpoint = expected_checkpoint(intent)
                path = directory / "result-checkpoint.json"
                if path.exists() and read(path) != checkpoint:
                    raise Refusal("result_checkpoint_collision")
                write(path, checkpoint)
                pause(directory, "result_checkpoint", selected)
                operation["state"] = "complete"
                write(directory / "operation.json", operation)
            pause(directory, "complete", selected)
            validate(directory, identity, token)
            return dict(status="complete")
        except (Refusal, KeyError, ValueError, FileNotFoundError) as error:
            return dict(status="refused", reason=str(error))


if __name__ == "__main__":
    result = worker(sys.argv[1], sys.argv[2], sys.argv[3],
                    selected=sys.argv[4] if len(sys.argv) > 4 else None,
                    reconcile="--reconcile" in sys.argv)
    print(json.dumps(result))
    sys.exit(0 if result["status"] == "complete" else 3)
