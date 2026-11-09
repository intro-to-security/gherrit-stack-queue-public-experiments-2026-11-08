#!/usr/bin/env python3
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import statistics
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent.parent / 'native-stacks-2026-11-08'
WORKSPACE = ROOT.parents[2]
spec = importlib.util.spec_from_file_location('baseline', ROOT / 'baseline-harness.py')
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)
ENV = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
ENV.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0', LC_ALL='C')
core.ENV = ENV
ZERO = '0' * 40
RUN = None
ROWS = []


def dump(path, value):
    core.atomic_json(path, value)


def cmd(argv, cwd, data=None, allowed=None, env=None):
    p = subprocess.run([str(x) for x in argv], cwd=cwd, input=data, capture_output=True,
                       env=env or ENV)
    entry = {'argv': [str(x) for x in argv], 'cwd': str(cwd), 'exit': p.returncode,
             'stdin_hex': data.hex() if data else None,
             'stdout_hex': p.stdout.hex(), 'stderr_hex': p.stderr.hex()}
    with (RUN / 'commands.jsonl').open('a') as f:
        f.write(json.dumps(entry, sort_keys=True) + '\n')
    if allowed is not None and p.returncode not in allowed:
        raise RuntimeError(json.dumps(entry))
    return p


def checked(label, actual, expected):
    if actual != expected:
        raise AssertionError(label + ': ' + repr(actual) + ' != ' + repr(expected))


def case(case_id, label, action):
    started = time.monotonic()
    row = {'id': case_id, 'label': label, 'disposition': 'performed'}
    try:
        row['evidence'] = action()
        row['status'] = 'passed'
    except Exception:
        row['status'] = 'failed'
        row['failure'] = traceback.format_exc()
        (RUN / (case_id + '-failure.txt')).write_text(row['failure'])
    row['seconds'] = time.monotonic() - started
    ROWS.append(row)
    dump(RUN / 'results-partial.json', ROWS)
    print(json.dumps({'id': case_id, 'status': row['status'], 'seconds': round(row['seconds'], 3)}), flush=True)


def message(subject):
    return subject + '\n\n' + core.TRAILER + '\n'


def tree_oid(repo, commit):
    return repo.git('rev-parse', commit + '^{tree}').stdout.strip()


def changed(files, **updates):
    return dict(files, **updates)


def layer(name, i, l, h):
    return core.Layer(name, core.RevisionRange(*i), core.RevisionRange(*l), core.RevisionRange(*h))


