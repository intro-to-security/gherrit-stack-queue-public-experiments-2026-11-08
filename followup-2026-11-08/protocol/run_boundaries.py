"""Real distinct-PR native API size and lifecycle boundary matrix."""
from lab import *
import sys

RESULT = HOME / 'boundary-results.json'


def run():
    results = json.loads(RESULT.read_text()) if RESULT.exists() else {}

    def record(case_id, value):
        results[case_id] = value
        save(RESULT, results)
        print(case_id + ' recorded', flush=True)

    def stack_request(label, numbers):
        return api(label, 'POST', BASE + '/stacks', {'pull_requests': numbers})

    def unstack(label, number):
        response = api(label, 'POST', BASE + '/stacks/' + str(number) + '/unstack')
        if response['http'] != 204:
            raise RuntimeError('Expected full release not established')
        confirmed = read(label + '-readback', BASE + '/stacks/' + str(number))
        if confirmed['http'] != 404:
            raise RuntimeError('Group still visible after release')
        return summary(response)

    if '--remaining-only' not in sys.argv:
        case = fixture('minimum', 2)
        minimum = {}
        for count in (0, 1, 2):
            response = stack_request('P-B00-size-' + str(count), case['prs'][:count])
            minimum[str(count)] = summary(response)
            if response['http'] == 201:
                minimum[str(count)]['observation'] = summary(read('P-B00-read-' + str(count), BASE + '/stacks/' + str(response['data']['number'])))
                minimum[str(count)]['release'] = unstack('P-B00-release-' + str(count), response['data']['number'])
        record('P-B00', minimum)

        case = fixture('size-boundary', 101)
        boundary = {'distinct_real_pr_count': len(set(case['prs'])),
                    'workflow_files': case['workflow_files'], 'prs': case['prs']}
        for count in (101, 99, 100):
            response = stack_request('P-B01-size-' + str(count), case['prs'][:count])
            boundary[str(count)] = summary(response)
            if response['http'] == 201:
                stack = response['data']['number']
                observed = read('P-B01-read-' + str(count), BASE + '/stacks/' + str(stack))
                boundary[str(count)]['readback'] = summary(observed)
                boundary[str(count)]['readback_count'] = len((observed['data'] or {}).get('pull_requests', []))
                boundary[str(count)]['release'] = unstack('P-B01-release-' + str(count), stack)
        record('P-B01', boundary)

        stack = register(case, 'P-B02-register-99', case['prs'][:99])
        append = {'initial_stack': stack, 'initial_size': 99}
        for count in (100, 101):
            response = api('P-B02-append-' + str(count), 'POST', BASE + '/stacks/' + str(stack) + '/add',
                           {'pull_requests': [case['prs'][count - 1]]})
            observed = read('P-B02-read-' + str(count), BASE + '/stacks/' + str(stack))
            members = [p['number'] for p in (observed['data'] or {}).get('pull_requests', [])]
            append[str(count)] = {'request': summary(response), 'readback': summary(observed),
                                  'count': len(members), 'exact_expected_prefix': members == case['prs'][:len(members)]}
            if response['http'] not in (200, 422):
                raise RuntimeError('Unexpected append result; no next write')
        record('P-B02', append)

    case = fixture('invalid-order', 3)
    malformed = {}
    variants = {'duplicate': [case['prs'][0], case['prs'][0]],
                'reverse': list(reversed(case['prs'][:2])),
                'wrong-base': [case['prs'][0], case['prs'][2]],
                'missing-pr': [case['prs'][0], 2147483647]}
    for kind, numbers in variants.items():
        response = stack_request('P-B03-' + kind, numbers)
        malformed[kind] = summary(response)
        if response['http'] == 201:
            malformed[kind]['release'] = unstack('P-B03-' + kind + '-release', response['data']['number'])
    stack = register(case, 'P-B03-valid-control')
    malformed['valid-control'] = summary(read('P-B03-valid-read', BASE + '/stacks/' + str(stack)))
    malformed['already-member-create'] = summary(stack_request('P-B03-already-member', case['prs']))
    record('P-B03', malformed)

    case = fixture('closed-upper', 2)
    close = api('P-B04-close-upper', 'PATCH', BASE + '/pulls/' + str(case['prs'][1]), {'state': 'closed'})
    if close['http'] != 200:
        raise RuntimeError('Close control failed')
    response = stack_request('P-B04-closed-register', case['prs'])
    closed = {'close': summary(close), 'register_closed': summary(response),
              'observation': observe(case, 'P-B04-after-register')}
    if response['http'] == 201:
        closed['release'] = unstack('P-B04-release-closed', response['data']['number'])
    reopened = api('P-B04-reopen-upper', 'PATCH', BASE + '/pulls/' + str(case['prs'][1]), {'state': 'open'})
    closed['reopen'] = summary(reopened)
    if reopened['http'] == 200:
        stack = register(case, 'P-B04-open-register')
        closed['open-control'] = summary(read('P-B04-open-read', BASE + '/stacks/' + str(stack)))
    record('P-B04', closed)

    case = fixture('deleted-upper', 2)
    ref = 'refs/heads/' + case['heads'][1]['ref']
    removed = push('P-B05-delete-owned-upper', {ref: ''}, {ref: case['heads'][1]['sha']})
    before = observe(case, 'P-B05-after-delete', include_refs=True)
    response = stack_request('P-B05-deleted-register', case['prs'])
    record('P-B05', {'deleted_ref': ref, 'original_object': case['heads'][1]['sha'],
                      'retained_tag': 'refs/tags/' + case['prefix'] + '/authored/002',
                      'push': removed, 'observation': before, 'registration': summary(response),
                      'after': observe(case, 'P-B05-final', stack=(response['data']['number'] if response['http'] == 201 else None))})


if __name__ == '__main__':
    run()
