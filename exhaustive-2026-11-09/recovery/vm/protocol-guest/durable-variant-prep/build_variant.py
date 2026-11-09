import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('/lab/protocol-durable')
BASE = Path('/lab/protocol-guest')
STAGE_LIMIT, ARCHIVE_LIMIT, LAB_LIMIT = 96*1024*1024, 48*1024*1024, 2*1024*1024*1024


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def size(path):
    return sum(p.stat().st_size for p in path.rglob('*') if p.is_file() and not p.is_symlink())


def inventory(path):
    return [dict(path=str(p.relative_to(path)),bytes=p.stat().st_size,sha256=sha(p))
            for p in sorted(path.rglob('*')) if p.is_file()]


def sync_directory(path):
    fd = os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def main():
    if Path(__file__).resolve().parent != ROOT or sys.platform != 'linux' or sys.version_info[:2] != (3,10):
        raise RuntimeError('root_owned_fresh_Linux_Python3.10_location_required')
    pins = json.loads((ROOT/'ORIGINAL-PINS.json').read_text())
    for name, expected in pins.items():
        if sha(ROOT/'original'/name) != expected or sha(BASE/name) != expected:
            raise RuntimeError('original_source_changed:'+name)
    receipt = json.loads((BASE/'BUILD-RECEIPT.json').read_text())
    stage, archive = ROOT/'initramfs', ROOT/'test-initramfs.gz'
    if stage.exists() or archive.exists() or (ROOT/'BUILD-RECEIPT.json').exists():
        raise RuntimeError('fresh_build_outputs_required')
    if inventory(BASE/'initramfs') != receipt['stage_files']:
        raise RuntimeError('original_runtime_stage_changed')
    if sha(BASE/'test-initramfs.gz') != receipt['initrd_sha256']:
        raise RuntimeError('original_runtime_image_changed')
    if size(Path('/lab')) + STAGE_LIMIT + ARCHIVE_LIMIT > LAB_LIMIT:
        raise RuntimeError('total_storage_preflight_refused')
    shutil.copytree(BASE/'initramfs',stage,symlinks=True)
    runtime = stage/'opt/protocol'
    for name in ('guest.py','source/protocol.py','source/run.py'):
        if sha(runtime/name) != pins[name]:
            raise RuntimeError('copied_original_runtime_source_changed:'+name)
    if sha(stage/'init') != pins['init']:
        raise RuntimeError('copied_original_init_changed')
    for name in ('durable_refs.py','variant_entry.py','ORIGINAL-PINS.json'):
        shutil.copy2(ROOT/name,runtime/name)
    old = '/usr/bin/python3 /opt/protocol/guest.py "$phase" "$prefix" || exit 2'
    new = '/usr/bin/python3 /opt/protocol/variant_entry.py "$phase" "$prefix" || exit 2'
    init = (stage/'init').read_text()
    if init.count(old) != 1:
        raise RuntimeError('exact_original_entry_line_missing')
    (stage/'init').write_text(init.replace(old,new))
    (stage/'init').chmod(0o755)
    if size(stage) > STAGE_LIMIT:
        raise RuntimeError('stage_bound_exceeded')
    listing = subprocess.run(['find','.','-print0'],cwd=stage,capture_output=True,check=True)
    packed = subprocess.run(['cpio','--null','-o','-H','newc'],cwd=stage,input=listing.stdout,capture_output=True,check=True)
    with archive.open('xb') as stream:
        with gzip.GzipFile(fileobj=stream,mode='wb',compresslevel=1,mtime=0) as compressed:
            compressed.write(packed.stdout)
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(ROOT)
    if archive.stat().st_size > ARCHIVE_LIMIT or size(Path('/lab')) > LAB_LIMIT:
        raise RuntimeError('archive_or_total_storage_bound_exceeded')
    record = dict(original_build_receipt_sha256=sha(BASE/'BUILD-RECEIPT.json'), original_pins=pins,
        copied_original_stage_bytes=receipt['stage_bytes'], stage_bytes=size(stage),
        initrd_bytes=archive.stat().st_size,initrd_sha256=sha(archive),
        kernel_sha256=sha(Path('/lab/boot/Image-virt')),stage_files=inventory(stage),
        source_hashes={name:sha(ROOT/name) for name in ('durable_refs.py','variant_entry.py','build_variant.py','controller_entry.py','ORIGINAL-PINS.json')},
        cpio_stderr=packed.stderr.decode(),limits=dict(stage=STAGE_LIMIT,archive=ARCHIVE_LIMIT,lab=LAB_LIMIT),
        scope='Copies verified existing runtime; only guest entry path and added loose-ref wrapper differ; no installs/compiler/guest launch')
    with (ROOT/'BUILD-RECEIPT.json').open('x') as stream:
        json.dump(record,stream,indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(ROOT)


if __name__ == '__main__':
    main()