def repeated():
    observations = []
    for seed in [3, 7, 11]:
        repo = core.FixtureGit(RUN / ('repeated-' + str(seed)))
        original = {k + '.txt': '0\n' for k in ['a', 'b', 'localA', 'hostA', 'localB', 'hostB', 'trunk']}
        p = repo.commit('P', original)
        ia = repo.commit('authored_A', changed(original, **{'a.txt': '1\n'}), p)
        ib = repo.commit('authored_B', changed(repo.files(ia), **{'b.txt': '1\n'}), ia)
        la = repo.commit('pending_A', changed(repo.files(ia), **{'localA.txt': str(seed) + '\n'}), p, message('Retain A amendment'))
        lb = repo.commit('pending_B', changed(repo.files(la), **{'b.txt': '1\n', 'localB.txt': str(seed) + '\n'}), la, message('Retain B amendment'))
        ir = [(p, ia), (ia, ib)]
        lr = [(p, la), (la, lb)]
        rounds = []
        for n in range(1, 7):
            pp = repo.commit('parent_' + str(n), changed(original, **{'trunk.txt': str(n) + '\n'}), p)
            ha_files = changed(repo.files(pp), **{'a.txt': '1\n', 'hostA.txt': str(n) + '\n'})
            ha = repo.commit('host_A_' + str(n), ha_files, pp, repo.message(ia))
            hb_files = changed(ha_files, **{'b.txt': '1\n', 'hostB.txt': str(n) + '\n'})
            hb = repo.commit('host_B_' + str(n), hb_files, ha, repo.message(ib))
            if n > 1:
                local_a_files = changed(repo.files(lr[0][1]), **{'localA.txt': str(seed + n - 1) + '\n'})
                new_la = repo.commit('amend_A_' + str(n), local_a_files, lr[0][0], repo.message(la))
                local_b_files = changed(repo.files(lr[1][1]), **{'localA.txt': str(seed + n - 1) + '\n'})
                new_lb = repo.commit('rebase_B_' + str(n), local_b_files, new_la, repo.message(lb))
                lr = [(lr[0][0], new_la), (new_la, new_lb)]
            hr = [(pp, ha), (ha, hb)]
            layers = [layer(name, i, l, h) for name, i, l, h in zip(['A', 'B'], ir, lr, hr)]
            out = repo.integrate('round_' + str(n), layers, pp)
            a, b = [x['accepted_local']['tip'] for x in out]
            ea = changed(ha_files, **{'localA.txt': str(seed + n - 1) + '\n'})
            eb = changed(ea, **{'b.txt': '1\n', 'hostB.txt': str(n) + '\n', 'localB.txt': str(seed) + '\n'})
            checked('A exact expected tree', repo.files(a), ea)
            checked('B exact expected tree', repo.files(b), eb)
            checked('B layer paths', repo.git('diff', '--name-only', a, b).stdout.splitlines(), ['b.txt', 'hostB.txt', 'localB.txt'])
            checked('A message', repo.message(a), repo.message(la))
            checked('B message', repo.message(b), repo.message(lb))
            rounds.append({'round': n, 'authored': [(p, ia), (ia, ib)], 'incorporated': ir, 'local': lr, 'hosted': hr,
                           'outputs': out, 'expected_A': ea, 'expected_B': eb})
            ir, lr = hr, [(pp, a), (a, b)]
        noop = repo.integrate('noop', [layer(name, i, l, h) for name, i, l, h in zip(['A', 'B'], ir, lr, ir)], lr[0][0])
        checked('unchanged tree', tree_oid(repo, noop[-1]['accepted_local']['tip']), tree_oid(repo, lr[-1][1]))
        observations.append({'seed': seed, 'rounds': rounds, 'noop': {'before_tip': lr[-1][1], 'after_tip': noop[-1]['accepted_local']['tip'], 'tree_unchanged': True}})
        dump(RUN / ('repeated-' + str(seed) + '-evidence.json'), observations[-1])
        repo.git('fsck', '--full', '--no-reflogs')
    return {'seeds': 3, 'rounds_per_seed': 6, 'evidence': ['repeated-' + str(n) + '-evidence.json' for n in [3, 7, 11]], 'checks_per_round': ['exact A/B trees', 'B ownership', 'A/B message bytes'], 'noops': [x['noop'] for x in observations]}


class ExactGit(core.FixtureGit):
    def tree_entries(self, entries):
        index = self.root.parent / (self.root.name + '-exact-index')
        if index.exists():
            index.unlink()
        env = dict(ENV, GIT_INDEX_FILE=str(index))
        self.git('read-tree', '--empty', env=env)
        for path, (mode, content) in sorted(entries.items()):
            blob = cmd(['git', 'hash-object', '-w', '--stdin'], self.root, content, (0,)).stdout.decode().strip()
            self.git('update-index', '--add', '--cacheinfo', mode, blob, path, env=env)
        return self.git('write-tree', env=env).stdout.strip()

    def entries(self, commit):
        entries = {}
        for line in self.git('ls-tree', '-r', commit).stdout.splitlines():
            metadata, path = line.split('\t', 1)
            mode, kind, oid = metadata.split()
            entries[path] = (mode, cmd(['git', 'cat-file', 'blob', oid], self.root, allowed=(0,)).stdout)
        return entries

    def commit_entries(self, label, entries, parent=None, text=None):
        return self.commit_tree(label, self.tree_entries(entries), parent, text)


def encoded(entries):
    return {p: {'mode': m, 'content_hex': b.hex()} for p, (m, b) in entries.items()}


