"""Build the case matrix and audit evidence without native writes."""
from lab import *


def assess():
    matrix = []
    for file_name, variant in [('transport-results.json', 'immediate close'),
                               ('transport-results-H500.json', '500ms hold, no HTTP read')]:
        source = json.loads((HOME / file_name).read_text())
        for case_id, result in source.items():
            fault = result['fault']
            wire = json.loads(evidence_path(case_id, '.wire-description.json').read_text())
            decision = json.loads(evidence_path(case_id, '.recovery-before-oracle.json').read_text())
            intents = [json.loads(p.read_text()) for p in EVIDENCE.glob(case_id + '-oracle-*.intent.json')]
            decision_precedes_oracles = bool(intents) and all(
                decision['monotonic'] < intent['monotonic_start'] for intent in intents)
            matrix.append({'id': case_id, 'disposition': 'performed',
                           'operation': result['label'], 'variant': variant,
                           'request_method': fault['method'], 'request_path': fault['path'],
                           'request_payload': fault['payload'],
                           'all_planned_bytes_sent': fault['tls_bytes_send_returned'] == fault['expected_send_bytes'],
                           'intentionally_omitted_body_bytes': wire['incomplete_by_bytes'],
                           'http_receive_calls': fault['http_receive_calls'],
                           'http_status_known': False,
                           'client_decision_before_every_oracle': decision_precedes_oracles,
                           'client_decision': decision['decision'], 'resent': False,
                           'observed': result['interpretation'], 'source': file_name,
                           'limits': ['Sole-writer fixture attribution', 'No provider idempotency or quiescence guarantee',
                                      'Local TLS send completion does not establish remote receipt',
                                      'Status/response may have been buffered during a hold but was never read']})
    raw = json.loads((HOME / 'raw-control-results.json').read_text())
    matrix.append({'id': 'P-T09', 'disposition': 'performed', 'observed': raw['P-T09'],
                   'source': 'raw-control-results.json'})
    boundaries = json.loads((HOME / 'boundary-results.json').read_text())
    for case_id, data in boundaries.items():
        if case_id == 'P-B00':
            observed = {count: response['http'] for count, response in data.items()}
        elif case_id == 'P-B01':
            observed = {str(count): {'http': data[str(count)]['http'],
                                     'readback_count': data[str(count)].get('readback_count')}
                        for count in (99, 100, 101)}
            observed.update(distinct_real_pr_count=data['distinct_real_pr_count'],
                            workflow_files=data['workflow_files'],
                            original99_effect='HTTP504 but group330 observed with exact intended99 members',
                            original100_result='422 duplicate membership; contaminated and excluded as capacity evidence',
                            clean_replacement='P-B01-F100')
        elif case_id == 'P-B02':
            observed = {str(count): {'http': data[str(count)]['request']['http'],
                                     'observed_count': data[str(count)]['count'],
                                     'exact_prefix': data[str(count)]['exact_expected_prefix']}
                        for count in (100, 101)}
        elif case_id == 'P-B03':
            observed = {name: response.get('http') for name, response in data.items()}
        elif case_id == 'P-B04':
            observed = {'closed_registration_http': data['register_closed']['http'],
                        'reopen_http': data['reopen']['http'],
                        'open_control_http': data.get('open-control', {}).get('http')}
        elif case_id == 'P-B05':
            observed = {'deleted_registration_http': data['registration']['http'],
                        'pr_states_after_delete': [{'number': p['number'], 'state': p['state'], 'merged': p['merged']}
                                                   for p in data['observation']['prs']],
                        'original_head_retained_in_tag': data['retained_tag']}
        matrix.append({'id': case_id, 'disposition': 'performed', 'observed': observed,
                       'source': 'boundary-results.json',
                       'limits': ['Observed hosted behavior on the recorded date/settings; no inferred permanent guarantee']})
    if 'P-B02' not in boundaries:
        matrix.append({'id': 'P-B02', 'disposition': 'failed premise; replaced by P-B02-F101',
                       'observed': {'original_fixture_append_performed': False,
                                    'reason': 'Blind repeated99-create after504 returned422 existing membership; no valid append boundary observation'},
                       'source': 'evidence/boundary-driver-deviation.json'})
    fresh = json.loads((HOME / 'fresh-boundary-results.json').read_text())
    for case_id, result in fresh.items():
        if case_id == 'P-B01-F100':
            observed = {'http': result['http'], 'effect_unknown': result['effect_unknown'],
                        'read_only_oracle': result['read_only_oracle']}
        else:
            observed = {'initial_http': result['initial']['http'], 'stack': result.get('stack'),
                        'boundaries': {str(row['to']): {'http': row['http'], 'count': row['count'],
                                                       'exact_prefix': row['exact_expected_prefix']}
                                       for row in result['appends'] if row['to'] >= 98},
                        'disposition': result.get('disposition'),
                        'unknown_operation': result.get('unknown_operation')}
        matrix.append({'id': case_id, 'disposition': 'performed', 'observed': observed,
                       'source': 'fresh-boundary-results.json',
                       'limits': ['Fresh disjoint identities; original group330 untouched', 'No provider quiescence claim']})
    matrix.append({'id': 'P-R01', 'disposition': 'reused prior evidence',
                   'source': 'reused-evidence.json'})
    credential = token().encode()
    matches = []
    for path in HOME.rglob('*'):
        if path.is_file() and GIT not in path.parents and credential in path.read_bytes():
            matches.append(str(path.relative_to(HOME)))
    creations = []
    mutations = []
    unresolved_ordinary = []
    receipts = list(EVIDENCE.glob('*.receipt.json'))
    for path in EVIDENCE.glob('*.intent.json'):
        record = json.loads(path.read_text())
        if record['method'] not in ('GET', 'HEAD'):
            mutations.append(record)
            if record['method'] == 'POST' and record['path'] == BASE + '/pulls':
                creations.append(record)
            label = record['label']
            if evidence_path(label, '.unknown.json').exists() or (
                    not evidence_path(label, '.receipt.json').exists() and
                    not evidence_path(label, '.transport.json').exists()):
                unresolved_ordinary.append(label)
    creations.sort(key=lambda r: r['started_at'])
    intervals = [(datetime.datetime.fromisoformat(b['started_at']) -
                  datetime.datetime.fromisoformat(a['started_at'])).total_seconds()
                 for a, b in zip(creations, creations[1:])]
    state = resources()
    declared = [row['id'] for row in matrix]
    expected = (['P-T' + str(i).zfill(2) for i in range(1, 9)] +
                ['P-T' + str(i).zfill(2) + '-H500' for i in range(1, 9)] +
                ['P-T09'] + ['P-B' + str(i).zfill(2) for i in range(6)] +
                ['P-B01-F100', 'P-B02-F101', 'P-R01'])
    audit = {'at': now(), 'credential_value_matches_in_evidence': matches,
             'retained_unknown_ordinary_write_intents': unresolved_ordinary,
             'all_planned_case_ids_accounted_for': set(expected) == set(declared),
             'all_no_read_faults_sent_planned_bytes': all(row['all_planned_bytes_sent'] for row in matrix if row['id'].startswith('P-T') and row['id'] != 'P-T09'),
             'all_no_read_faults_have_zero_http_receive_calls': all(row['http_receive_calls'] == 0 for row in matrix if row['id'].startswith('P-T') and row['id'] != 'P-T09'),
             'all_recovery_decisions_precede_every_oracle': all(row['client_decision_before_every_oracle'] for row in matrix if row['id'].startswith('P-T') and row['id'] != 'P-T09'),
             'mutation_intent_count': len(mutations), 'ordinary_receipt_count': len(receipts),
             'fixture_count': len(state), 'known_pr_identities': sum(len(c['prs']) for c in state.values()),
             'additional_pr_identities_discovered_after_lost_create': [168],
             'total_observed_pr_identities': sum(len(c['prs']) for c in state.values()) + 1,
             'minimum_seconds_between_pr_create_dispatches': min(intervals),
             'cross_process_pacing_clock': 'UTC timestamps; process-relative monotonic values are compared only within each transport case',
             'audit_clock_correction': 'The first audit incorrectly pooled process-relative monotonic readings. Its result is preserved in evidence/evidence-audit-before-clock-fix.json; raw operation timestamps are unchanged.',
             'all_fixture_trunk_trees_workflow_free': all(c['workflow_files'] == '' for c in state.values()),
             'scope': 'No settings or main writes; native objects retained',
             'recorded_harness_violation': 'P-B02-register-99 blindly repeated the same logical create after P-B01-size-99 returned504. See boundary-driver-deviation.json. All deliberate TLS-cut identities were dispatched only once.'}
    save(HOME / 'matrix.json', matrix)
    save(HOME / 'evidence-audit.json', audit)
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    assess()
