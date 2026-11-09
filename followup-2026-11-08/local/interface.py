#!/usr/bin/env python3
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('followup', ROOT / 'followup.py')
f = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = f
spec.loader.exec_module(f)
core = f.core
RUN = ROOT / 'interface-runs' / str(time.time_ns())
RUN.mkdir(parents=True)
f.RUN = RUN
shutil.copyfile(Path(__file__), RUN / 'interface.py')
RESULTS = []


def case(case_id, label, action):
    f.case(case_id, label, action)


def hooks():
    observations = []
    for scenario in ['dry-run', 'unrelated', 'deletion']:
        directory, source, outer, p, a, b = f.new_sink('hook-' + scenario)
        inner = directory / 'inner.git'
        f.cmd(['git', 'init', '--bare', inner], directory, allowed=(0,))
        source.git('remote', 'rename', 'sink', 'outer')
        source.git('remote', 'add', 'inner', str(inner))
        source.git('update-ref', 'refs/heads/source', a)
        source.git('update-ref', 'refs/heads/unrelated', b)
        source.git('switch', 'source')
        hook = source.root / '.git' / 'hooks' / 'pre-push'
        hook.parent.mkdir(exist_ok=True)
        hook.write_text('''#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys
root = pathlib.Path(%r)
record = {'argv': sys.argv[1:], 'stdin': sys.stdin.read(), 'cwd': os.getcwd()}
command = ['git', '-c', 'core.hooksPath=/dev/null', 'push', '--no-verify', 'inner', 'refs/heads/source:refs/heads/inner-publication']
result = subprocess.run(command, text=True, capture_output=True)
record['inner_push'] = {'command': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
(root / 'hook.json').write_text(json.dumps(record, indent=2) + '\\n')
sys.exit(result.returncode)
''' % str(directory))
        hook.chmod(0o755)
        source.git('config', '--local', 'core.hooksPath', str(hook.parent))
        before = {'source': f.refs_at(source.root), 'inner': f.refs_at(inner), 'outer': f.refs_at(outer)}
        if scenario == 'dry-run':
            args = ['push', '--porcelain', '--dry-run', 'outer', 'refs/heads/source:refs/heads/outer-publication']
        elif scenario == 'unrelated':
            args = ['push', '--porcelain', 'outer', 'refs/heads/unrelated:refs/heads/unrelated-publication']
        else:
            args = ['push', '--porcelain', 'outer', ':refs/heads/head']
        f.dump(directory / 'intent.json', {'scenario': scenario, 'args': args, 'before': before})
        result = source.git(*args)
        after = {'source': f.refs_at(source.root), 'inner': f.refs_at(inner), 'outer': f.refs_at(outer)}
        f.checked('hook independently publishes source', after['inner'], {'refs/heads/inner-publication': a})
        if scenario == 'dry-run':
            f.checked('outer dry-run no ref change', after['outer'], before['outer'])
        elif scenario == 'unrelated':
            f.checked('outer destination gets unrelated source B', after['outer']['refs/heads/unrelated-publication'], b)
            f.checked('inner still publishes current source A', after['inner']['refs/heads/inner-publication'], a)
        else:
            f.checked('outer deletion happened', after['outer'], {})
        observation = {'scenario': scenario, 'args': args, 'before': before, 'after': after, 'hook': core.read_json(directory / 'hook.json'), 'hook_sha256': hashlib.sha256(hook.read_bytes()).hexdigest(), 'exit': result.returncode}
        f.dump(directory / 'evidence.json', observation)
        observations.append(observation)
    return {'new_controls': observations, 'prior_dry_run_input_equivalence': str(f.PRIOR / 'cli-history/hook-dryrun/RESULTS.json'), 'limit': 'Fixture hook semantics; current GHerrit source separately records that pre-push ignores destination/stdin in favor of current branch and gherrit.remote. No human error rates measured.'}


