"""Finite structural-prefix campaign. All hosted effects stay in one namespace."""
from lab import *
import argparse
import signal
import sys
import traceback

FIXTURES = HOME / 'fixtures'
MATRIX = HOME / 'RESULTS.json'


def initialize():
    EVIDENCE.mkdir(exist_ok=True)
    FIXTURES.mkdir(exist_ok=True)
    repo = require(read('capabilities-repo', BASE), [200])
    save(HOME / 'capabilities.json', {key: repo['data'].get(key) for key in [
        'id', 'full_name', 'default_branch', 'private', 'permissions', 'allow_merge_commit',
        'allow_squash_merge', 'allow_rebase_merge', 'allow_auto_merge', 'archived']})
    if not (GIT / '.git').exists():
        result = command(['git', 'clone', '--single-branch', '--branch', 'main',
                          'https://github.com/' + REPO + '.git', str(GIT)])
        save(EVIDENCE / 'clone.json', {'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            raise RuntimeError('Clone failed')
        git('config', 'core.hooksPath', str(HOME / 'empty-hooks'))
        git('config', 'user.name', 'Josh Liebow-Feeser')
        git('config', 'user.email', 'hello@joshlf.com')
    return git('rev-parse', 'refs/remotes/origin/main')


def setup(name, topology, seed):
    directory = FIXTURES / name
    path = directory / 'fixture.json'
    if path.exists() and (directory / 'custody.json').exists():
        return json.loads(path.read_text())
    directory.mkdir(exist_ok=True)
    if path.exists():
        fixture = json.loads(path.read_text())
    else:
        prefix = PREFIX + name
        trunk_sha = commit(name + '-trunk', seed, {name + '/trunk.txt': 'trunk=1\n'})
        heads = {}
        parent = trunk_sha
        updates = {'refs/heads/' + prefix + '/trunk': trunk_sha}
        for letter in 'ABC':
            sha = commit(name + '-old-' + letter, parent, {name + '/' + letter + '.txt': letter + '=1\n'})
            heads[letter] = {'ref': prefix + '/' + letter, 'sha': sha, 'parent': parent}
            updates['refs/heads/' + heads[letter]['ref']] = sha
            updates['refs/tags/' + prefix + '/authored/' + letter + '/v1'] = sha
            parent = sha
        push(name + '-seed-push', updates, {})
        fixture = {'name': name, 'prefix': prefix, 'trunk': prefix + '/trunk',
                   'trunk_sha': trunk_sha, 'old_heads': heads, 'prs': {}, 'stack': None,
                   'topology': topology, 'created_at': now()}
        save(path, fixture)
    parentref = fixture['trunk']
    for letter, head in fixture['old_heads'].items():
        if letter not in fixture['prs']:
            response = require(api(name + '-seed-pr-' + letter, 'POST', BASE + '/pulls',
                                   {'head': head['ref'], 'base': parentref,
                                    'title': 'Structural restart ' + name + ': ' + letter,
                                    'body': 'Synthetic after-ack interruption fixture.\n\n' + NOTICE}), [201])
            fixture['prs'][letter] = response['data']['number']
            save(path, fixture)
        parentref = head['ref']
    if not fixture['stack']:
        response = require(api(name + '-seed-register', 'POST', BASE + '/stacks',
                               {'pull_requests': list(fixture['prs'].values())}), [201])
        fixture['stack'] = response['data']['number']
        save(path, fixture)
    order = list('CAB' if topology == 'reorder' else 'ADBC')
    parent = fixture['trunk_sha']
    newheads = {}
    for letter in order:
        sha = commit(name + '-new-' + letter, parent, {name + '/' + letter + '.txt': letter + '=1\n'})
        newheads[letter] = {'ref': fixture['prefix'] + '/' + letter, 'sha': sha, 'parent': parent}
        parent = sha
    fixture['new_heads'] = newheads
    fixture['order'] = order
    effects = [{'id': 'unstack', 'kind': 'unstack'}]
    for letter in 'BC':
        effects.append({'id': 'park-' + letter, 'kind': 'base', 'letter': letter, 'base': fixture['trunk']})
    effects.append({'id': 'heads-archives', 'kind': 'push'})
    if topology == 'insert':
        effects.append({'id': 'create-D', 'kind': 'create', 'letter': 'D', 'base': newheads['A']['ref']})
    for index, letter in enumerate(order):
        base = fixture['trunk'] if index == 0 else newheads[order[index - 1]]['ref']
        if letter == 'D' or base == fixture['trunk']:
            continue
        effects.append({'id': 'final-' + letter, 'kind': 'base', 'letter': letter, 'base': base})
    effects.append({'id': 'register', 'kind': 'register'})
    fixture['effects'] = effects
    fixture['initial'] = snapshot(fixture, name + '-initial')
    if any(pr['state'] != 'open' or pr['merged'] for pr in fixture['initial']['prs'].values()):
        raise RuntimeError('Initial lifecycle invalid')
    patches = {}
    for generation, heads in [('old', fixture['old_heads']), ('new', newheads)]:
        for letter, head in heads.items():
            patch = git('diff', '--binary', '--full-index', head['parent'], head['sha']) + '\n'
            patch_path = directory / (generation + '-' + letter + '.patch')
            patch_path.write_text(patch)
            paths = git('diff', '--name-only', head['parent'], head['sha']).splitlines()
            if paths != [name + '/' + letter + '.txt']:
                raise RuntimeError('Layer owns unexpected paths: ' + str(paths))
            patches[generation + '-' + letter] = {'path': patch_path.name,
                                                  'sha256': hashlib.sha256(patch.encode()).hexdigest(), 'paths': paths}
    if topology == 'reorder':
        if git('rev-parse', fixture['old_heads']['C']['sha'] + '^{tree}') != git('rev-parse', newheads['B']['sha'] + '^{tree}'):
            raise RuntimeError('Reorder changed final tree')
    fixture['patches'] = patches
    save(path, fixture)
    save(directory / 'custody.json', {'manifest_sha256': digest(fixture), 'created_at': now(),
                                     'scope': fixture['prefix'], 'sole_writer': 'this experiment only'})
    return fixture


def effect_label(fixture, effect):
    return fixture['name'] + '-effect-' + effect['id']


def known_prs(fixture):
    prs = dict(fixture['prs'])
    receipt = label_path(fixture['name'] + '-effect-create-D', '.receipt.json')
    if receipt.exists():
        value = json.loads(receipt.read_text())
        if value.get('http') == 201:
            prs['D'] = value['data']['number']
    return prs


def expected_request(fixture, effect, prs):
    kind = effect['kind']
    if kind == 'unstack':
        return 'POST', BASE + '/stacks/' + str(fixture['stack']) + '/unstack', None
    if kind == 'base':
        return 'PATCH', BASE + '/pulls/' + str(prs[effect['letter']]), {'base': effect['base']}
    if kind == 'create':
        return 'POST', BASE + '/pulls', {'head': fixture['new_heads']['D']['ref'], 'base': effect['base'],
            'title': 'Structural restart ' + fixture['name'] + ': D',
            'body': 'Synthetic inserted canonical review; independent file.\n\n' + NOTICE}
    if kind == 'register':
        return 'POST', BASE + '/stacks', {'pull_requests': [prs[letter] for letter in fixture['order']]}
    if kind == 'push':
        updates = {}
        expected = {}
        for letter, head in fixture['new_heads'].items():
            ref = 'refs/heads/' + head['ref']
            updates[ref] = head['sha']
            expected[ref] = fixture['initial']['refs'].get(ref, '')
            updates['refs/tags/' + fixture['prefix'] + '/authored/' + letter + '/v2'] = head['sha']
        return updates, expected
    raise RuntimeError('Unknown effect kind')


def load_prefix(fixture):
    completed = []
    gap = False
    prs = dict(fixture['prs'])
    for effect in fixture['effects']:
        label = effect_label(fixture, effect)
        receipt_path = label_path(label, '.receipt.json')
        intent = label_path(label, '.intent.json')
        if not receipt_path.exists():
            if intent.exists():
                raise RuntimeError('REFUSE missing receipt for dispatched effect: ' + effect['id'])
            gap = True
            continue
        if gap:
            raise RuntimeError('REFUSE noncontiguous effect receipts')
        receipt = json.loads(receipt_path.read_text())
        request = expected_request(fixture, effect, prs)
        if effect['kind'] == 'push':
            if (receipt['updates'], receipt['expected']) != request or receipt['exit'] != 0:
                raise RuntimeError('REFUSE invalid push evidence')
        else:
            if (receipt['method'], receipt['path'], receipt['payload']) != request:
                raise RuntimeError('REFUSE receipt/manifest mismatch')
            allowed = [204, 200] if effect['kind'] == 'unstack' else [201] if effect['kind'] in ('create', 'register') else [200]
            require(receipt, allowed)
        if effect['kind'] == 'create':
            prs['D'] = receipt['data']['number']
        completed.append((effect, receipt))
    return completed, prs


def expected_state(fixture, completed):
    initial = fixture['initial']
    expected_refs = dict(initial['refs'])
    prs = {letter: {key: value[key] for key in ['number', 'node_id', 'state', 'merged', 'head_ref', 'head_sha', 'base_ref']}
           for letter, value in initial['prs'].items()}
    group = fixture['stack']
    order = list('ABC')
    for effect, receipt in completed:
        kind = effect['kind']
        if kind == 'unstack':
            group = None
        elif kind == 'base':
            prs[effect['letter']]['base_ref'] = effect['base']
        elif kind == 'push':
            expected_refs.update(receipt['updates'])
            for letter in prs:
                prs[letter]['head_sha'] = fixture['new_heads'][letter]['sha']
        elif kind == 'create':
            value = receipt['data']
            prs['D'] = {'number': value['number'], 'node_id': value['node_id'], 'state': 'open', 'merged': False,
                         'head_ref': fixture['new_heads']['D']['ref'], 'head_sha': fixture['new_heads']['D']['sha'],
                         'base_ref': effect['base']}
        elif kind == 'register':
            group = receipt['data']['number']
            order = fixture['order']
    return {'refs': expected_refs, 'prs': prs, 'group': group, 'order': order}


def verify(fixture, completed, label):
    expected = expected_state(fixture, completed)
    extra = {letter: value['number'] for letter, value in expected['prs'].items() if letter not in fixture['prs']}
    actual = snapshot(fixture, label, extra)
    errors = []
    if actual['refs'] != expected['refs']:
        errors.append('refs differ from exact journal prefix')
    for letter, wanted in expected['prs'].items():
        observed = actual['prs'][letter]
        for key, value in wanted.items():
            if observed[key] != value:
                errors.append(letter + '.' + key + ' differs')
        stack = observed['stack']
        number = stack['number'] if stack else None
        if number != expected['group']:
            errors.append(letter + ' membership differs')
        if stack and stack.get('position') != expected['order'].index(letter) + 1:
            errors.append(letter + ' position differs')
    if expected['group'] is not None:
        group = require(read(label + '-group', BASE + '/stacks/' + str(expected['group'])), [200])
        members = [pr['number'] for pr in group['data']['pull_requests']]
        if members != [expected['prs'][letter]['number'] for letter in expected['order']]:
            errors.append('native group ordered membership differs')
    save(label_path(label, '.verification.json'), {'at': now(), 'expected': expected, 'errors': errors,
                                                  'snapshot': label_path(label, '.snapshot.json').name})
    if errors:
        raise RuntimeError('REFUSE stale or inconsistent live state: ' + '; '.join(errors))
    return actual


def execute(fixture, effect, prs):
    label = effect_label(fixture, effect)
    request = expected_request(fixture, effect, prs)
    if effect['kind'] == 'push':
        return push(label, *request)
    method, path, payload = request
    allowed = [200, 204] if effect['kind'] == 'unstack' else [201] if effect['kind'] in ('create', 'register') else [200]
    return require(api(label, method, path, payload), allowed)


def worker(name, boundary, runid):
    directory = FIXTURES / name
    fixture = json.loads((directory / 'fixture.json').read_text())
    custody = json.loads((directory / 'custody.json').read_text())
    if custody['manifest_sha256'] != digest(fixture):
        raise RuntimeError('REFUSE missing or changed custody/manifest')
    completed, prs = load_prefix(fixture)
    verify(fixture, completed, name + '-' + runid + '-start')
    resumed = len(completed)
    for effect in fixture['effects'][resumed:]:
        receipt = execute(fixture, effect, prs)
        completed.append((effect, receipt))
        if effect['kind'] == 'create':
            prs['D'] = receipt['data']['number']
        verified = verify(fixture, completed, name + '-' + runid + '-after-' + effect['id'])
        checkpoint = {'at': now(), 'pid': os.getpid(), 'effect': effect['id'],
                      'completed_count': len(completed), 'manifest_sha256': digest(fixture),
                      'receipt_sha256': digest(receipt), 'readback': verified}
        save(directory / ('checkpoint-' + runid + '-' + effect['id'] + '.json'), checkpoint)
        if effect['id'] == boundary:
            save(directory / ('boundary-' + runid + '.json'), checkpoint)
            os.kill(os.getpid(), signal.SIGSTOP)
    final = verify(fixture, completed, name + '-' + runid + '-final')
    save(directory / ('completion-' + runid + '.json'), {'at': now(), 'pid': os.getpid(), 'resumed_after_count': resumed,
                                                       'completed_count': len(completed), 'prs': prs, 'final': final})


def run_child(name, boundary, runid, kill=False):
    directory = FIXTURES / name
    out = directory / ('worker-' + runid + '.stdout.txt')
    err = directory / ('worker-' + runid + '.stderr.txt')
    args = [sys.executable, str(HOME / 'run.py'), 'worker', name, '--boundary', boundary, '--runid', runid]
    with out.open('w') as stdout, err.open('w') as stderr:
        child = subprocess.Popen(args, stdout=stdout, stderr=stderr)
        started = time.monotonic()
        marker = directory / ('boundary-' + runid + '.json')
        killed = False
        while child.poll() is None:
            if kill and marker.exists():
                os.kill(child.pid, signal.SIGKILL)
                killed = True
                break
            if time.monotonic() - started > 420:
                os.kill(child.pid, signal.SIGKILL)
                child.wait()
                raise RuntimeError('Bounded worker timeout; inspect before any retry')
            time.sleep(0.25)
        code = child.wait()
    record = {'at': now(), 'pid': child.pid, 'args': args, 'exit': code,
              'killed_after_durable_boundary': killed, 'elapsed': time.monotonic() - started,
              'stdout': out.name, 'stderr': err.name}
    save(directory / ('process-' + runid + '.json'), record)
    return record


def count_mutation_receipts(name):
    return sorted(path.name for path in EVIDENCE.glob(name + '-effect-*.receipt.json'))


def campaign():
    seed = initialize()
    results = json.loads(MATRIX.read_text()) if MATRIX.exists() else {'started_at': now(), 'cases': {}}
    cases = [('S01', 'reorder', 'unstack'), ('S02', 'reorder', 'park-B'),
             ('S03', 'reorder', 'park-C'), ('S04', 'reorder', 'heads-archives'),
             ('S05', 'reorder', 'final-A'), ('S06', 'reorder', 'final-B'),
             ('S07', 'reorder', 'register'), ('S08', 'insert', 'create-D'),
             ('S09', 'insert', 'register'), ('S10', 'reorder', 'unstack')]
    for caseid, topology, boundary in cases:
        if caseid in results['cases']:
            continue
        name = caseid.lower()
        print('START', caseid, topology, boundary, now(), flush=True)
        entry = {'id': caseid, 'topology': topology, 'boundary': boundary, 'started_at': now()}
        try:
            fixture = setup(name, topology, seed)
            entry.update(fixture=str((FIXTURES / name / 'fixture.json').relative_to(HOME)),
                         prs=fixture['prs'], original_stack=fixture['stack'])
            first = run_child(name, boundary, 'initial', kill=True)
            entry['interruption'] = first
            if first['exit'] != -signal.SIGKILL or not first['killed_after_durable_boundary']:
                raise RuntimeError('Worker did not reach selected acknowledged boundary')
            before = count_mutation_receipts(name)
            entry['receipts_before_recovery'] = before
            if caseid != 'S10':
                second = run_child(name, '', 'recovery')
                entry['recovery'] = second
                if second['exit']:
                    raise RuntimeError('Recovery refused or failed; retain fixture')
                completion = json.loads((FIXTURES / name / 'completion-recovery.json').read_text())
                entry['completion'] = completion
                entry['receipts_after_recovery'] = count_mutation_receipts(name)
                entry['disposition'] = 'performed-observed-recovered'
            else:
                receipt = label_path(name + '-effect-unstack', '.receipt.json')
                withheld = FIXTURES / name / 'withheld-unstack.receipt.json'
                receipt.replace(withheld)
                missing = run_child(name, '', 'missing-evidence')
                missing_no_write = count_mutation_receipts(name) == [path for path in before if path != receipt.name]
                withheld.replace(receipt)
                entry['missing_evidence'] = {'process': missing, 'no_new_effect_receipt': missing_no_write,
                                             'restored_receipt_sha256': digest(json.loads(receipt.read_text()))}
                if missing['exit'] == 0 or not missing_no_write:
                    raise RuntimeError('Missing-evidence negative failed')
                advanced = commit(name + '-stale-control-B', fixture['old_heads']['B']['sha'], {name + '/B.txt': 'B=external-control\n'})
                push(name + '-stale-control-push', {'refs/heads/' + fixture['old_heads']['B']['ref']: advanced,
                     'refs/tags/' + fixture['prefix'] + '/control/B/stale': advanced},
                     {'refs/heads/' + fixture['old_heads']['B']['ref']: fixture['old_heads']['B']['sha']})
                stale = run_child(name, '', 'stale-live')
                stale_no_write = count_mutation_receipts(name) == before
                entry['stale_live'] = {'process': stale, 'no_new_effect_receipt': stale_no_write,
                                       'live_control_head': advanced}
                if stale['exit'] == 0 or not stale_no_write:
                    raise RuntimeError('Stale-state negative failed')
                entry['disposition'] = 'performed-refused-missing-and-stale-retained-stopped'
            entry['finished_at'] = now()
        except Exception as error:
            entry.update(disposition='performed-unresolved-stopped', error=str(error), traceback=traceback.format_exc())
            print('FAIL', caseid, str(error)[:400], flush=True)
        results['cases'][caseid] = entry
        save(MATRIX, results)
        print('END', caseid, entry['disposition'], now(), flush=True)
    results['finished_at'] = now()
    save(MATRIX, results)
    print('CAMPAIGN DONE', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['campaign', 'worker'])
    parser.add_argument('name', nargs='?')
    parser.add_argument('--boundary', default='')
    parser.add_argument('--runid', default='recovery')
    arguments = parser.parse_args()
    if arguments.mode == 'campaign':
        campaign()
    else:
        try:
            worker(arguments.name, arguments.boundary, arguments.runid)
        except Exception as error:
            save(FIXTURES / arguments.name / ('refusal-' + arguments.runid + '.json'),
                 {'at': now(), 'pid': os.getpid(), 'error': str(error), 'traceback': traceback.format_exc()})
            raise
