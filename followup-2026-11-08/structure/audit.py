"""Independent final observations and static accounting for the finite campaign."""
from lab import *
from run import load_prefix, verify, known_prs, effect_label

results = json.loads((HOME / 'RESULTS.json').read_text())
summary = {'at': now(), 'fixtures': {}, 'source_hashes': {}, 'mutations': {}, 'errors': []}
for name in ['lab.py', 'run.py', 'audit.py']:
    summary['source_hashes'][name] = hashlib.sha256((HOME / name).read_bytes()).hexdigest()
baseline = json.loads((HOME / 'SOURCE-VERSION.json').read_text())
summary['executor_sources_unchanged'] = all(summary['source_hashes'][name] == baseline[name]['sha256'] for name in ['lab.py', 'run.py'])
if not summary['executor_sources_unchanged']:
    summary['errors'].append('Executor source changed during campaign')
for directory in sorted((HOME / 'fixtures').iterdir()):
    path = directory / 'fixture.json'
    if not path.exists():
        continue
    fixture = json.loads(path.read_text())
    name = fixture['name']
    entry = {'prs': known_prs(fixture), 'patches': {}, 'effects': {}, 'errors': []}
    completed, prs = load_prefix(fixture)
    if name == 's10':
        entry['final'] = snapshot(fixture, name + '-audit-retained-negative')
        entry['retained_reason'] = 'deliberate stale live head; no executor mutation authority restored'
    else:
        entry['final'] = verify(fixture, completed, name + '-audit-final')
        entry['completed_count'] = len(completed)
        if len(completed) != len(fixture['effects']):
            entry['errors'].append('Incomplete effect prefix')
    entry['old_stack_number'] = fixture['stack']
    first_pr = next(iter(entry['final']['prs'].values()))
    entry['final_stack_number'] = first_pr['stack']['number'] if first_pr['stack'] else None
    for letter in 'ABC':
        old = (directory / ('old-' + letter + '.patch')).read_bytes()
        new = (directory / ('new-' + letter + '.patch')).read_bytes()
        entry['patches'][letter] = {'old_sha256': hashlib.sha256(old).hexdigest(),
                                    'new_sha256': hashlib.sha256(new).hexdigest(),
                                    'byte_identical': old == new}
        if old != new:
            entry['errors'].append('Changed layer patch ' + letter)
    if fixture['topology'] == 'insert':
        top_delta = (git('diff', '--binary', '--full-index', fixture['old_heads']['C']['sha'], fixture['new_heads']['C']['sha']) + '\n').encode()
        expected_delta = (directory / 'new-D.patch').read_bytes()
        entry['insertion_top_tree_delta_is_exact_D_patch'] = top_delta == expected_delta
        if top_delta != expected_delta:
            entry['errors'].append('Insertion changed final tree beyond exact D patch')
    for letter, number in entry['prs'].items():
        record = require(read(name + '-audit-head-uniqueness-' + letter,
             BASE + '/pulls?state=all&head=joshlf:' + fixture['prefix'] + '/' + letter + '&per_page=100'), [200])
        matches = [value['number'] for value in record['data']]
        entry.setdefault('head_pr_uniqueness', {})[letter] = matches
        if matches != [number]:
            entry['errors'].append('Unexpected PR set for ' + letter)
    for effect in fixture['effects']:
        label = effect_label(fixture, effect)
        intent = label_path(label, '.intent.json')
        receipt = label_path(label, '.receipt.json')
        entry['effects'][effect['id']] = {'intent_exists': intent.exists(), 'receipt_exists': receipt.exists(),
                                          'intent': intent.name, 'receipt': receipt.name}
    entry['original_nodes_retained'] = {letter: entry['final']['prs'][letter]['node_id'] == fixture['initial']['prs'][letter]['node_id'] for letter in 'ABC'}
    entry['old_archives_retained'] = {letter: entry['final']['refs'].get('refs/tags/' + fixture['prefix'] + '/authored/' + letter + '/v1') == fixture['old_heads'][letter]['sha'] for letter in 'ABC'}
    entry['new_archives_retained'] = {letter: entry['final']['refs'].get('refs/tags/' + fixture['prefix'] + '/authored/' + letter + '/v2') == head['sha'] for letter, head in fixture['new_heads'].items()} if name != 's10' else {'not_published_in_stopped_fixture': True}
    if not all(entry['original_nodes_retained'].values()) or not all(entry['old_archives_retained'].values()) or not all(entry['new_archives_retained'].values()):
        entry['errors'].append('Canonical identity or archive mismatch')
    entry['all_canonical_prs_open_unmerged'] = all(value['state'] == 'open' and not value['merged']
                                                   for value in entry['final']['prs'].values())
    if not entry['all_canonical_prs_open_unmerged']:
        entry['errors'].append('Unexpected lifecycle')
    if name == 's10':
        missing = json.loads((directory / 'refusal-missing-evidence.json').read_text())
        stale = json.loads((directory / 'refusal-stale-live.json').read_text())
        entry['negative_refusals'] = {'missing': missing['error'], 'stale': stale['error'],
                                      'effect_dispatch_intents': [value['intent'] for value in entry['effects'].values() if value['intent_exists']]}
        if entry['negative_refusals']['effect_dispatch_intents'] != [name + '-effect-unstack.intent.json']:
            entry['errors'].append('Negative fixture dispatched extra executor effect')
    summary['fixtures'][name] = entry
    summary['errors'].extend(name + ': ' + error for error in entry['errors'])
for path in EVIDENCE.glob('*.intent.json'):
    value = json.loads(path.read_text())
    if 'method' not in value or value['method'] != 'GET':
        summary['mutations'][path.name] = {'method': value.get('method', 'git-push'),
                                         'receipt_exists': path.with_name(path.name.replace('.intent.json', '.receipt.json')).exists()}
summary['new_pr_count'] = sum(len(entry['prs']) for entry in summary['fixtures'].values())
summary['all_expected_pr_count'] = summary['new_pr_count'] == 32
if not summary['all_expected_pr_count']:
    summary['errors'].append('Expected exactly 32 scoped fixture PRs')
summary['all_mutations_have_receipts'] = all(item['receipt_exists'] for item in summary['mutations'].values())
check = git('fsck', '--full', '--no-reflogs', check=False)
summary['git_fsck'] = {'exit': check.returncode, 'stdout': check.stdout, 'stderr': check.stderr}
if check.returncode:
    summary['errors'].append('Git fsck failed')
if not summary['all_mutations_have_receipts']:
    summary['errors'].append('Unreceipted mutation remains')
summary['completed_at'] = now()
save(HOME / 'FINAL-AUDIT.json', summary)
print(json.dumps({'new_pr_count': summary['new_pr_count'], 'fixture_count': len(summary['fixtures']),
                  'mutation_count': len(summary['mutations']), 'errors': summary['errors'],
                  'git_fsck_exit': check.returncode}, indent=2))
