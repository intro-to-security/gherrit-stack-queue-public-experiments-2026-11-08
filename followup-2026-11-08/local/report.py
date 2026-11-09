#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
baseline = Path(read(ROOT / 'latest-run.json')['run'])
followup = Path(read(ROOT / 'latest-followup-run.json')['run'])
interface = Path(read(ROOT / 'latest-interface-run.json')['run'])
adversarial = Path(read(ROOT / 'latest-adversarial-run.json')['run'])
base_results = read(baseline / 'results.json')
follow_results = read(followup / 'RESULTS.json')
interface_results = read(interface / 'RESULTS.json')
adversarial_results = read(adversarial / 'RESULTS.json')

def evidence(run, group):
    return str((run / 'RESULTS.json').relative_to(ROOT)) + '#' + group

rows = []
def add(number, status, outcome, references, disposition='performed'):
    rows.append({'id': 'L%02d' % number, 'status': status, 'disposition': disposition, 'outcome': outcome, 'evidence': references})

bref = str((baseline / 'results.json').relative_to(ROOT))
add(1, 'passed', 'Unmodified original prototype: 122/122 assertions, including eight real SIGKILL prefixes.', [bref])
add(2, 'passed', 'Eighteen repeated changing-parent A/B integrations matched independent exact trees, messages and B ownership.', [evidence(followup, 'L02-L04')])
add(3, 'passed-negative-control', 'Authored-baseline reuse conflicts; accepted-local-as-hosted baseline loses pending content.', [bref + '#integration'])
add(4, 'passed', 'Three unchanged imports preserve exact tree; scratch commit identities may change.', [evidence(followup, 'L02-L04')])
add(5, 'passed-with-scope-limit', 'Two-commit local and hosted groups preserve net tree, upper ownership and local tip message; accepted layer is flattened.', [evidence(followup, 'L05-L08')])
add(6, 'passed', 'Rename with hosted edit, executable mode with hosted edit, deletion and binary local edit preserve exact modes/blob bytes.', [evidence(followup, 'L06-L07')])
add(7, 'passed-expected-conflicts', 'Rename/rename, modify/delete and binary/binary conflict explicitly with input objects and conflict trees pinned.', [evidence(followup, 'L06-L07')])
add(8, 'passed-with-scope-limit', 'Revert as new change and explicitly accepted reset retain intended trees and original objects; intent is supplied.', [bref + '#ordinary_git', evidence(followup, 'L05-L08')])
prior = ROOT.parent.parent / 'native-stacks-2026-11-08'
add(9, 'passed', 'F-before-B owns only pending API delta; B owns consumer. Prior executable hosted integration succeeds with F and fails specifically for missing field without F.', [bref + '#landed_followup', os.path.relpath(prior / 'local-git/hosted-integration/RESULTS.md', ROOT)], 'performed-and-reused-prior')
add(10, 'passed', 'Captured continuation preserves dirty/staged/untracked bytes, moving source and old checkpoint; occupied name refuses.', [bref + '#continuation'])
add(11, 'passed', 'Eight original SIGKILL states plus repeated recovery send no duplicate; indeterminate stays blocked.', [bref + '#fault_prefixes', evidence(followup, 'L11')])
add(12, 'passed-with-scope-limit', 'Missing bindings/checkpoint/pending manifest/op record withhold cooperative admission; full custody retains unknown guard and reconciles unique local receipt without resend.', [evidence(followup, 'L12')])
add(13, 'model-failure', 'Acknowledged wrong ref/checkpoint refuses, but complete-record recovery and admission accept a deleted continuation ref or checkpoint.', [evidence(followup, 'L13-L14')])
add(14, 'model-failure', 'Deleting applied operation record makes direct worker recreate planned intent and resend (1→2), bypassing separately correct admission refusal.', [evidence(followup, 'L13-L14')])
add(15, 'passed-with-scope-limit', 'Seven real SIGKILL journal replacement prefixes retain complete old/new JSON; no power-loss inference.', [evidence(followup, 'L15')])
add(16, 'model-failure', 'Simultaneous workers have no enforced owner fence and hit shared temporary-file or ref races; an earlier retained run also recorded duplicate dispatch.', [evidence(followup, 'L16'), 'followup-runs/1794194513334823000/RESULTS.json#L16'])
add(17, 'passed', 'Two divergent concurrent head/archive writers yield one coupled winner and no partial loser ref.', [evidence(followup, 'L17-L18')])
add(18, 'passed-negative-control', 'Same-target concurrent attempts can race; after the winner, identical stale-lease retry reports both refs up to date and succeeds.', [evidence(followup, 'L17-L18'), str((followup / 'commands.jsonl').relative_to(ROOT))])
add(19, 'passed', 'Stale head lease atomically rejects otherwise valid archive creation.', [evidence(followup, 'L19-L21')])
add(20, 'passed-negative-control', 'Stale lease on an unchanged equal head is omitted as a guard while a new archive is written.', [evidence(followup, 'L19-L21'), str((followup / 'git-equal-ref/packet.trace').relative_to(ROOT))])
add(21, 'passed-negative-control', 'Old→intervening→old ABA sequence permits old-value lease; no generation/ownership claim follows.', [evidence(followup, 'L19-L21')])
add(22, 'passed-with-scope-limit', 'Exact old/new ranges exclude parent drift; tip comparison includes it; range-diff identifies same patch and changed/unmatched patches.', [evidence(followup, 'L22')])
add(23, 'passed-negative-control', 'Outer dry-run, unrelated ref and deletion all allow fixture hook to publish current branch to its independent destination.', [evidence(interface, 'L23'), os.path.relpath(prior / 'cli-history/hook-dryrun/RESULTS.md', ROOT)], 'performed-and-reused-prior')
add(24, 'passed-with-scope-limit', 'Explicit local prototype dispatches nothing on dry-run and publishes exact captured SHA/destination after live source moves.', [evidence(interface, 'L24')])
add(25, 'passed-with-scope-limit', 'Pinned CLI digest and parser verified; 15 pure adapter inputs pass accept/reject oracles. Live authorization remains untested here.', [evidence(interface, 'L25-L26')])
add(26, 'passed-with-scope-limit', 'Five pinned link-help process timings and retained source comparison; prior hosted CLI effects reused. No API/transport latency estimate.', [evidence(interface, 'L25-L26'), os.path.relpath(prior / 'cli-history/RESULTS.md', ROOT)], 'performed-and-reused-prior')
add(27, 'unavailable', 'Machine/device power loss is outside this host/lane; production migration/signing and independent humans require implementations/actors; provider/real network-loss cases belong to root and other lanes.', [], 'concretely-unavailable')
add(28, 'model-failure', 'Two real processes cache planned; first completes; stale second then resumes: both exit 0, serialized emulator records two requests.', [evidence(adversarial, 'L28')])
add(29, 'model-failure', 'Custody admission permits a complete record whose operation ID disagrees with the pending manifest.', [evidence(adversarial, 'L29')])
add(30, 'passed-with-scope-limit', 'File-fsync failure leaves old JSON; directory-fsync failure raises after new JSON is visible. Exceptions do not imply no effect.', [evidence(adversarial, 'L30')])

