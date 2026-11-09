import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path('/lab/protocol-durable')


def load(name, relative, pins):
    source = ROOT/'original'/relative
    if hashlib.sha256(source.read_bytes()).hexdigest() != pins[relative]:
        raise RuntimeError('pinned_original_changed:'+relative)
    spec = importlib.util.spec_from_file_location(name,source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    if Path(__file__).resolve().parent != ROOT or sys.platform != 'linux':
        raise RuntimeError('root_owned_Linux_location_required')
    pins = json.loads((ROOT/'ORIGINAL-PINS.json').read_text())
    load('oracle','oracle.py',pins)
    controller = load('durable_original_controller','root_controller.py',pins)
    controller.ROOT, controller.OUT = ROOT, ROOT/'actual-results'
    controller.main()


if __name__ == '__main__':
    main()
