"""Root-owned, one-shot guest trials of the pinned local Python/Git prototype."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import time
import oracle

ROOT = Path('/lab/protocol-guest')
OUT = ROOT / 'actual-results'
CASES = ('validated', 'after_return', 'marked', 'request_logged', 'provider_head',
         'provider_archive', 'provider_receipt', 'acknowledged', 'result_ref',
         'result_checkpoint', 'complete')
DISK_BYTES = 32 * 1024 * 1024


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(path.parent)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def bytes_under(path):
    return sum(p.stat().st_size for p in path.rglob('*') if p.is_file() and not p.is_symlink())


def archive(disk, target):
    expected = sha(disk)
    with disk.open('rb') as source, target.open('xb') as output:
        with gzip.GzipFile(fileobj=output, mode='wb', compresslevel=1, mtime=0) as compressed:
            shutil.copyfileobj(source, compressed, 1048576)
        output.flush()
        os.fsync(output.fileno())
    digest, size = hashlib.sha256(), 0
    with gzip.open(target, 'rb') as source:
        for block in iter(lambda: source.read(1048576), b''):
            digest.update(block)
            size += len(block)
    if digest.hexdigest() != expected or size != DISK_BYTES:
        raise RuntimeError('Archive does not preserve exact disk bytes')
    sync_directory(target.parent)
    return {'file': target.name, 'raw_bytes': size, 'raw_sha256': expected,
            'gzip_sha256': sha(target), 'gzip_bytes': target.stat().st_size,
            'verified_lossless': True}


def boot(disk, prefix, phase):
    log = OUT / (prefix + '-' + phase + '.log')
    command = ['qemu-system-aarch64', '-machine', 'virt', '-cpu', 'cortex-a57',
               '-accel', 'tcg', '-smp', '1', '-m', '256M', '-nographic',
               '-no-reboot', '-nic', 'none', '-kernel', '/lab/boot/Image-virt',
               '-initrd', str(ROOT / 'test-initramfs.gz'), '-append',
               'console=ttyAMA0 panic=-1 phase=' + phase + ' prefix=' + prefix,
               '-drive', 'if=none,file=' + str(disk) + ',format=raw,cache=writeback,id=d0',
               '-device', 'virtio-blk-device,drive=d0']
    save(log.with_suffix('.intent.json'), {'command': command, 'prefix': prefix,
         'phase': phase, 'utc_seconds': time.time(), 'state': 'may be started'})
    target = ('BARRIER PROTOCOL ' + (prefix if phase == 'cut' else 'CLEAN_RECOVERY_UNMOUNTED')).encode()
    data, reached, natural = b'', False, False
    deadline = time.monotonic() + 60
    with log.open('xb') as stream:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            while time.monotonic() < deadline:
                ready, _, _ = select.select([process.stdout], [], [], 1)
                if ready:
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        break
                    stream.write(chunk)
                    stream.flush()
                    data += chunk
                    if target + b'\r\n' in data or target + b'\n' in data:
                        reached = True
                        stream.flush()
                        os.fsync(stream.fileno())
                        break
                if process.poll() is not None:
                    break
        finally:
            if phase == 'recover' and reached:
                try:
                    natural = process.wait(timeout=10) == 0
                except subprocess.TimeoutExpired:
                    process.kill()
            elif process.poll() is None:
                process.kill()
            result = process.wait(timeout=10)
            rest = process.stdout.read()
            stream.write(rest)
            data += rest
            stream.flush()
            os.fsync(stream.fileno())
    save(log.with_suffix('.receipt.json'), {'pid': process.pid, 'exit': result,
         'target': target.decode(), 'reached': reached, 'natural_shutdown': natural,
         'bytes': len(data), 'utc_seconds': time.time()})
    if not reached or phase == 'recover' and not natural:
        raise RuntimeError('Guest premise failed; retained disk/logs, no retry: ' + log.name)
    return oracle.parse_serial(data.decode(errors='replace'))


def main():
    grant = json.loads((ROOT / 'RUNTIME-GRANT.json').read_text())
    if grant.get('coordinator') != 'root' or grant.get('cases') != list(CASES) or grant.get('disk_bytes') != DISK_BYTES:
        raise RuntimeError('Exact root trial grant required')
    for name, expected in grant['source_hashes'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('Reviewed source changed: ' + name)
    if sha(ROOT / 'test-initramfs.gz') != grant['initramfs_sha256'] or sha(Path('/lab/boot/Image-virt')) != grant['kernel_sha256']:
        raise RuntimeError('Reviewed runtime input changed')
    OUT.mkdir(exist_ok=False)
    sync_directory(OUT.parent)
    save(OUT / 'run-intent.json', grant)
    base = OUT / 'base.raw'
    with base.open('xb') as stream:
        stream.truncate(DISK_BYTES)
    make = subprocess.run(['mkfs.ext4', '-F', '-b', '4096', str(base)], capture_output=True, text=True)
    save(OUT / 'mkfs.json', {'exit': make.returncode, 'stdout': make.stdout, 'stderr': make.stderr})
    make.check_returncode()
    with base.open('rb') as stream:
        os.fsync(stream.fileno())
    sync_directory(OUT)
    rows = []
    try:
        for prefix in CASES:
            if bytes_under(ROOT) + DISK_BYTES > 384 * 1024 * 1024 or bytes_under(Path('/lab')) + DISK_BYTES > 2 * 1024 * 1024 * 1024:
                raise RuntimeError('Owned storage envelope would be exceeded')
            disk = OUT / (prefix + '.raw')
            shutil.copyfile(base, disk)
            cut = boot(disk, prefix, 'cut')
            if 'runtime' not in cut or 'baseline' not in cut:
                raise RuntimeError('Missing actual runtime or retained baseline')
            before = archive(disk, OUT / (prefix + '-pre-recovery.raw.gz'))
            recovered = boot(disk, prefix, 'recover')
            verdict = oracle.check(prefix, cut['baseline'], recovered['before_recovery'],
                                   recovered['after_recovery'], recovered['recovery_result'])
            fsck = subprocess.run(['e2fsck', '-fn', str(disk)], capture_output=True, text=True)
            after = archive(disk, OUT / (prefix + '-post-recovery.raw.gz'))
            row = {'prefix': prefix, 'verdict': verdict, 'pre_recovery': before,
                   'post_recovery': after, 'fsck': {'exit': fsck.returncode,
                   'stdout': fsck.stdout, 'stderr': fsck.stderr, 'repair': False}}
            save(OUT / (prefix + '-result.json'), row)
            rows.append(row)
            print(json.dumps({'prefix': prefix, 'passed': verdict['passed'],
                             'classification': verdict['classification']}), flush=True)
            if not verdict['passed']:
                raise RuntimeError('Actual prototype/oracle mismatch; retained raw disk')
            disk.unlink()
            sync_directory(OUT)
    except Exception as error:
        save(OUT / 'STOP.json', {'error': str(error), 'rows_completed': len(rows),
             'state': 'No retry; read-only reconciliation required'})
        raise
    save(OUT / 'RESULTS.json', {'cases': rows, 'all_passed': all(r['verdict']['passed'] for r in rows),
         'expected_cases': len(CASES), 'boots': 2 * len(CASES),
         'limits': 'Exact experimental prototype on Linux Git2.34/ext4; existing objects synced at baseline; outer host/device caches survive; no production or provider guarantee'})


if __name__ == '__main__':
    main()