sources = {}
for name in ['PLAN.md', 'baseline-harness.py', 'followup.py', 'interface.py', 'recovery_adversarial.py', 'verify_evidence.py', 'report.py', 'HARNESS-CORRECTIONS.md']:
    path = ROOT / name
    sources[name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
result = {'scope': 'Local disposable real-Git evidence and cooperative recovery prototype only. Expected negative-control execution success is distinct from the model invariant verdict.', 'baseline_run': str(baseline.relative_to(ROOT)), 'followup_run': str(followup.relative_to(ROOT)), 'interface_run': str(interface.relative_to(ROOT)), 'adversarial_run': str(adversarial.relative_to(ROOT)), 'baseline_assertions': {'passed': base_results['passed_count'], 'total': base_results['check_count']}, 'new_probe_groups': {'executed': len(follow_results['rows']) + len(interface_results['rows']) + len(adversarial_results['rows']), 'driver_failures_final': follow_results['failed'] + interface_results['failed'] + adversarial_results['failed'], 'preserved_first_run_driver_failures': 2}, 'model_failure_case_ids': [row['id'] for row in rows if row['status'] == 'model-failure'], 'matrix': rows, 'sources': sources, 'object_verification': read(ROOT / 'OBJECT-VERIFICATION.json'), 'no_network_effects': True, 'no_production_changes': True}
(ROOT / 'RESULTS.json').write_text(json.dumps(result, indent=2) + '\n')
table = '| Case | Disposition | Observation |\n| --- | --- | --- |\n' + '\n'.join('| ' + row['id'] + ' | ' + row['status'] + ' | ' + row['outcome'].replace('|', '\\|') + ' |' for row in rows) + '\n'
(ROOT / 'CASE-MATRIX.md').write_text('# Local case dispositions\n\nEvery planned ID has a terminal disposition. `model-failure` identifies an observed prototype invariant gap even when the negative probe itself ran as expected. Detailed artifact paths are in `RESULTS.json`.\n\n' + table + '\n*Authored by an AI agent acting on joshlf\'s behalf.*\n')
print(json.dumps({'planned_ids': len(rows), 'model_failure_ids': result['model_failure_case_ids'], 'new_probe_groups': result['new_probe_groups'], 'object_stores': result['object_verification']['repository_count']}))
