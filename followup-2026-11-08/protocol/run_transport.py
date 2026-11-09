"""Real full-send/no-response-read experiments, each on a fresh fixture."""
from lab import *
import argparse

arguments = argparse.ArgumentParser()
arguments.add_argument('--hold-ms', type=int, choices=(0, 200, 500, 1000), default=0)
options = arguments.parse_args()
VARIANT = '-H' + str(options.hold_ms) if options.hold_ms else ''
RESULT = HOME / ('transport-results' + VARIANT + '.json')
base_fixture = fixture
base_lost_send = lost_send


def fixture(name, *args, **kwargs):
    return base_fixture(name + VARIANT.lower(), *args, **kwargs)


def lost_send(*args, **kwargs):
    return base_lost_send(*args, hold_ms=options.hold_ms, **kwargs)


def three_reads(label, observer):
    samples = []
    for index, pause in enumerate((0, 2, 3)):
        if pause:
            time.sleep(pause)
        samples.append(observer(label + '-oracle-' + str(index)))
    return samples


def run():
    if RESULT.exists():
        raise RuntimeError('Transport run already recorded; never replay')
    preflight = {name: summary(api('preflight-' + name + VARIANT, 'GET', path))
                 for name, path in [
                     ('repo', BASE), ('main', BASE + '/branches/main'),
                     ('rulesets', BASE + '/rulesets'),
                     ('workflows', BASE + '/actions/workflows')]}
    save(HOME / ('preflight' + VARIANT + '.json'), preflight)
    results = {}

    def record(case_id, label, fault, samples, interpretation):
        results[case_id] = {'label': label, 'fault': fault, 'oracle_samples': samples,
                            'interpretation': interpretation,
                            'no_resend': True, 'no_further_fixture_writes': True}
        save(RESULT, results)
        print(case_id + ' recorded', flush=True)

    case = fixture('lost-pr', 1, create_prs=False)
    label = 'P-T01' + VARIANT
    fault = lost_send(label, 'POST', BASE + '/pulls', pr_payload(case, 0))
    query = urllib.parse.urlencode({'state': 'all', 'head': 'joshlf:' + case['heads'][0]['ref'],
                                    'base': case['trunk'], 'per_page': 100})
    samples = three_reads(label, lambda name: summary(read(name, BASE + '/pulls?' + query)))
    matches = [p['number'] for p in (samples[-1].get('data') or [])
               if p.get('head', {}).get('ref') == case['heads'][0]['ref']
               and p.get('body') == pr_payload(case, 0)['body']]
    record(label, 'PR create', fault, samples,
           {'matching_prs': matches, 'effect': 'positive identified object' if matches else 'no match in bounded observations',
            'general_idempotency': False})

    case = fixture('lost-comment', 1)
    label = 'P-T02' + VARIANT
    body = 'Unique synthetic in-flight comment ' + label + ' / lost-comment.\n\n' + NOTICE
    path = BASE + '/issues/' + str(case['prs'][0]) + '/comments'
    fault = lost_send(label, 'POST', path, {'body': body})
    samples = three_reads(label, lambda name: summary(read(name, path + '?per_page=100')))
    matches = [c['id'] for c in (samples[-1].get('data') or []) if c.get('body') == body]
    record(label, 'comment create', fault, samples,
           {'matching_comments': matches, 'effect': 'positive identified object' if matches else 'no match in bounded observations',
            'general_idempotency': False})

    case = fixture('lost-base', 1)
    alias = case['prefix'] + '/alternate-trunk'
    push('lost-base-alias' + VARIANT, {'refs/heads/' + alias: case['trunk_sha']})
    label = 'P-T03' + VARIANT
    before = observe(case, label + '-before')
    fault = lost_send(label, 'PATCH', BASE + '/pulls/' + str(case['prs'][0]), {'base': alias})
    samples = three_reads(label, lambda name: observe(case, name))
    record(label, 'base PATCH', fault, samples,
           {'before_base': before['prs'][0]['base']['ref'], 'desired_base': alias,
            'observed_base': samples[-1]['prs'][0]['base']['ref'],
            'effect': 'positive transition' if samples[-1]['prs'][0]['base']['ref'] == alias else 'not observed',
            'general_causal_fence': False})

    case = fixture('lost-stack-create', 2)
    label = 'P-T04' + VARIANT
    fault = lost_send(label, 'POST', BASE + '/stacks', {'pull_requests': case['prs']})
    samples = three_reads(label, lambda name: summary(read(name, BASE + '/stacks?pull_request=' + str(case['prs'][0]))))
    groups = samples[-1].get('data') or []
    record(label, 'stack create', fault, samples,
           {'groups': [{'number': g['number'], 'members': [p['number'] for p in g['pull_requests']]} for g in groups],
            'effect': 'positive grouping' if groups else 'no grouping in bounded observations',
            'sole_writer_attribution_only': True})

    case = fixture('lost-stack-append', 3)
    stack = register(case, numbers=case['prs'][:2])
    label = 'P-T05' + VARIANT
    fault = lost_send(label, 'POST', BASE + '/stacks/' + str(stack) + '/add',
                      {'pull_requests': case['prs'][2:]})
    samples = three_reads(label, lambda name: summary(read(name, BASE + '/stacks/' + str(stack))))
    members = [p['number'] for p in (samples[-1].get('data') or {}).get('pull_requests', [])]
    record(label, 'stack append', fault, samples,
           {'expected': case['prs'], 'observed': members,
            'effect': 'positive appended membership' if members == case['prs'] else 'expected membership not observed',
            'sole_writer_attribution_only': True})

    case = fixture('lost-stack-unstack', 2)
    stack = register(case)
    label = 'P-T06' + VARIANT
    fault = lost_send(label, 'POST', BASE + '/stacks/' + str(stack) + '/unstack')
    samples = three_reads(label, lambda name: observe(case, name, stack=stack))
    record(label, 'stack unstack', fault, samples,
           {'memberships': [p['stack'] for p in samples[-1]['prs']],
            'stack_http': samples[-1]['stack']['http'],
            'effect': ('observed membership absence; client dispatch remains unknown'
                       if all(p['stack'] is None for p in samples[-1]['prs'])
                       else 'membership still present; unstack effect not observed'),
            'absence_is_not_quiescence': True})

    case = fixture('lost-merge', 2)
    stack = register(case)
    label = 'P-T07' + VARIANT
    fault = lost_send(label, 'PUT', BASE + '/pulls/' + str(case['prs'][-1]) + '/merge-async',
                      {'merge_method': 'squash', 'merge_action': 'direct_merge',
                       'sha': case['heads'][-1]['sha']})
    samples = []
    started = time.monotonic()
    for index in range(12):
        samples.append(observe(case, label + '-oracle-' + str(index), stack=stack, include_refs=True))
        if all(p['merged'] for p in samples[-1]['prs']) or time.monotonic() - started >= 35:
            break
        time.sleep(min(3, max(0, 35 - (time.monotonic() - started))))
    git('fetch', 'origin', 'refs/heads/' + case['trunk'])
    actual = git('rev-parse', 'FETCH_HEAD^{tree}')
    expected = git('rev-parse', case['heads'][-1]['sha'] + '^{tree}')
    record(label, 'direct async merge', fault, samples,
           {'all_members_observed_merged': all(p['merged'] for p in samples[-1]['prs']),
            'expected_tree': expected, 'observed_trunk_tree': actual,
            'tree_matches': actual == expected, 'uuid_known': False,
            'http_status_known': False, 'same_intent_resubmitted': False,
            'provider_quiescence_established': False})

    case = fixture('partial-pr', 1, create_prs=False)
    label = 'P-T08' + VARIANT
    fault = lost_send(label, 'POST', BASE + '/pulls', pr_payload(case, 0), incomplete=True)
    query = urllib.parse.urlencode({'state': 'all', 'head': 'joshlf:' + case['heads'][0]['ref'],
                                    'base': case['trunk'], 'per_page': 100})
    samples = three_reads(label, lambda name: summary(read(name, BASE + '/pulls?' + query)))
    record(label, 'truncated PR create negative', fault, samples,
           {'matching_prs': [p['number'] for p in (samples[-1].get('data') or [])],
            'limit': 'Bounded absence control; no general guarantee inferred from EOF behavior'})


if __name__ == '__main__':
    run()
