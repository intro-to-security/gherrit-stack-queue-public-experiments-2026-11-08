import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
SIZE = 65536
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
NAMES = ["current.json", "next.json", "result-old.json", "result-new.json",
         "intent.json", "ref.json", "checkpoint.json", "done.json"]


def canonical(value):
    return json.dumps(value, separators=(",", ":")).encode()


def payload(generation):
    return "".join(ALPHABET[(index * 7 + generation * 11) % len(ALPHABET)] for index in range(SIZE))


def record(generation):
    contents = payload(generation)
    return canonical(dict(generation=generation, value="old-complete" if generation == 0 else "new-complete",
                          payload=contents, payload_sha256=hashlib.sha256(contents.encode()).hexdigest()))


def result_hash(generation):
    return hashlib.sha256(record(generation)).hexdigest()


def pointer(generation):
    return canonical(dict(generation=generation, operation="extension-" + str(generation), result_sha256=result_hash(generation)))


INTENT = canonical(dict(operation="extension-1", **{"from":0,"to":1}, result_sha256=result_hash(1)))
DONE = canonical(dict(operation="extension-1", result_sha256=result_hash(1), accepted_generation=1))


def describe(contents):
    if contents is None:
        return dict(present=False, valid=False)
    result = dict(present=True, bytes=len(contents), sha256=hashlib.sha256(contents).hexdigest(), valid=False)
    try:
        value = json.loads(contents)
        result["generation"] = value.get("generation")
        if type(value.get("generation")) is int and value["generation"] in (0, 1):
            generation = value["generation"]
            result["full_expected_bytes"] = contents == record(generation)
            text = value.get("payload")
            result["checksum_matches"] = isinstance(text, str) and hashlib.sha256(text.encode()).hexdigest() == value.get("payload_sha256")
            result["valid"] = result["full_expected_bytes"] and result["checksum_matches"]
    except (ValueError, UnicodeError, AttributeError) as error:
        result["parse_error"] = str(error)
    return result


def parse(log):
    records = {}
    for line in log.splitlines():
        if line.startswith("RECORDHEX "):
            _, name, size, encoded = line.split(" ", 3)
            contents = bytes.fromhex(encoded)
            if int(size) != len(contents):
                raise ValueError("record_length_mismatch")
        elif line.startswith("ABSENTHEX "):
            _, name = line.split(" ", 1)
            contents = None
        else:
            continue
        if name not in NAMES or name in records:
            raise ValueError("unexpected_or_duplicate_record")
        records[name] = contents
    if set(records) != set(NAMES):
        raise ValueError("incomplete_record_observation")
    return records


def classify(records):
    active = describe(records["current.json"])
    temporary = describe(records["next.json"])
    details = dict(active=active, unpublished_temporary=temporary,
                   scope="local file protocol only; no hosted dispatch authority")
    if not active["valid"]:
        return dict(kind="refuse-invalid-active", **details)
    if records["intent.json"] is None:
        return dict(kind="active-valid-ignore-unpublished-temp", **details)
    if records["intent.json"] != INTENT:
        return dict(kind="refuse-invalid-intent", **details)
    ref = next((generation for generation in (0, 1) if records["ref.json"] == pointer(generation)), None)
    checkpoint = next((generation for generation in (0, 1) if records["checkpoint.json"] == pointer(generation)), None)
    retained = records["result-new.json"] == record(1) and describe(records["result-new.json"])["valid"]
    details.update(ref_generation=ref, checkpoint_generation=checkpoint, retained_result_valid=retained)
    if records["done.json"] is not None:
        valid = records["done.json"] == DONE and ref == 1 and checkpoint == 1 and retained
        return dict(kind="done-validated" if valid else "refuse-invalid-completion", **details)
    if ref is None or checkpoint is None or not retained:
        return dict(kind="refuse-invalid-pending-evidence", **details)
    if (ref, checkpoint) == (0, 0):
        return dict(kind="pending-intent-only", **details)
    if (ref, checkpoint) == (1, 0):
        return dict(kind="pending-output-prefix", **details)
    if (ref, checkpoint) == (1, 1):
        return dict(kind="pending-finalization", **details)
    return dict(kind="refuse-invalid-output-order", **details)


