"""Read exact owned PR/ref/event state and compare each original patch."""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'control'))
from rootlab import Lab, preserve

QUERY = '''query($a:Int!,$b:Int!){repository(owner:"joshlf",name:"gherrit-native-stack-experiments-2026-11-08") {
 a:pullRequest(number:$a){number headRefOid baseRefOid baseRefName timelineItems(first:100){nodes{__typename
 ... on HeadRefForcePushedEvent{id createdAt beforeCommit{oid} afterCommit{oid} actor{login}}
 ... on AutomaticBaseChangeSucceededEvent{id createdAt oldBase newBase}}}}
 b:pullRequest(number:$b){number headRefOid baseRefOid baseRefName timelineItems(first:100){nodes{__typename
 ... on HeadRefForcePushedEvent{id createdAt beforeCommit{oid} afterCommit{oid} actor{login}}
 ... on AutomaticBaseChangeSucceededEvent{id createdAt oldBase newBase}}}}}}'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('key', choices=['clean-rebase', 'conflict-a', 'conflict-b', 'stale-vector'])
    parser.add_argument('label')
    args = parser.parse_args()
    lab = Lab(HERE, 'exh-1109-ui')
    case = json.loads((HERE / ('READY-' + args.key + '.json')).read_text())
    label = args.key + '-' + args.label
    prs = {k: lab.api(label + '-read-' + k.lower(), '/pulls/' + str(n)) for k, n in case['prs'].items()}
    for k, value in prs.items():
        assert value['head']['ref'] == case['refs'][k]
        assert value['head']['repo']['full_name'] == lab.repo
    fetch = ['git', '-c', 'core.hooksPath=/dev/null', '--git-dir', str(lab.bare), 'fetch', '--no-tags', 'origin']
    for branch in case['refs'].values():
        ref = lab.refname(branch)
        fetch.append('+' + ref + ':refs/observed/' + branch)
    lab.command(label + '-fetch', fetch)
    out = {'prs': prs, 'git': {}}
    for k in ['A', 'B']:
        new = lab.git('rev-parse', 'refs/observed/' + case['refs'][k])
        old = case['commits'][k]
        before = lab.git('diff', old + '^', old)
        after = lab.git('diff', new + '^', new)
        out['git'][k] = {'head': new, 'parents': lab.git('show', '-s', '--format=%P', new),
                         'tree': lab.git('show', '-s', '--format=%T', new),
                         'original_patch': before, 'current_patch': after, 'patch_equal': before == after,
                         'raw_commit': lab.git('cat-file', 'commit', new)}
    data = json.dumps({'query': QUERY, 'variables': {'a':case['prs']['A'], 'b':case['prs']['B']}})
    receipt = lab.command(label + '-timeline', ['gh','api','graphql','--input','-'], data)
    out['events'] = json.loads(receipt['stdout'])
    preserve(HERE / (label + '-outcome.json'), out)
    print(json.dumps({'key':args.key, 'prs':case['prs'], 'git':{k:{a:v for a,v in o.items() if a not in ['raw_commit','original_patch','current_patch']} for k,o in out['git'].items()}}))


if __name__ == '__main__':
    main()
