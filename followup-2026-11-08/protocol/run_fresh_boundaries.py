"""Use disjoint identities after the retained unknown99-member creation."""
from lab import *

RESULT = HOME / 'fresh-boundary-results.json'


def group_members(label, stack):
    response = read(label, BASE + '/stacks/' + str(stack))
    data = response.get('data') or {}
    return {'http': response['http'], 'members': [p['number'] for p in data.get('pull_requests', [])],
            'receipt': str(evidence_path(response['label'], '.receipt.json').relative_to(HOME))}


def run():
    if RESULT.exists():
        raise RuntimeError('Fresh driver already recorded; reconcile rather than replay')
    results = {}
    case = fixture('fresh-direct100', 100)
    label = 'P-B01-F100'
    try:
        response = api(label + '-create', 'POST', BASE + '/stacks', {'pull_requests': case['prs']})
        result = {'http': response['http'], 'response': summary(response),
                  'effect_unknown': False, 'prs': case['prs']}
    except RuntimeError:
        receipt_path = evidence_path(label + '-create', '.receipt.json')
        if not receipt_path.exists():
            raise
        response = json.loads(receipt_path.read_text())
        if response['http'] < 500:
            raise
        result = {'http': response['http'], 'response': summary(response),
                  'effect_unknown': True, 'prs': case['prs'],
                  'decision': 'No retry or any further fixture mutation; read-only reconciliation only'}
    group = read(label + '-oracle', BASE + '/stacks?pull_request=' + str(case['prs'][0]))
    observed = [{'number': g['number'], 'count': len(g['pull_requests']),
                 'exact_ordered_members': [p['number'] for p in g['pull_requests']] == case['prs']}
                for g in (group.get('data') or [])]
    result['read_only_oracle'] = observed
    results[label] = result
    save(RESULT, results)
    print(label + ' recorded', flush=True)

    case = fixture('fresh-increment101', 101)
    label = 'P-B02-F101'
    initial = api(label + '-create2', 'POST', BASE + '/stacks', {'pull_requests': case['prs'][:2]})
    result = {'initial': summary(initial), 'prs': case['prs'], 'appends': [],
              'provider_quiescence_claimed': False}
    results[label] = result
    save(RESULT, results)
    if initial['http'] != 201:
        result['disposition'] = 'initial registration unavailable; stop'
        save(RESULT, results)
        return
    stack = initial['data']['number']
    result['stack'] = stack
    current = 2
    while current < 101:
        target = min(current + 8, 98) if current < 98 else current + 1
        operation = label + '-append-to-' + str(target)
        try:
            response = api(operation, 'POST', BASE + '/stacks/' + str(stack) + '/add',
                           {'pull_requests': case['prs'][current:target]})
        except RuntimeError:
            receipt = evidence_path(operation, '.receipt.json')
            result['unknown_operation'] = operation
            result['decision'] = 'Stop fixture; no further mutations or retry'
            if receipt.exists():
                response = json.loads(receipt.read_text())
                result['unknown_receipt'] = summary(response)
            result['read_only_after_unknown'] = group_members(operation + '-unknown-oracle', stack)
            save(RESULT, results)
            raise
        observed = group_members(operation + '-readback', stack)
        row = {'from': current, 'to': target, 'http': response['http'],
               'response': summary(response), 'readback': observed,
               'count': len(observed['members']),
               'exact_expected_prefix': observed['members'] == case['prs'][:len(observed['members'])]}
        result['appends'].append(row)
        save(RESULT, results)
        if response['http'] == 200 and observed['members'] == case['prs'][:target]:
            current = target
        elif response['http'] == 422:
            result['disposition'] = 'known rejection at size' + str(target)
            save(RESULT, results)
            break
        else:
            result['disposition'] = 'unexpected response/readback; stop without further mutations'
            save(RESULT, results)
            break
    else:
        result['disposition'] = 'append101 accepted'
        save(RESULT, results)
    print(label + ' recorded', flush=True)


if __name__ == '__main__':
    run()
