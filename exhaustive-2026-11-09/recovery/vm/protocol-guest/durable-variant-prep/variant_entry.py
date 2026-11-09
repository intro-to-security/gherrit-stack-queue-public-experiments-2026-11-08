import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PINS = json.loads((ROOT / "ORIGINAL-PINS.json").read_text())


def main():
    original = ROOT / "guest.py"
    if hashlib.sha256(original.read_bytes()).hexdigest() != PINS["guest.py"]:
        raise RuntimeError("original_guest_changed")
    spec = importlib.util.spec_from_file_location("original_guest",original)
    guest = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guest)
    import durable_refs
    original_emit = guest.emit
    installed = False
    def emit(kind,value):
        nonlocal installed
        if kind == "runtime":
            value = dict(value,original_instrumentation=value["instrumentation"],
                               instrumentation="Original serial-only pause plus scoped successful update-ref file and parent-directory fsync barriers",
                               durable_ref_variant={"wrapper_sha256":hashlib.sha256((ROOT/"durable_refs.py").read_bytes()).hexdigest(),
                                                    "entry_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                                    "original_guest_sha256":PINS["guest.py"],
                                                    "scope":"Scoped successful loose-ref update barriers; original worker/oracle unchanged"})
        original_emit(kind,value)
        if kind in ("baseline","before_recovery"):
            if installed:
                raise RuntimeError("duplicate_barrier_installation")
            record = value["files"]["operation.json"]
            data = bytes.fromhex(record["hex"])
            if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
                raise RuntimeError("invalid_frozen_intent_snapshot")
            protocol = sys.modules["protocol"]
            durable_refs.install(protocol,Path(value["directory"]),json.loads(data)["intent"],
                report=lambda record:print("DURABLE_REF "+json.dumps(record,sort_keys=True),flush=True))
            installed = True
    guest.emit = emit
    try:
        guest.main(*sys.argv[1:])
    except Exception as error:
        original_emit("harness_failure",{"type":type(error).__name__,"error":str(error)})
        raise


if __name__ == "__main__":
    main()