def exact_variants():
    outcomes = []
    for variant in ['rename', 'mode', 'deletion', 'binary', 'rename-conflict', 'delete-conflict', 'binary-conflict']:
        repo = ExactGit(RUN / ('exact-' + variant))
        base = {'a.txt': ('100644', b'0\n'), 'old.txt': ('100644', b'line one\nline two\n'), 'host.txt': ('100644', b'0\n'), 'blob.bin': ('100644', bytes(range(64)))}
        p = repo.commit_entries('P', base)
        authored = dict(base, **{'a.txt': ('100644', b'1\n')})
        i = repo.commit_entries('I', authored, p)
        local, hosted = dict(authored), dict(authored)
        hosted['host.txt'] = ('100644', b'hosted\n')
        expected_conflict = variant.endswith('conflict')
        if variant in ['rename', 'rename-conflict']:
            local['local-name.txt'] = local.pop('old.txt')
            if expected_conflict:
                hosted['host-name.txt'] = hosted.pop('old.txt')
            else:
                hosted['old.txt'] = ('100644', b'line one\nline two edited by hosted\n')
        elif variant == 'mode':
            local['old.txt'] = ('100755', local['old.txt'][1])
            hosted['old.txt'] = ('100644', b'line one\nline two edited by hosted\n')
        elif variant in ['deletion', 'delete-conflict']:
            local.pop('old.txt')
            if expected_conflict:
                hosted['old.txt'] = ('100644', b'hosted content\n')
        else:
            local['blob.bin'] = ('100644', b'\x00local\xff' + bytes(range(64)))
            if expected_conflict:
                hosted['blob.bin'] = ('100644', b'\x00hosted\xff' + bytes(range(64)))
        l = repo.commit_entries('L', local, p, message('Retain exact local ' + variant))
        h = repo.commit_entries('H', hosted, p)
        try:
            out = repo.integrate(variant, [layer('A', (p, i), (p, l), (p, h))], p)
            if expected_conflict:
                raise AssertionError('expected conflict')
            expected = dict(hosted)
            if variant == 'rename':
                expected['local-name.txt'] = expected.pop('old.txt')
            elif variant == 'mode':
                expected['old.txt'] = ('100755', hosted['old.txt'][1])
            elif variant == 'deletion':
                expected.pop('old.txt')
            else:
                expected['blob.bin'] = local['blob.bin']
            tip = out[0]['accepted_local']['tip']
            checked('exact modes and bytes', repo.entries(tip), expected)
            row = {'variant': variant, 'expected_conflict': False, 'output': tip, 'expected': encoded(expected), 'actual': encoded(repo.entries(tip)), 'output_patch': repo.git('diff', '--binary', p, tip).stdout}
        except core.MergeConflict as failure:
            if not expected_conflict:
                raise
            row = {'variant': variant, 'expected_conflict': True, 'failure': str(failure), 'merges': repo.merges}
        row.update(inputs={'base': p, 'incorporated': i, 'local': l, 'hosted': h}, local=encoded(local), hosted=encoded(hosted))
        outcomes.append(row)
        dump(RUN / ('exact-' + variant + '-evidence.json'), row)
        repo.git('fsck', '--full', '--no-reflogs')
    return outcomes


