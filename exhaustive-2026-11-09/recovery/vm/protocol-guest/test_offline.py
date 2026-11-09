import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

import guest
import oracle

ROOT = Path(__file__).resolve().parent


def raw(value):
    data = json.dumps(value, sort_keys=True).encode()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "hex": data.hex()}


def command(data):
    return {"argv": ["offline-fixture"], "exit": 0, "stdout_hex": data.hex(), "stderr_hex": ""}


def git_object(kind, body):
    oid = hashlib.sha1(kind.encode() + b" " + str(len(body)).encode() + b"\0" + body).hexdigest()
    return {"oid": oid, "type": kind, "size": len(body), "read": command(body)}


def model(prefix):
    first = git_object("commit", b"offline-old\n")
    second = git_object("commit", b"offline-result\n")
    old, result = first["oid"], second["oid"]
    intent = {"id": "op-offline", "input": old, "result": result, "expected": old,
              "continuation": "refs/retained/completed-offline", "provider": "/state/scope/offline/provider",
              "binding": {"repository": "local-fixture", "change": "A", "head": "A", "review": 1},
              "captured_checkpoint": {"incorporated": old, "accepted_local": result}, "scope": ["head:A"]}
    request = {"id": intent["id"], "digest": oracle.digest(intent)}
    receipt = dict(request, head=result)

    def repo(refs):
        return {"refs": command("".join(k + " " + v + "\n" for k, v in refs.items()).encode()),
                "inventory": command("".join(f"{v['oid']} {v['type']} {v['size']}\n" for v in (first, second)).encode()),
                "objects": [copy.deepcopy(first), copy.deepcopy(second)], "fsck": command(b"")}

    baseline = {"directory": "/state/scope/offline", "files": {"operation.json": raw({"intent": intent, "state": "planned"}),
                           "authority.json": raw({"owner": "/state/scope/offline", "token": "epoch-1"}),
                           "authority-link.json": raw({"path": "/state/scope/offline/authority.json"}),
                           "manifest.json": raw({"id": intent["id"], "digest": oracle.digest(intent)}),
                           "bindings.json": raw(intent["binding"]),
                           "original-checkpoint.json": raw(intent["captured_checkpoint"]),
                           "provider/state.json": raw({"requests": [], "receipts": []})},
                "repos": {"local": repo({"refs/retained/input": old, "refs/retained/result": result}),
                          "provider": repo({"refs/heads/A": old})}}
    before = copy.deepcopy(baseline)
    index = oracle.PREFIXES.index(prefix)
    state = "planned" if index == 0 else "indeterminate" if index < 6 else "acknowledged" if index < 9 else "complete"
    operation = {"intent": intent, "state": state}
    if index >= 6:
        operation["receipt"] = receipt
    before["files"]["operation.json"] = raw(operation)
    before["files"]["provider/state.json"] = raw({"requests": [request] if index >= 2 else [], "receipts": [receipt] if index >= 5 else []})
    if index >= 8:
        before["files"]["result-checkpoint.json"] = raw({key: intent[key] for key in ("id", "input", "result", "continuation", "captured_checkpoint")})
    after = copy.deepcopy(before)
    if prefix in oracle.UNKNOWN_PREFIXES:
        returned = {"status": "blocked_unknown_no_resend"}
    else:
        after["files"]["operation.json"] = raw({"intent": intent, "state": "complete", "receipt": receipt})
        after["files"]["result-checkpoint.json"] = raw({key: intent[key] for key in ("id", "input", "result", "continuation", "captured_checkpoint")})
        after["files"]["provider/state.json"] = raw({"requests": [request], "receipts": [receipt]})
        after["repos"]["local"] = repo({"refs/retained/input": old, "refs/retained/result": result, intent["continuation"]: result})
        after["repos"]["provider"] = repo({"refs/heads/A": result, "refs/archives/" + intent["id"]: result})
        returned = {"status": "complete"}
    return baseline, before, after, returned