EXPECTED_KINDS = {1:"active-valid-ignore-unpublished-temp",2:"active-valid-ignore-unpublished-temp",
                  3:"active-valid-ignore-unpublished-temp",4:"active-valid-ignore-unpublished-temp",
                  5:"active-valid-ignore-unpublished-temp",6:"refuse-invalid-active",
                  7:"pending-intent-only",8:"pending-output-prefix",9:"pending-finalization",
                  10:"done-validated",11:"refuse-invalid-completion",12:"refuse-invalid-completion"}


def check_case(stage, records):
    verdict = classify(records)
    checks = dict(expected_kind=verdict["kind"] == EXPECTED_KINDS[stage],
                  retained_old_exact=records["result-old.json"] == record(0))
    if stage in (1, 2, 5) or stage >= 7:
        checks["unchanged_active_old_exact"] = records["current.json"] == record(0)
    if stage == 3:
        checks["rename_active_old_or_new_exact"] = records["current.json"] in (record(0), record(1))
    if stage == 4:
        checks["directory_synced_new_exact"] = records["current.json"] == record(1)
        checks["renamed_temporary_absent"] = records["next.json"] is None
    if stage == 5:
        checks["injected_unpublished_corruption_detected"] = not describe(records["next.json"])["valid"]
        checks["injected_unpublished_bytes_exact"] = records["next.json"] == record(1)[:len(record(1))//2]
    if stage == 6:
        checks["injected_active_corruption_detected"] = not describe(records["current.json"])["valid"]
        checks["injected_active_bytes_exact"] = records["current.json"] == record(1)[:len(record(1))//2]
    if stage == 11:
        checks["false_completion_control_exact"] = records["done.json"] == DONE and records["ref.json"] == pointer(1) and records["checkpoint.json"] == pointer(0)
    if stage == 12:
        retained = describe(records["result-new.json"])
        checks["valid_JSON_checksum_corruption_observed"] = retained.get("checksum_matches") is False and len(records["result-new.json"] or b"") == len(record(1))
    return dict(stage=stage, verdict=verdict, checks=checks, expected=all(checks.values()))


def fsck_diagnostics(result):
    combined = result["stdout"] + "\n" + result["stderr"]
    lines = [line for line in combined.splitlines() if re.search(r"warning|wrong|error|fix\?|skipping.*recover", line, re.I)]
    return dict(exit=result["exit"], diagnostic_lines=lines,
                clean_diagnostics=result["exit"] == 0 and not lines,
                scope="After stated inspector path; exit zero alone is insufficient")


def fixture(stage):
    values = {name:None for name in NAMES}
    values.update({"current.json":record(0),"result-old.json":record(0),"ref.json":pointer(0),"checkpoint.json":pointer(0)})
    if stage in (2, 3): values["next.json"] = record(1)
    if stage == 4: values["current.json"] = record(1)
    if stage == 5: values["next.json"] = record(1)[:len(record(1))//2]
    if stage == 6: values["current.json"] = record(1)[:len(record(1))//2]
    if stage >= 7:
        values["result-new.json"], values["intent.json"] = record(1), INTENT
    if stage >= 8: values["ref.json"] = pointer(1)
    if stage >= 9: values["checkpoint.json"] = pointer(1)
    if stage >= 10: values["done.json"] = DONE
    if stage == 11: values["checkpoint.json"] = pointer(0)
    if stage == 12:
        corrupted = bytearray(record(1))
        offset = corrupted.index(b'"payload":"') + len(b'"payload":"')
        corrupted[offset] = ord('b') if corrupted[offset] == ord('a') else ord('a')
        values["result-new.json"] = bytes(corrupted)
    return values


def generate():
    values = dict(PAYLOAD_SIZE=SIZE, OLD_PAYLOAD_SHA=hashlib.sha256(payload(0).encode()).hexdigest(),
                  NEW_PAYLOAD_SHA=hashlib.sha256(payload(1).encode()).hexdigest(),
                  OLD_RECORD_SHA=result_hash(0), NEW_RECORD_SHA=result_hash(1))
    header = "\n".join("#define " + key + " " + (str(value) if isinstance(value,int) else json.dumps(value)) for key,value in values.items()) + "\n"
    (ROOT / "expected.h").write_text(header)
    (ROOT / "EXPECTED.json").write_text(json.dumps(dict(constants=values, record_sizes={str(g):len(record(g)) for g in (0,1)}, expected_kinds=EXPECTED_KINDS),indent=2)+"\n")


def offline():
    cases = [check_case(stage, fixture(stage)) for stage in range(1,13)]
    bad_done = [dict(stage=stage, bad_done_flag_accepts=fixture(stage)["done.json"] is not None,
                     exact_oracle=classify(fixture(stage))["kind"]) for stage in (11,12)]
    damaged = fixture(10)
    value = json.loads(damaged["ref.json"])
    value["result_sha256"] = "0"*64
    damaged["ref.json"] = canonical(value)
    bad_generation = dict(bad_generation_only_accepts=json.loads(damaged["ref.json"])["generation"] == json.loads(damaged["checkpoint.json"])["generation"] == 1,
                          exact_oracle=classify(damaged)["kind"])
    wrong_value = json.loads(record(1))
    wrong_value["value"] = "wrong-complete"
    full_value_probe = describe(canonical(wrong_value))
    v3 = ROOT.parent / "7e278a42e7" / "evidence" / "results-v3"
    actual = json.loads((v3 / "RESULTS.json").read_text())
    old, new = dict(generation=0,value="old-complete"),dict(generation=1,value="new-complete")
    audits = []
    for case in actual["cases"]:
        stage, records = case["stage"],case["records"]
        checks = dict(current_full_value=records["/state/current.json"] == (new if stage in (4,5) else old),
                      ref_full_value=records["/state/ref.json"] == (new if stage>=7 else old),
                      checkpoint_full_value=records["/state/checkpoint.json"] == (new if stage==8 else old),
                      temporary_full_value=records["/state/next.json"] == (new if stage in (2,3) else None),
                      intent_full_value=records["/state/intent.json"] == ({"from":0,"to":1,"value":"new-complete"} if stage>=6 else None))
        diagnostics = fsck_diagnostics(json.loads((v3 / ("case-"+str(stage)+"-fsck.json")).read_text()))
        audits.append(dict(stage=stage,checks=checks,diagnostics=diagnostics))
    seventh = actual["cases"][6]["records"]
    bad_ref = dict(actual_stage=7, bad_reference_only_accepts=seventh["/state/ref.json"]["generation"]==1,
                   correct_pending=seventh["/state/ref.json"] != seventh["/state/checkpoint.json"],
                   source=str(v3 / "case-7-result.json"))
    boot_checks = []
    for stage in range(1,9):
        for phase in ("cut","recover"):
            receipt = json.loads((v3 / ("case-"+str(stage)+"-"+phase+".receipt.json")).read_text())
            expected = "BARRIER CUT"+str(stage) if phase=="cut" else "BARRIER RECOVERED"
            boot_checks.append(dict(stage=stage,phase=phase,pid=receipt["pid"],
                                   valid=receipt["exit"]==-9 and receipt["reached"] and receipt["barrier"]==expected))
    report = dict(cases=cases, bad_done_controls=bad_done, bad_generation_control=bad_generation,
                  retained_actual_v3=audits, actual_v3_boot_checks=boot_checks, bad_classifier_on_actual_v3=bad_ref,
                  full_value_probe=full_value_probe,
                  all_expected=all(case["expected"] for case in cases) and all(all(a["checks"].values()) for a in audits)
                    and all(row["valid"] for row in boot_checks)
                    and bad_ref["correct_pending"] and bad_generation["exact_oracle"] == "refuse-invalid-completion"
                    and full_value_probe["checksum_matches"] and not full_value_probe["valid"],
                  guest_execution=False, scope="Offline exact-byte/checksum/classifier checks plus retained actual v3 records")
    (ROOT / "OFFLINE-CHECKS.json").write_text(json.dumps(report,indent=2)+"\n")
    if not report["all_expected"] or not bad_ref["bad_reference_only_accepts"] or not bad_generation["bad_generation_only_accepts"]:
        raise SystemExit("offline checks failed")
    print(json.dumps(dict(offline_cases=12, all_expected=True, actual_v3_cases=8, unsafe_controls=5)))


if __name__ == "__main__":
    if sys.argv[1] == "generate": generate()
    elif sys.argv[1] == "check": offline()
    else: raise SystemExit("unknown action")