def multi_reset_revert():
    repo = core.FixtureGit(RUN / 'multi-reset-revert')
    files = {'a.txt': '0\n', 'b.txt': '0\n', 'local.txt': '0\n', 'host.txt': '0\n'}
    p = repo.commit('P', files)
    ia = repo.commit('I_A', changed(files, **{'a.txt': '1\n'}), p)
    ib = repo.commit('I_B', changed(repo.files(ia), **{'b.txt': '1\n'}), ia)
    l1 = repo.commit('L_A_first', changed(repo.files(ia), **{'local.txt': 'first\n'}), p)
    l2 = repo.commit('L_A_tip', changed(repo.files(l1), **{'local.txt': 'local\n'}), l1, message('Local group tip'))
    lb = repo.commit('L_B', changed(repo.files(l2), **{'b.txt': '1\n'}), l2, repo.message(ib))
    h1 = repo.commit('H_A_first', changed(repo.files(ia), **{'host.txt': 'first\n'}), p)
    h2 = repo.commit('H_A_tip', changed(repo.files(h1), **{'host.txt': 'hosted\n'}), h1)
    hb = repo.commit('H_B', changed(repo.files(h2), **{'b.txt': '1\n'}), h2, repo.message(ib))
    out = repo.integrate('multi', [layer('A', (p, ia), (p, l2), (p, h2)), layer('B', (ia, ib), (l2, lb), (h2, hb))], p)
    a, b = [r['accepted_local']['tip'] for r in out]
    expected = changed(files, **{'a.txt': '1\n', 'local.txt': 'local\n', 'host.txt': 'hosted\n', 'b.txt': '1\n'})
    checked('multi range exact tree', repo.files(b), expected)
    checked('local tip message', repo.message(a), repo.message(l2))
    checked('B ownership', repo.git('diff', '--name-only', a, b).stdout.splitlines(), ['b.txt'])
    revert = repo.commit('new_ID_revert', changed(repo.files(a), **{'a.txt': '0\n'}), a, message('Revert A as new change R'))
    reverted = repo.integrate('revert', [layer('A', (p, h2), (p, a), (p, h2)), layer('R', (a, a), (a, revert), (a, a))], p)
    checked('revert retained', repo.files(reverted[-1]['accepted_local']['tip'])['a.txt'], '0\n')
    reset = repo.commit('accepted_reset', repo.files(h2), p, repo.message(l2))
    resetout = repo.integrate('reset', [layer('A', (p, h2), (p, reset), (p, h2))], p)
    checked('explicit reset removes pending local', repo.files(resetout[0]['accepted_local']['tip']), repo.files(h2))
    checked('original pending object retained', repo.git('cat-file', '-t', a).stdout.strip(), 'commit')
    return {'multi': out, 'inputs': {'local_group': (p, l2), 'hosted_group': (p, h2)}, 'local_commit_count': repo.git('rev-list', '--count', p + '..' + l2).stdout.strip(), 'output_A_commit_count': repo.git('rev-list', '--count', p + '..' + a).stdout.strip(), 'revert': reverted, 'reset': resetout, 'scope': 'Net range integration; individual intermediate commit identities are not retained in accepted flattened layer.'}


def baseline_path():
    return Path(core.read_json(ROOT / 'latest-run.json')['run'])


def copy_job(prefix, label):
    original = baseline_path() / 'faults' / prefix
    target = RUN / label
    shutil.copytree(original, target)
    job = core.read_json(target / 'job.json')
    job.update(directory=str(target), repo=str(target / 'repo'), provider=str(target / 'provider.json'))
    dump(target / 'job.json', job)
    return target, job


def run_worker(directory, reconcile=False):
    args = [sys.executable, ROOT / 'baseline-harness.py', 'worker', directory / 'job.json']
    if reconcile:
        args += ['--reconcile-receipt']
    return cmd(args, directory)


def duplicate_recovery():
    rows = []
    for prefix in core.PREFIXES:
        directory, job = copy_job(prefix, 'duplicate-' + prefix)
        before = core.read_json(job['provider'])
        first, second = run_worker(directory), run_worker(directory)
        after = core.read_json(job['provider'])
        checked('duplicate recovery no extra requests ' + prefix, len(after['requests']), len(before['requests']))
        checked('same terminal recovery', first.returncode, second.returncode)
        rows.append({'prefix': prefix, 'first': first.returncode, 'second': second.returncode, 'requests': len(after['requests']), 'operation': core.read_json(directory / 'operation.json')})
    return rows


def custody_missing():
    rows = []
    for name in ['bindings.json', 'accepted-checkpoint.json', 'pending-operations.json', 'operation.json']:
        directory, job = copy_job('provider_applied', 'missing-' + name.replace('.', '-'))
        (directory / name).unlink()
        admission = core.transfer_authority(directory)
        checked('missing evidence excludes authority', admission['mutation_authority'], False)
        rows.append({'deleted': name, 'admission': admission})
    full, job = copy_job('provider_applied', 'full-custody')
    admission = core.transfer_authority(full)
    checked('unknown guard survives custody', admission['mutation_authority'], False)
    recovered = run_worker(full, reconcile=True)
    checked('unique local receipt permits completion', recovered.returncode, 0)
    checked('custody no resend', len(core.read_json(job['provider'])['requests']), 1)
    return {'missing': rows, 'full_admission': admission, 'full_recovery': recovered.returncode, 'scope': 'Cooperative admission policy; direct worker invocation is separately challenged.'}