def explicit():
    directory, source, sink, p, a, b = f.new_sink('explicit-publication')
    unrelated = directory / 'unrelated.git'
    f.cmd(['git', 'init', '--bare', unrelated], directory, allowed=(0,))
    plan = {'source_commit': a, 'destination': str(sink), 'updates': {'refs/heads/head': a, 'refs/tags/archive': a}, 'expected': {'refs/heads/head': p, 'refs/tags/archive': ''}}
    f.dump(directory / 'plan.json', plan)
    commands = []
    def execute(plan, dry_run):
        if dry_run:
            return {'state': 'planned_no_dispatch', 'plan': plan}
        args = ['git', 'push', '--porcelain', '--no-verify', '--atomic']
        args += ['--force-with-lease=' + ref + ':' + plan['expected'][ref] for ref in plan['updates']]
        args += [plan['destination']] + [sha + ':' + ref for ref, sha in plan['updates'].items()]
        commands.append(args)
        return f.cmd(args, source.root, allowed=(0,))
    before = {'sink': f.refs_at(sink), 'unrelated': f.refs_at(unrelated)}
    preview = execute(plan, True)
    f.checked('explicit dry-run no dispatch', commands, [])
    f.checked('explicit dry-run all refs unchanged', {'sink': f.refs_at(sink), 'unrelated': f.refs_at(unrelated)}, before)
    source.git('update-ref', 'refs/heads/source', b)
    result = execute(plan, False)
    after = {'sink': f.refs_at(sink), 'unrelated': f.refs_at(unrelated)}
    f.checked('captured source remains planned A after live source moves B', after['sink'], {'refs/heads/head': a, 'refs/tags/archive': a})
    f.checked('unrelated destination untouched', after['unrelated'], {})
    evidence = {'plan': plan, 'preview': preview, 'commands': commands, 'before': before, 'after': after, 'exit': result.returncode, 'scope': 'Tiny explicit local publishing prototype demonstrates possible command contract; it does not establish production integration or usability.'}
    f.dump(directory / 'evidence.json', evidence)
    return evidence


URL_PATTERN = re.compile(r'https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)\Z')


def validate_adapter(urls, snapshots, repository, trunk, options, env):
    if not trunk or options or env.get('GH_STACK_NO_ATOMIC'):
        return 'reject-options-or-trunk'
    seen = set()
    expected_base = trunk
    if len(urls) < 2 or len(urls) != len(snapshots):
        return 'reject-arity'
    for url, pr in zip(urls, snapshots):
        match = URL_PATTERN.fullmatch(url)
        if not match or '/'.join(match.group(1, 2)) != repository:
            return 'reject-url-or-repository'
        number = int(match.group(3))
        if number in seen or number != pr['number']:
            return 'reject-identity'
        seen.add(number)
        if pr['state'] != 'open' or pr['merged'] or pr['auto_merge'] or pr['head_repository'] != repository:
            return 'reject-lifecycle-or-fork'
        if pr['base'] != expected_base:
            return 'reject-order-or-base'
        expected_base = pr['head']
    return 'eligible-for-live-recheck'


