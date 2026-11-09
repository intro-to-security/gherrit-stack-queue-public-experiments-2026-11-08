"""Retain exact authored and observed Git objects using read-only hosted access."""
from lab import *


def run():
    state = resources()
    before = now()
    refs = git('ls-remote', 'origin', 'refs/heads/' + PREFIX + '*', 'refs/tags/' + PREFIX + '*')
    (EVIDENCE / 'final-native-refs.txt').write_text(refs + '\n')
    git('fetch', 'origin', '+refs/heads/' + PREFIX + '*:refs/remotes/protocol-observed/*')
    bundle = EVIDENCE / 'authored-and-observed.bundle'
    if bundle.exists():
        raise RuntimeError('Retain existing bundle rather than silently overwrite')
    git('bundle', 'create', str(bundle), '--all')
    verification = git('bundle', 'verify', str(bundle))
    sampled_runs = {}
    for name in ('size-boundary', 'fresh-direct100', 'fresh-increment101'):
        case = state[name]
        for index in (0, len(case['heads']) - 1):
            head = case['heads'][index]
            query = urllib.parse.urlencode({'branch': head['ref'], 'per_page': 1})
            response = read('final-actions-' + name + '-' + str(index + 1), BASE + '/actions/runs?' + query)
            sampled_runs[head['ref']] = {'http': response['http'],
                                         'total_count': (response.get('data') or {}).get('total_count')}
    save(HOME / 'final-capture.json',
         {'started_at': before, 'finished_at': now(), 'native_ref_lines': len(refs.splitlines()),
          'ref_file': 'evidence/final-native-refs.txt',
          'bundle': 'evidence/authored-and-observed.bundle',
          'bundle_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
          'bundle_verify_stdout': verification, 'sampled_actions_runs': sampled_runs,
          'limit': 'Final non-atomic readback; not a provider quiescence fence. No hosted mutation occurred.'})
    print(json.dumps({'native_refs': len(refs.splitlines()),
                      'bundle_bytes': bundle.stat().st_size, 'sampled_actions_runs': sampled_runs}))


if __name__ == '__main__':
    run()