def damaged_completion():
    rows = []
    for scenario in ['wrong-ref', 'wrong-checkpoint', 'deleted-ref-complete', 'deleted-checkpoint-complete', 'missing-operation-after-effect']:
        prefix = 'provider_applied' if scenario == 'missing-operation-after-effect' else 'complete'
        directory, job = copy_job(prefix, 'damaged-' + scenario)
        repo = core.FixtureGit(job['repo'], initialize=False)
        if scenario == 'wrong-ref':
            operation = core.read_json(directory / 'operation.json')
            operation['state'] = 'acknowledged'
            dump(directory / 'operation.json', operation)
            repo.git('update-ref', job['continuation'], job['captured_source'])
        elif scenario == 'wrong-checkpoint':
            operation = core.read_json(directory / 'operation.json')
            operation['state'] = 'acknowledged'
            dump(directory / 'operation.json', operation)
            checkpoint = core.read_json(directory / 'continuation-checkpoint.json')
            checkpoint['result'] = job['captured_source']
            dump(directory / 'continuation-checkpoint.json', checkpoint)
        elif scenario == 'deleted-ref-complete':
            repo.git('update-ref', '-d', job['continuation'])
        elif scenario == 'deleted-checkpoint-complete':
            (directory / 'continuation-checkpoint.json').unlink()
        else:
            (directory / 'operation.json').unlink()
        before = core.read_json(job['provider'])
        admission = core.transfer_authority(directory)
        result = run_worker(directory)
        after = core.read_json(job['provider'])
        ref = repo.git('show-ref', '--verify', '--hash', job['continuation'], allowed=(0, 128)).stdout.strip()
        checkpoint = core.read_json(directory / 'continuation-checkpoint.json') if (directory / 'continuation-checkpoint.json').exists() else None
        model_failure = (result.returncode == 0 and (ref != job['result'] or checkpoint is None)) or len(after['requests']) > len(before['requests'])
        if scenario in ['wrong-ref', 'wrong-checkpoint']:
            checked('incompatible evidence refuses ' + scenario, result.returncode, 4 if scenario == 'wrong-ref' else 5)
        elif not model_failure:
            raise AssertionError('negative probe no longer demonstrates expected validation gap: ' + scenario)
        row = {'scenario': scenario, 'admission': admission, 'worker_exit': result.returncode, 'requests_before': len(before['requests']), 'requests_after': len(after['requests']), 'final_ref': ref, 'checkpoint': checkpoint, 'model_failure': model_failure}
        dump(directory / 'probe.json', row)
        rows.append(row)
    return {'probes': rows, 'model_failures': [r['scenario'] for r in rows if r['model_failure']]}


FSYNC_PREFIXES = ['before-temp', 'partial-temp', 'written-temp', 'flushed-temp', 'fsynced-temp', 'renamed', 'directory-fsynced']


def fsync_child(directory, selected):
    directory = Path(directory)
    path = directory / 'journal.json'
    temporary = directory / 'journal.json.new'
    payload = (json.dumps({'generation': 'new', 'payload': 'x' * 65536}) + '\n').encode()
    def pause(prefix):
        if prefix == selected:
            dump(directory / 'paused.json', {'prefix': prefix, 'pid': os.getpid()})
            while True:
                signal.pause()
    pause('before-temp')
    with temporary.open('wb') as f:
        f.write(payload[:97])
        pause('partial-temp')
        f.write(payload[97:])
        pause('written-temp')
        f.flush()
        pause('flushed-temp')
        os.fsync(f.fileno())
        pause('fsynced-temp')
    os.replace(temporary, path)
    pause('renamed')
    fd = os.open(str(directory), os.O_RDONLY)
    os.fsync(fd)
    os.close(fd)
    pause('directory-fsynced')


def journal_prefixes():
    rows = []
    for prefix in FSYNC_PREFIXES:
        directory = RUN / ('fsync-' + prefix)
        directory.mkdir()
        dump(directory / 'journal.json', {'generation': 'old'})
        with (directory / 'child.stdout').open('wb') as out, (directory / 'child.stderr').open('wb') as err:
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'fsync-child', str(directory), prefix], env=ENV, stdout=out, stderr=err)
            wait_marker(child, directory / 'paused.json')
            child.kill()
            code = child.wait()
        checked('real SIGKILL', code, -signal.SIGKILL)
        journal = core.read_json(directory / 'journal.json')
        checked('atomic journal generation', journal['generation'], 'new' if prefix in ['renamed', 'directory-fsynced'] else 'old')
        temp = directory / 'journal.json.new'
        row = {'prefix': prefix, 'pid': child.pid, 'exit': code, 'journal_generation': journal['generation'], 'journal_sha256': hashlib.sha256((directory / 'journal.json').read_bytes()).hexdigest(), 'temp_exists': temp.exists(), 'temp_bytes': temp.stat().st_size if temp.exists() else None, 'power_loss_claim': False}
        rows.append(row)
        dump(directory / 'evidence.json', row)
    return {'prefixes': rows, 'limit': 'SIGKILL preserves kernel/filesystem cache; this does not emulate device/power loss, torn writes or fsync correctness.'}


