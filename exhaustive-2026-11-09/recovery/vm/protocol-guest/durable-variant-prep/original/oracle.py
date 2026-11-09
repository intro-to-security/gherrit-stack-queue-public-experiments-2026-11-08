"""Independent, pure checks over actual raw guest Git/JSON readbacks."""
import hashlib
import json

PREFIXES = ("validated", "marked", "request_logged", "provider_head",
            "provider_archive", "provider_receipt", "acknowledged", "result_ref",
            "result_checkpoint", "complete", "after_return")
UNKNOWN_PREFIXES = {"marked", "request_logged", "provider_head", "provider_archive"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def document(snapshot, name):
    record = snapshot["files"][name]
    data = bytes.fromhex(record["hex"])
    if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError("invalid_raw_record:" + name)
    return json.loads(data)


def output(record):
    if record["exit"]:
        raise ValueError("failed_git_read:" + json.dumps(record["argv"]))
    return bytes.fromhex(record["stdout_hex"])


def repository(snapshot, role):
    repo = snapshot["repos"][role]
    refs = dict(line.split(" ", 1) for line in output(repo["refs"]).decode().splitlines())
    inventory = {(oid, kind, int(size)) for oid, kind, size in
                 (line.split() for line in output(repo["inventory"]).decode().splitlines())}
    objects = {}
    for record in repo["objects"]:
        data = output(record["read"])
        oid, kind, size = record["oid"], record["type"], record["size"]
        actual = hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if len(data) != size or actual != oid or oid in objects:
            raise ValueError("invalid_git_object:" + oid)
        objects[oid] = {"type": kind, "hex": data.hex()}
    if inventory != {(oid, item["type"], len(bytes.fromhex(item["hex"]))) for oid, item in objects.items()}:
        raise ValueError("git_inventory_mismatch:" + role)
    if any(oid not in objects for oid in refs.values()):
        raise ValueError("ref_object_missing:" + role)
    if repo["fsck"]["exit"] != 0:
        raise ValueError("git_fsck_failed:" + role)
    return refs, objects


def check(prefix, baseline, before, after, result):
    if prefix not in PREFIXES:
        raise ValueError("unknown_cut_prefix")
    checks = []

    def require(name, value):
        checks.append({"name": name, "passed": bool(value)})

    try:
        intent = document(baseline, "operation.json")["intent"]
        directory = baseline["directory"]
        require("same_fixture_directory", isinstance(directory, str) and before["directory"] == directory and after["directory"] == directory)
        require("captured_provider_directory", intent["provider"] == directory + "/provider")
        require("binding_agrees_with_frozen_intent", document(baseline, "bindings.json") == intent["binding"])
        require("checkpoint_agrees_with_frozen_intent", document(baseline, "original-checkpoint.json") == intent["captured_checkpoint"])
        authority = document(baseline, "authority.json")
        require("captured_custody_owner_and_token", authority.get("owner") == directory and authority.get("token") == "epoch-1")
        require("captured_authority_path", document(baseline, "authority-link.json") == {"path": directory + "/authority.json"})
        identity = intent["id"]
        expected_receipt = {"id": identity, "digest": digest(intent), "head": intent["result"]}
        expected_request = {"id": identity, "digest": digest(intent)}
        operation = document(after, "operation.json")
        prior_operation = document(before, "operation.json")
        prior_store = document(before, "provider/state.json")
        store = document(after, "provider/state.json")
        index = PREFIXES.index(prefix)
        expected_state = "planned" if index == 0 else "indeterminate" if index < 6 else "acknowledged" if index < 9 else "complete"
        require("durable_prefix_operation", prior_operation["state"] == expected_state and prior_operation["intent"] == intent)
        require("durable_prefix_requests", prior_store["requests"] == ([expected_request] if index >= 2 else []))
        require("durable_prefix_receipts", prior_store["receipts"] == ([expected_receipt] if index >= 5 else []))
        if index >= 8:
            require("durable_prefix_checkpoint", document(before, "result-checkpoint.json") == {key: intent[key] for key in ("id", "input", "result", "continuation", "captured_checkpoint")})
        local_refs, local_objects = repository(after, "local")
        remote_refs, remote_objects = repository(after, "provider")
        _, original_local = repository(baseline, "local")
        _, original_remote = repository(baseline, "provider")
        require("exact_frozen_intent", operation["intent"] == intent)
        for name in ("authority.json", "authority-link.json", "manifest.json", "bindings.json", "original-checkpoint.json"):
            require("unchanged_" + name, document(after, name) == document(baseline, name))
        require("manifest_binds_intent", document(after, "manifest.json") == {"id": identity, "digest": digest(intent)})
        require("local_all_original_git_objects_exact", local_objects == original_local)
        require("provider_all_original_git_objects_exact", remote_objects == original_remote)
        for role in ("local", "provider"):
            require("unchanged_fsck_diagnostics_" + role,
                    all(after["repos"][role]["fsck"][key] == baseline["repos"][role]["fsck"][key]
                        for key in ("exit", "stdout_hex", "stderr_hex")))
        require("retained_input", local_refs.get("refs/retained/input") == intent["input"])
        require("retained_result", local_refs.get("refs/retained/result") == intent["result"])
        unknown = prior_operation["state"] != "planned" or bool(prior_store["requests"] or prior_store["receipts"])
        if unknown:
            require("unknown_effect_never_resends", store["requests"] == prior_store["requests"])
        else:
            require("new_dispatch_at_most_once", store["requests"] == [expected_request])
        if result.get("status") == "complete":
            checkpoint = {key: intent[key] for key in ("id", "input", "result", "continuation", "captured_checkpoint")}
            require("completed_operation_state", operation["state"] == "complete")
            require("exact_local_continuation", local_refs.get(intent["continuation"]) == intent["result"])
            require("exact_local_checkpoint", document(after, "result-checkpoint.json") == checkpoint)
            require("exact_local_receipt", operation.get("receipt") == expected_receipt)
            require("exact_provider_head", remote_refs.get("refs/heads/A") == intent["result"])
            require("exact_provider_archive", remote_refs.get("refs/archives/" + identity) == intent["result"])
            require("exact_single_provider_request", store["requests"] == [expected_request])
            require("exact_single_provider_receipt", store["receipts"] == [expected_receipt])
            classification = "validated_complete" if all(row["passed"] for row in checks) else "false_or_unverifiable_completion"
        else:
            require("bounded_unknown_result", result.get("status") == "blocked_unknown_no_resend")
            require("unknown_stays_indeterminate", operation["state"] == "indeterminate")
            classification = "blocked_unknown_no_resend" if all(row["passed"] for row in checks) else "recovery_failure"
        expected = "blocked_unknown_no_resend" if prefix in UNKNOWN_PREFIXES else "validated_complete"
        require("planned_prefix_expectation", classification == expected)
        return {"prefix": prefix, "passed": all(row["passed"] for row in checks), "classification": classification,
                "expected": expected, "checks": checks, "worker_result": result}
    except (KeyError, ValueError, TypeError) as error:
        return {"prefix": prefix, "passed": False, "classification": "invalid_or_missing_evidence",
                "checks": checks, "error": str(error), "worker_result": result}


def parse_serial(text):
    records = {}
    for line in text.splitlines():
        if line.startswith("PROTOCOL {"):
            record = json.loads(line[len("PROTOCOL "):])
            if record["kind"] in records:
                raise ValueError("duplicate_serial_kind:" + record["kind"])
            records[record["kind"]] = record["value"]
    return records
