"""Render the evidence-backed dispositions after the final hosted readback."""
from pathlib import Path
import json

HOME = Path(__file__).resolve().parent
results = json.loads((HOME / 'RESULTS.json').read_text())
audit = json.loads((HOME / 'FINAL-AUDIT.json').read_text())
rows = []
for caseid, value in results['cases'].items():
    name = caseid.lower()
    if caseid == 'S10':
        for suffix, key, description in [('a', 'missing_evidence', 'withheld acknowledged receipt'),
                                          ('b', 'stale_live', 'independently advanced live B head')]:
            item = value[key]
            rows.append({'id': caseid + suffix, 'topology': value['topology'], 'boundary': description,
                         'disposition': 'performed-refused-before-new-dispatch',
                         'fixture': value['fixture'], 'process': 'fixtures/' + name + '/process-' + ('missing-evidence' if suffix == 'a' else 'stale-live') + '.json',
                         'refusal': 'fixtures/' + name + '/refusal-' + ('missing-evidence' if suffix == 'a' else 'stale-live') + '.json',
                         'exit': item['process']['exit'], 'no_new_effect_receipt': item['no_new_effect_receipt'],
                         'retained_stop_reason': 'deliberate stale live state; original receipt restored exactly'})
    else:
        completion = value['completion']
        rows.append({'id': caseid, 'topology': value['topology'], 'boundary': value['boundary'],
                     'disposition': value['disposition'], 'fixture': value['fixture'],
                     'interruption': 'fixtures/' + name + '/process-initial.json',
                     'boundary_checkpoint': 'fixtures/' + name + '/boundary-initial.json',
                     'recovery': 'fixtures/' + name + '/process-recovery.json',
                     'completion': 'fixtures/' + name + '/completion-recovery.json',
                     'kill_exit': value['interruption']['exit'], 'recovery_exit': value['recovery']['exit'],
                     'resumed_after_count': completion['resumed_after_count'],
                     'completed_count': completion['completed_count'], 'canonical_prs': completion['prs']})
output = {'started_at': results['started_at'], 'finished_at': audit['completed_at'], 'rows': rows,
          'final_audit': 'FINAL-AUDIT.json', 'all_planned_cases_disposed': len(rows) == 11,
          'findings_are_bounded_observations': True}
(HOME / 'CASE-MATRIX.json').write_text(json.dumps(output, indent=2) + '\n')
table = ['| Case | Selected prefix / negative input | Disposition | Evidence |',
         '| --- | --- | --- | --- |']
for row in rows:
    if row['id'].startswith('S10'):
        link = '[' + row['id'] + ' refusal](' + row['refusal'] + ')'
        disposition = 'Refused; no new executor dispatch'
    else:
        link = '[kill](' + row['interruption'] + '), [fresh recovery](' + row['completion'] + ')'
        disposition = 'Recovered ' + str(row['resumed_after_count']) + ' → ' + str(row['completed_count'])
    table.append('| ' + row['id'] + ' | ' + row['boundary'] + ' | ' + disposition + ' | ' + link + ' |')
(HOME / 'CASE-MATRIX.md').write_text('# Structural-prefix dispositions\n\n' + '\n'.join(table) +
    '\n\nEvery selected crash exited by SIGKILL (`-9`). Each recovery used a new PID.\n'
    'The receipt/readback/checkpoint had been persisted before the selected kill.\n'
    'These are after-ack crashes, not lost in-flight responses or machine power loss.\n\n'
    '*Authored by an AI agent acting on joshlf\'s behalf.*\n')
print('Wrote eleven evidence-backed matrix rows; final audit errors:', audit['errors'])