class OfflineControls(unittest.TestCase):
    def test_invalid_baseline_cannot_authorize_complete(self):
        for name, value in [("bindings.json", {"review": 999}),
                            ("authority.json", {"owner": "/foreign", "token": "wrong"}),
                            ("original-checkpoint.json", {"accepted_local": "foreign"})]:
            baseline, before, after, returned = model("after_return")
            for snapshot in (baseline, before, after):
                snapshot["files"][name] = raw(value)
            self.assertFalse(oracle.check("after_return", baseline, before, after, returned)["passed"])

    def test_all_planned_prefixes(self):
        for prefix in oracle.PREFIXES:
            with self.subTest(prefix=prefix):
                self.assertTrue(oracle.check(prefix, *model(prefix))["passed"])

    def test_each_complete_evidence_component_matters(self):
        for name in ("continuation", "checkpoint", "receipt", "provider_head", "provider_archive", "request_identity", "duplicate_request", "object_bytes"):
            with self.subTest(name=name):
                baseline, before, after, returned = model("after_return")
                operation = oracle.document(after, "operation.json")
                intent = operation["intent"]
                if name == "continuation":
                    refs = after["repos"]["local"]["refs"]
                    refs["stdout_hex"] = bytes.fromhex(refs["stdout_hex"]).replace(intent["continuation"].encode(), b"refs/retained/other").hex()
                elif name == "checkpoint":
                    after["files"]["result-checkpoint.json"] = raw({"result": intent["input"]})
                elif name == "receipt":
                    operation["receipt"]["id"] = "foreign"
                    after["files"]["operation.json"] = raw(operation)
                elif name in ("provider_head", "provider_archive"):
                    refs = after["repos"]["provider"]["refs"]
                    selected = "refs/heads/A" if name == "provider_head" else "refs/archives/" + intent["id"]
                    data = bytes.fromhex(refs["stdout_hex"]).decode().splitlines()
                    refs["stdout_hex"] = ("\n".join(line for line in data if not line.startswith(selected + " ")) + "\n").encode().hex()
                elif name in ("request_identity", "duplicate_request"):
                    store = oracle.document(after, "provider/state.json")
                    if name == "request_identity": store["requests"][0]["id"] = "foreign"
                    else: store["requests"].append(dict(store["requests"][0]))
                    after["files"]["provider/state.json"] = raw(store)
                else:
                    after["repos"]["provider"]["objects"][0]["read"]["stdout_hex"] = b"corrupt".hex()
                self.assertFalse(oracle.check("after_return", baseline, before, after, returned)["passed"])

    def test_unknown_cannot_resend(self):
        baseline, before, after, returned = model("marked")
        store = oracle.document(after, "provider/state.json")
        store["requests"].append({"id": "second-dispatch", "digest": "wrong"})
        after["files"]["provider/state.json"] = raw(store)
        self.assertFalse(oracle.check("marked", baseline, before, after, returned)["passed"])

    def test_source_bytes_and_injection_boundary(self):
        pins = json.loads((ROOT / "SOURCE-PINS.json").read_text())
        for pin in pins:
            self.assertEqual(hashlib.sha256((ROOT / pin["retained"]).read_bytes()).hexdigest(), pin["sha256"])
            self.assertEqual(guest.PINS[Path(pin["retained"]).name], pin["sha256"])
        tree = ast.parse((ROOT / "guest.py").read_text())
        prototype_assignments = [ast.unparse(target) for node in ast.walk(tree) if isinstance(node, ast.Assign)
                                 for target in node.targets if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "p"]
        self.assertEqual(prototype_assignments, ["p.pause"])

    def test_ldd_parser_and_missing_dependency(self):
        spec = importlib.util.spec_from_file_location("build_recipe", ROOT / "build-root.py")
        recipe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(recipe)
        self.assertEqual(recipe.ldd_paths("libc.so.6 => /lib/aarch64-linux-gnu/libc.so.6 (0x1)\n /lib/ld-linux-aarch64.so.1 (0x2)\n"),
                         {Path("/lib/aarch64-linux-gnu/libc.so.6"), Path("/lib/ld-linux-aarch64.so.1")})
        with self.assertRaises(RuntimeError): recipe.ldd_paths("libmissing => not found")


if __name__ == "__main__":
    unittest.main()