def wait_marker(child, path):
    deadline = time.monotonic() + 15
    while not path.exists():
        if child.poll() is not None:
            raise RuntimeError('child exited early: ' + str(child.returncode))
        if time.monotonic() >= deadline:
            child.kill()
            child.wait()
            raise RuntimeError('child marker timeout')
        time.sleep(0.01)


def concurrent_worker_child(job_path, barrier):
    old_read = core.read_json
    blocked = False
    def read(path):
        nonlocal blocked
        value = old_read(path)
        if Path(path).name == 'operation.json' and value.get('state') == 'planned' and not blocked:
            blocked = True
            dump(Path(barrier) / (str(os.getpid()) + '.ready'), {'pid': os.getpid()})
            deadline = time.monotonic() + 15
            while not (Path(barrier) / 'go').exists():
                if time.monotonic() >= deadline:
                    raise RuntimeError('barrier timeout')
                time.sleep(0.01)
        return value
    core.read_json = read
    return core.worker(job_path)


def concurrent_workers():
    rows = []
    for n in range(2):
        directory, job = copy_job('planned', 'concurrent-worker-' + str(n))
        operation = core.read_json(directory / 'operation.json')
        operation['state'] = 'planned'
        dump(directory / 'operation.json', operation)
        dump(directory / 'provider.json', {'head': job['incorporated']['tip'], 'requests': []})
        checkpoint = directory / 'continuation-checkpoint.json'
        if checkpoint.exists():
            checkpoint.unlink()
        repo = core.FixtureGit(job['repo'], initialize=False)
        repo.git('update-ref', '-d', job['continuation'])
        barrier = directory / 'barrier'
        barrier.mkdir()
        children, handles = [], []
        for writer in range(2):
            out = (directory / ('writer-' + str(writer) + '.stdout')).open('wb')
            err = (directory / ('writer-' + str(writer) + '.stderr')).open('wb')
            handles += [out, err]
            children.append(subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'concurrent-worker-child', str(directory / 'job.json'), str(barrier)], env=ENV, stdout=out, stderr=err))
        deadline = time.monotonic() + 15
        while len(list(barrier.glob('*.ready'))) < 2:
            if any(c.poll() is not None for c in children) or time.monotonic() > deadline:
                for c in children:
                    if c.poll() is None:
                        c.kill()
                    c.wait()
                raise RuntimeError('concurrent barrier failed')
            time.sleep(0.01)
        (barrier / 'go').write_text('go\n')
        exits = [c.wait(timeout=15) for c in children]
        for handle in handles:
            handle.close()
        provider = core.read_json(directory / 'provider.json')
        row = {'run': n, 'pids': [c.pid for c in children], 'exits': exits, 'requests_in_final_store': len(provider['requests']), 'provider': provider,
               'errors': [(directory / ('writer-' + str(i) + '.stderr')).read_text() for i in range(2)], 'scope': 'A cooperative one-writer prototype has no concurrent ownership fence; a lost store update may undercount attempts.'}
        dump(directory / 'probe.json', row)
        rows.append(row)
    return rows


def new_sink(label):
    directory = RUN / label
    directory.mkdir()
    source = core.FixtureGit(directory / 'source')
    p = source.commit('P', {'payload.txt': 'old\n'})
    a = source.commit('A', {'payload.txt': 'writer A\n'}, p)
    b = source.commit('B', {'payload.txt': 'writer B\n'}, p)
    sink = directory / 'sink.git'
    cmd(['git', 'init', '--bare', sink], directory, allowed=(0,))
    source.git('remote', 'add', 'sink', str(sink))
    source.git('push', '--no-verify', 'sink', p + ':refs/heads/head')
    return directory, source, sink, p, a, b


