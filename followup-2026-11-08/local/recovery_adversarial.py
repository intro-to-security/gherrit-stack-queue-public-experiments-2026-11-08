#!/usr/bin/env python3
import errno
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('followup', ROOT / 'followup.py')
f = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = f
spec.loader.exec_module(f)
core = f.core


def wait_file(path):
    deadline = time.monotonic() + 15
    while not path.exists():
        if time.monotonic() > deadline:
            raise RuntimeError('barrier timeout ' + str(path))
        time.sleep(.01)


def stale_child(job, barrier, role):
    barrier = Path(barrier)
    old_read = core.read_json
    stopped = False
    def read(path):
        nonlocal stopped
        value = old_read(path)
        if Path(path).name == 'operation.json' and value.get('state') == 'planned' and not stopped:
            stopped = True
            f.dump(barrier / (role + '-ready.json'), {'pid': os.getpid(), 'cached_state': value})
            wait_file(barrier / 'go')
            if role == 'stale':
                wait_file(barrier / 'first-complete.json')
        return value
    core.read_json = read
    result = core.worker(job)
    f.dump(barrier / (role + '-complete.json'), {'pid': os.getpid(), 'exit': result})
    return result


def ordered_duplicate():
    directory, job = f.copy_job('planned', 'ordered-stale-writer')
    operation = core.read_json(directory / 'operation.json')
    operation['state'] = 'planned'
    f.dump(directory / 'operation.json', operation)
    f.dump(directory / 'provider.json', {'head': job['incorporated']['tip'], 'requests': []})
    (directory / 'continuation-checkpoint.json').unlink()
    repo = core.FixtureGit(job['repo'], initialize=False)
    repo.git('update-ref', '-d', job['continuation'])
    barrier = directory / 'barrier'
    barrier.mkdir()
    f.dump(directory / 'intent.json', {'roles': ['first', 'stale'], 'schedule': 'Both cache planned; first completes; stale resumes cached planned.'})
    children, handles = [], []
    for role in ['first', 'stale']:
        out, err = (directory / (role + '.stdout')).open('wb'), (directory / (role + '.stderr')).open('wb')
        handles += [out, err]
        children.append(subprocess.Popen([sys.executable, str(Path(__file__)), 'child', str(directory / 'job.json'), str(barrier), role], env=f.ENV, stdout=out, stderr=err))
    for role in ['first', 'stale']:
        wait_file(barrier / (role + '-ready.json'))
    (barrier / 'go').write_text('go\n')
    exits = [child.wait(timeout=15) for child in children]
    for h in handles:
        h.close()
    provider = core.read_json(job['provider'])
    f.checked('both stale invocation processes return complete', exits, [0, 0])
    f.checked('serialized emulator independently records duplicate dispatch', len(provider['requests']), 2)
    row = {'exits': exits, 'provider': provider, 'model_failure': True, 'boundary': 'Current prototype worker assumes one cooperating writer and lacks an enforced exclusion or stale-operation generation check.'}
    f.dump(directory / 'probe.json', row)
    return row


def foreign_record():
    directory, job = f.copy_job('complete', 'foreign-operation-record')
    operation = core.read_json(directory / 'operation.json')
    operation['id'] = 'different-operation-not-in-manifest'
    f.dump(directory / 'operation.json', operation)
    admission = core.transfer_authority(directory)
    f.checked('existing prototype admits mismatched identity', admission['mutation_authority'], True)
    row = {'manifest': core.read_json(directory / 'pending-operations.json'), 'record_id': operation['id'], 'admission': admission, 'model_failure': True, 'effects': 0}
    f.dump(directory / 'probe.json', row)
    return row


def fsync_errors():
    rows = []
    for fail_number in [1, 2]:
        directory = f.RUN / ('fsync-error-' + str(fail_number))
        directory.mkdir()
        target = directory / 'checkpoint.json'
        f.dump(target, {'generation': 'old'})
        real_fsync = os.fsync
        count = 0
        def fail(fd):
            nonlocal count
            count += 1
            if count == fail_number:
                raise OSError(errno.EIO, 'injected experiment fsync error')
            return real_fsync(fd)
        os.fsync = fail
        caught = None
        try:
            core.atomic_json(target, {'generation': 'new'})
        except OSError as error:
            caught = {'errno': error.errno, 'message': str(error)}
        finally:
            os.fsync = real_fsync
        f.checked('fsync failure propagates', caught is not None, True)
        visible = core.read_json(target)
        f.checked('pre/post-rename visibility', visible['generation'], 'old' if fail_number == 1 else 'new')
        row = {'injected_fsync': 'file' if fail_number == 1 else 'directory', 'exception': caught, 'visible_checkpoint': visible, 'temporary_exists': target.with_suffix('.json.new').exists(), 'unknown_power_durability': True}
        f.dump(directory / 'probe.json', row)
        rows.append(row)
    return rows


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'child':
        return stale_child(*sys.argv[2:])
    f.RUN = ROOT / 'adversarial-runs' / str(time.time_ns())
    f.RUN.mkdir(parents=True)
    shutil.copyfile(Path(__file__), f.RUN / 'recovery_adversarial.py')
    f.case('L28', 'Ordered stale planned worker duplicates', ordered_duplicate)
    f.case('L29', 'Custody operation identity mismatch', foreign_record)
    f.case('L30', 'Fsync error before and after rename', fsync_errors)
    result = {'run': str(f.RUN), 'rows': f.ROWS, 'passed': sum(r['status'] == 'passed' for r in f.ROWS), 'failed': sum(r['status'] == 'failed' for r in f.ROWS)}
    f.dump(f.RUN / 'RESULTS.json', result)
    f.dump(ROOT / 'latest-adversarial-run.json', {k: v for k, v in result.items() if k != 'rows'})
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}))
    return bool(result['failed'])


if __name__ == '__main__':
    sys.exit(main())
