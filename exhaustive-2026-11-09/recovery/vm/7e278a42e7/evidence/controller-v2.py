"""Cut power only to a child QEMU, then inspect a fresh boot of its own disk.

The surviving container/host caches are outside this failure boundary. An
unsynced record surviving one cut is evidence of that run, not an fsync waiver.
"""
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import time

ROOT = Path('/lab')
OUT = ROOT / 'results-v2'


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def boot(disk, phase, log):
    command = ['qemu-system-aarch64', '-machine', 'virt', '-cpu', 'cortex-a57',
               '-accel', 'tcg', '-smp', '1', '-m', '256M', '-nographic',
               '-no-reboot', '-nic', 'none', '-kernel', '/lab/boot/Image-virt',
               '-initrd', '/lab/test-initramfs.gz', '-append',
               'console=ttyAMA0 panic=-1 phase=' + phase,
               '-drive', 'if=none,file=' + str(disk) + ',format=raw,cache=writeback,id=d0',
               '-device', 'virtio-blk-device,drive=d0']
    save(log.with_suffix('.intent.json'), {'command': command, 'phase': phase,
                                         'utc_seconds': time.time()})
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    target = b'BARRIER ' + (b'RECOVERED' if phase == 'recover' else b'CUT' + phase.encode())
    data = b''
    deadline = time.monotonic() + 60
    reached = False
    with log.open('xb') as stream:
        try:
            while time.monotonic() < deadline:
                readable, _, _ = select.select([process.stdout], [], [], 1)
                if readable:
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        break
                    stream.write(chunk)
                    stream.flush()
                    data += chunk
                    if target + b'\r\n' in data or target + b'\n' in data:
                        reached = True
                        break
                if process.poll() is not None:
                    break
        finally:
            # Popen owns this exact emulator child. No process-name or VM reset.
            if process.poll() is None:
                process.kill()
            result = process.wait(timeout=10)
            rest = process.stdout.read()
            stream.write(rest)
            data += rest
            stream.flush()
            os.fsync(stream.fileno())
    save(log.with_suffix('.receipt.json'), {'pid': process.pid, 'exit': result,
         'barrier': target.decode(), 'reached': reached, 'bytes': len(data),
         'utc_seconds': time.time(), 'failure_boundary': 'guest emulator SIGKILL; outer caches survive'})
    if not reached:
        raise RuntimeError('Guest did not reach barrier; inspect ' + str(log))
    return data.decode(errors='replace')


def main():
    OUT.mkdir(exist_ok=False)
    base = ROOT / 'base-v2.raw'
    with base.open('xb') as stream:
        stream.truncate(64 * 1024 * 1024)
    make = subprocess.run(['mkfs.ext4', '-F', str(base)], capture_output=True, text=True)
    save(OUT / 'filesystem-creation.json', {'exit': make.returncode, 'stdout': make.stdout,
                                         'stderr': make.stderr})
    make.check_returncode()
    results = []
    for stage in range(1, 9):
        disk = ROOT / ('case-v2-' + str(stage) + '.raw')
        shutil.copyfile(base, disk)
        boot(disk, str(stage), OUT / ('case-' + str(stage) + '-cut.log'))
        after_cut = hashlib.sha256(disk.read_bytes()).hexdigest()
        recovered = boot(disk, 'recover', OUT / ('case-' + str(stage) + '-recover.log'))
        records = {}
        for line in recovered.splitlines():
            if line.startswith('RECORD '):
                _, path, raw = line.split(' ', 2)
                records[path] = None if raw == 'ABSENT' else json.loads(raw)
        if len(records) != 5:
            raise RuntimeError('Incomplete recovery observation')
        current = records['/state/current.json']
        if current not in [{'generation': 0, 'value': 'old-complete'},
                           {'generation': 1, 'value': 'new-complete'}]:
            raise RuntimeError('Invalid active record')
        if stage >= 4 and stage <= 5 and current['generation'] != 1:
            raise RuntimeError('Synced current record lost')
        ref = records['/state/ref.json']['generation']
        checkpoint = records['/state/checkpoint.json']['generation']
        if stage == 7 and (ref, checkpoint) != (1, 0):
            raise RuntimeError('Pending ref/checkpoint prefix lost')
        if stage == 8 and (ref, checkpoint) != (1, 1):
            raise RuntimeError('Durable final checkpoint lost')
        if stage >= 6 and records['/state/intent.json'] != {'from': 0, 'to': 1, 'value': 'new-complete'}:
            raise RuntimeError('Durable intent lost')
        fsck = subprocess.run(['e2fsck', '-fn', str(disk)], capture_output=True, text=True)
        save(OUT / ('case-' + str(stage) + '-fsck.json'), {'exit': fsck.returncode,
             'stdout': fsck.stdout, 'stderr': fsck.stderr, 'repair': False})
        results.append({'stage': stage, 'records': records, 'after_cut_sha256': after_cut,
                        'after_inspection_sha256': hashlib.sha256(disk.read_bytes()).hexdigest(),
                        'recovery': 'pending-intent-needs-reconciliation' if (ref != checkpoint or
                             records['/state/intent.json'] is not None and checkpoint < records['/state/intent.json']['to'])
                             else 'matching-record-generations',
                        'fsck_exit': fsck.returncode})
        save(OUT / ('case-' + str(stage) + '-result.json'), results[-1])
        print(json.dumps(results[-1]), flush=True)
    save(OUT / 'RESULTS.json', {'cases': results, 'limit': 'Guest emulator cut, not host/device power loss; eight single trials'})


if __name__ == '__main__':
    main()