def refs_at(sink):
    result = cmd(['git', 'for-each-ref', '--format=%(refname) %(objectname)'], sink, allowed=(0,))
    return dict(line.split() for line in result.stdout.decode().splitlines())


def push(source, args, env=None):
    return cmd(['git', 'push', '--porcelain', '--no-verify'] + args, source.root, env=env)


def concurrent_git():
    rows = []
    for same in [False, True]:
        directory, source, sink, p, a, b = new_sink('git-concurrent-' + ('same' if same else 'divergent'))
        children, handles, argument_lists = [], [], []
        for writer, target in enumerate([a, a if same else b]):
            args = ['git', 'push', '--porcelain', '--no-verify', '--atomic', '--force-with-lease=refs/heads/head:' + p, '--force-with-lease=refs/tags/archive:', 'sink', target + ':refs/heads/head', target + ':refs/tags/archive']
            argument_lists.append(args)
            out = (directory / ('writer-' + str(writer) + '.stdout')).open('wb')
            err = (directory / ('writer-' + str(writer) + '.stderr')).open('wb')
            handles += [out, err]
            children.append(subprocess.Popen(args, cwd=source.root, env=ENV, stdout=out, stderr=err))
        codes = [child.wait(timeout=15) for child in children]
        for h in handles:
            h.close()
        after = refs_at(sink)
        checked('coupled winner', after['refs/heads/head'], after['refs/tags/archive'])
        if not same:
            checked('exactly one divergent winner', sum(c == 0 for c in codes), 1)
        else:
            retry = push(source, argument_lists[0][4:])
            checked('equal refs stale ownership checks can report success', retry.returncode, 0)
        rows.append({'same_target': same, 'exits': codes, 'refs': after, 'args': argument_lists, 'stdout': [(directory / ('writer-' + str(i) + '.stdout')).read_text() for i in range(2)], 'stderr': [(directory / ('writer-' + str(i) + '.stderr')).read_text() for i in range(2)]})
    return rows


def atomic_equal_aba():
    rows = []
    directory, source, sink, p, a, b = new_sink('git-atomic-rejection')
    result = push(source, ['--atomic', '--force-with-lease=refs/heads/head:' + b, '--force-with-lease=refs/tags/archive:', 'sink', a + ':refs/heads/head', a + ':refs/tags/archive'])
    checked('stale atomic push rejects', result.returncode != 0, True)
    checked('atomic no archive side effect', refs_at(sink), {'refs/heads/head': p})
    rows.append({'control': 'atomic-stale', 'exit': result.returncode, 'stdout': result.stdout.decode(), 'stderr': result.stderr.decode(), 'refs': refs_at(sink)})
    directory, source, sink, p, a, b = new_sink('git-equal-ref')
    trace = directory / 'packet.trace'
    env = dict(ENV, GIT_TRACE_PACKET=str(trace))
    result = push(source, ['--atomic', '--force-with-lease=refs/heads/head:' + b, '--force-with-lease=refs/tags/archive:', 'sink', p + ':refs/heads/head', a + ':refs/tags/archive'], env=env)
    checked('unchanged guard lease not checked', result.returncode, 0)
    checked('archive written despite stale unchanged guard', refs_at(sink), {'refs/heads/head': p, 'refs/tags/archive': a})
    rows.append({'control': 'equal-ref', 'exit': result.returncode, 'refs': refs_at(sink), 'packet_trace': str(trace)})
    directory, source, sink, p, a, b = new_sink('git-aba')
    cmd(['git', 'fetch', '--no-tags', str(source.root), a], sink, allowed=(0,))
    cmd(['git', 'update-ref', 'refs/heads/head', a, p], sink, allowed=(0,))
    cmd(['git', 'update-ref', 'refs/heads/head', p, a], sink, allowed=(0,))
    result = push(source, ['--atomic', '--force-with-lease=refs/heads/head:' + p, 'sink', b + ':refs/heads/head'])
    checked('ABA value lease accepts', result.returncode, 0)
    checked('ABA final', refs_at(sink), {'refs/heads/head': b})
    rows.append({'control': 'ABA', 'sequence': [p, a, p, b], 'exit': result.returncode, 'refs': refs_at(sink)})
    return rows