def adapter():
    binary = f.PRIOR / 'cli-history/bin/darwin-arm64'
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    expected = '70c0cb11346ad5d4f97a02a5cf5242052254d1775d356dc0759f035457873850'
    f.checked('pinned binary digest', digest, expected)
    commands = [(['--version'], (0,)), (['link', '--help'], (0,)), (['link'], (1,)), (['link', '--dry-run'], (1,))]
    parser = []
    env = dict(f.ENV, GH_TOKEN='', GITHUB_TOKEN='', GH_CONFIG_DIR=str(RUN / 'empty-gh-config'))
    for args, allowed in commands:
        result = f.cmd([binary] + args, RUN, allowed=allowed, env=env)
        parser.append({'args': args, 'exit': result.returncode, 'stdout': result.stdout.decode(), 'stderr': result.stderr.decode()})
    times = []
    for n in range(5):
        start = time.monotonic()
        f.cmd([binary, 'link', '--help'], RUN, allowed=(0,), env=env)
        times.append(time.monotonic() - start)
    repository = 'joshlf/gherrit-native-stack-experiments-2026-11-08'
    urls = ['https://github.com/' + repository + '/pull/' + str(n) for n in [101, 102]]
    snapshot = [{'number': 101, 'state': 'open', 'merged': False, 'auto_merge': False, 'head_repository': repository, 'base': 'main', 'head': 'A'}, {'number': 102, 'state': 'open', 'merged': False, 'auto_merge': False, 'head_repository': repository, 'base': 'A', 'head': 'B'}]
    variants = []
    def add(label, urls=urls, snapshots=snapshot, trunk='main', options=(), env={}, expected='eligible-for-live-recheck'):
        actual = validate_adapter(urls, snapshots, repository, trunk, options, env)
        f.checked(label, actual, expected)
        variants.append({'label': label, 'urls': urls, 'snapshots': snapshots, 'trunk': trunk, 'options': options, 'env': env, 'expected': expected, 'actual': actual})
    add('canonical adjacent eligible')
    add('numeric branch ambiguity', urls=['101', '102'], expected='reject-url-or-repository')
    add('host spoof', urls=[urls[0].replace('github.com', 'github.com.attacker.invalid'), urls[1]], expected='reject-url-or-repository')
    add('foreign repository', urls=[urls[0].replace('/joshlf/', '/other/'), urls[1]], expected='reject-url-or-repository')
    add('duplicate canonical identity', urls=[urls[0], urls[0]], expected='reject-identity')
    add('reverse order', urls=list(reversed(urls)), snapshots=list(reversed(snapshot)), expected='reject-order-or-base')
    changed = copy.deepcopy(snapshot); changed[1]['base'] = 'main'
    add('CLI would repair base', snapshots=changed, expected='reject-order-or-base')
    changed = copy.deepcopy(snapshot); changed[0]['merged'] = True; changed[0]['state'] = 'closed'
    add('merged review', snapshots=changed, expected='reject-lifecycle-or-fork')
    changed = copy.deepcopy(snapshot); changed[0]['auto_merge'] = True
    add('admitted auto-merge state', snapshots=changed, expected='reject-lifecycle-or-fork')
    changed = copy.deepcopy(snapshot); changed[0]['head_repository'] = 'other/fork'
    add('cross-fork', snapshots=changed, expected='reject-lifecycle-or-fork')
    add('implicit trunk', trunk='', expected='reject-options-or-trunk')
    add('open readiness mutation', options=['--open'], expected='reject-options-or-trunk')
    add('disable atomic option', options=['--no-atomic'], expected='reject-options-or-trunk')
    add('disable atomic environment', env={'GH_STACK_NO_ATOMIC': '1'}, expected='reject-options-or-trunk')
    add('URL query suffix', urls=[urls[0] + '?x=1', urls[1]], expected='reject-url-or-repository')
    source = f.WORKSPACE / 'outputs/github-native-stack-design-2026-11-08/platform/sources'
    target = RUN / 'retained-sources'
    target.mkdir()
    copied = []
    for relative in ['gh-stack/LICENSE', 'gh-stack/cmd/link.go', 'gh-stack/cmd/submit.go', 'gh-stack/cmd/push.go', 'gh-stack/internal/git/gitops.go', 'manifest.json']:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, destination)
        copied.append({'path': relative, 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()})
    gherrit = f.WORKSPACE / 'worktrees/rust-stable'
    gherrit_files = []
    for relative in ['src/lib.rs', 'src/pre_push/publication.rs']:
        destination = target / 'gherrit' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(gherrit / relative, destination)
        gherrit_files.append({'path': relative, 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()})
    revision = f.cmd(['git', 'rev-parse', 'HEAD'], gherrit, allowed=(0,)).stdout.decode().strip()
    result = {'binary_path': str(binary), 'sha256': digest, 'parser': parser, 'local_validation_cases': variants, 'help_wall_seconds': times, 'help_median_seconds': statistics.median(times), 'retained_sources': copied, 'gherrit_revision': revision, 'gherrit_sources': gherrit_files, 'retained_release_source_relationship': 'manifest.json says v0.3.0 release 2a49e675... differs from inspected bd0a3250... only by docs/package-lock.json; this run makes no new network/version-current claim.', 'scope': 'Pure validator plus pinned binary parser/help and retained implementation sources. Live checks must be repeated at dispatch and external writes reconciled. Cost excludes API, subprocess network, transport and human workflow cost.'}
    f.dump(RUN / 'adapter-evidence.json', result)
    return result


case('L23', 'Hook dry-run, destination and deletion controls', hooks)
case('L24', 'Explicit dry-run and captured destination prototype', explicit)
case('L25-L26', 'Pinned CLI parser, adapter validation and local cost', adapter)
result = {'run': str(RUN), 'rows': f.ROWS, 'passed': sum(r['status'] == 'passed' for r in f.ROWS), 'failed': sum(r['status'] == 'failed' for r in f.ROWS)}
f.dump(RUN / 'RESULTS.json', result)
f.dump(ROOT / 'latest-interface-run.json', {k: v for k, v in result.items() if k != 'rows'})
print(json.dumps({k: v for k, v in result.items() if k != 'rows'}))
sys.exit(bool(result['failed']))