def history():
    repo = core.FixtureGit(RUN / 'history')
    p = repo.commit('P', {'change.txt': '0\n', 'parent.txt': '0\n'})
    a = repo.commit('A', {'change.txt': '1\n', 'parent.txt': '0\n'}, p, message('Authored patch'))
    q = repo.commit('Q', {'change.txt': '0\n', 'parent.txt': '1\n'}, p)
    same = repo.commit('same', {'change.txt': '1\n', 'parent.txt': '1\n'}, q, repo.message(a))
    newer = repo.commit('newer', {'change.txt': '2\n', 'parent.txt': '1\n'}, q, repo.message(a))
    oldpatch = repo.git('diff', '--binary', p, a).stdout
    samepatch = repo.git('diff', '--binary', q, same).stdout
    checked('historical patches same', oldpatch, samepatch)
    checked('tip diff includes parent', repo.git('diff', '--name-only', a, same).stdout.splitlines(), ['parent.txt'])
    equals = repo.git('range-diff', '--no-color', p + '..' + a, q + '..' + same).stdout
    changes = repo.git('range-diff', '--no-color', p + '..' + a, q + '..' + newer).stdout
    checked('range-diff unchanged', ' = ' in equals, True)
    changedpatch = repo.git('diff', '--binary', q, newer).stdout
    checked('independent patch bytes changed', oldpatch != changedpatch, True)
    checked('range-diff does not report unchanged patch', ' = ' not in changes, True)
    checked('range-diff renders changed or unmatched patches', (' ! ' in changes) or (' < ' in changes and ' > ' in changes), True)
    evidence = {'ranges': {'v1': (p, a), 'same_patch_new_parent': (q, same), 'changed_patch_new_parent': (q, newer)}, 'old_patch': oldpatch, 'same_patch': samepatch, 'tip_diff': repo.git('diff', '--binary', a, same).stdout, 'range_diff_same': equals, 'range_diff_changed': changes}
    dump(RUN / 'history-evidence.json', evidence)
    return evidence


def main():
    global RUN
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['run', 'fsync-child', 'concurrent-worker-child'])
    parser.add_argument('extra', nargs='*')
    args = parser.parse_args()
    if args.mode == 'fsync-child':
        fsync_child(*args.extra)
        return 0
    if args.mode == 'concurrent-worker-child':
        return concurrent_worker_child(*args.extra)
    RUN = ROOT / 'followup-runs' / str(time.time_ns())
    RUN.mkdir(parents=True)
    shutil.copyfile(Path(__file__), RUN / 'followup.py')
    dump(RUN / 'environment.json', {'git': subprocess.run(['git', '--version'], capture_output=True, text=True).stdout.strip(), 'python': sys.version, 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'baseline_sha256': hashlib.sha256((ROOT / 'baseline-harness.py').read_bytes()).hexdigest(), 'claim': 'Local synthetic evidence only; no network.'})
    case('L02-L04', 'Repeated independent tree/metamorphic/no-op oracle', repeated)
    case('L05-L08', 'Multi-commit ranges, explicit reset and revert', multi_reset_revert)
    case('L06-L07', 'Exact mode, rename, deletion, binary and conflicts', exact_variants)
    case('L11', 'Duplicate recovery at every durable prefix', duplicate_recovery)
    case('L12', 'Missing evidence and cooperative custody', custody_missing)
    case('L13-L14', 'Damaged completion and missing operation negative probes', damaged_completion)
    case('L15', 'SIGKILL during atomic journal replacement', journal_prefixes)
    case('L16', 'Concurrent duplicate prototype worker', concurrent_workers)
    case('L17-L18', 'Concurrent coupled Git publications', concurrent_git)
    case('L19-L21', 'Git atomic, equal-ref and ABA controls', atomic_equal_aba)
    case('L22', 'Changed-parent range comparison', history)
    result = {'run': str(RUN), 'rows': ROWS, 'passed': sum(r['status'] == 'passed' for r in ROWS), 'failed': sum(r['status'] == 'failed' for r in ROWS)}
    dump(RUN / 'RESULTS.json', result)
    dump(ROOT / 'latest-followup-run.json', {'run': str(RUN), 'passed': result['passed'], 'failed': result['failed']})
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}))
    return 1 if result['failed'] else 0


if __name__ == '__main__':
    sys.exit(main())
