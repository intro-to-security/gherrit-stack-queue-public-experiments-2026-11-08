import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
BARE=ROOT/'objects.git'
SOURCE=ROOT/'fixture.py'
ORIGINAL=ROOT/'source-inputs/fixture-a-fresh.py'
HELPER=ROOT.parents[2]/'control/rootlab.py'
SOURCE_SHA='769b6e0348898e142b983f17d37ef3b07aa5220bb0a110edb1b5d6b57c4c5549'
HELPER_SHA='ae1ae63d5ee8370cbca11711f5d5e76a97669881ddf8ef8911493666393d128d'
RUN=subprocess.run
CALLS=[]
ALLOWED={'init','config','remote','hash-object','mktree','commit-tree','update-ref','cat-file','rev-parse','diff','ls-tree','show','fsck'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_run(argv,*args,**kwargs):
    if not isinstance(argv,list) or not argv or argv[0]!='git':
        raise RuntimeError('Local preparation forbids non-Git process')
    commands=[x for x in argv[1:] if x in ALLOWED]
    if len(commands)!=1 or any(x in argv for x in ('push','fetch','ls-remote','clone','pull','send-pack','upload-pack')):
        raise RuntimeError('Local preparation forbids network/hosted/unknown command')
    command=commands[0]
    if command=='init':
        if argv!=['git','init','--bare',str(BARE)]:
            raise RuntimeError('Foreign init')
    elif '--git-dir' not in argv or argv[argv.index('--git-dir')+1]!=str(BARE):
        raise RuntimeError('Foreign Git store')
    result=RUN(argv,*args,**kwargs)
    CALLS.append(dict(argv=argv,exit=result.returncode))
    return result


def git(*args):
    p=guarded_run(['git','-c','core.hooksPath=/dev/null','--git-dir',str(BARE),*args],text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout


def main():
    assert sha(SOURCE)==SOURCE_SHA and sha(HELPER)==HELPER_SHA
    old=ORIGINAL.read_bytes();new=SOURCE.read_bytes()
    assert old.count(b'exh-1109-ui-stale-debug-a-fresh-')==2
    assert old.replace(b'exh-1109-ui-stale-debug-a-fresh-',b'exh-1109-ui-stale-debug-held-fresh-')==new
    assert not BARE.exists() and not (ROOT/'LOCAL-INPUTS.json').exists()
    subprocess.run=guarded_run
    spec=importlib.util.spec_from_file_location('held_fresh_fixture',SOURCE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):
        module.local()
    m=json.loads((ROOT/'LOCAL-INPUTS.json').read_bytes())
    assert m['prefix'].startswith('exh-1109-ui-stale-debug-held-fresh-')
    assert len(m['commits'])==9 and len(m['refs'])==7
    parents={'T0':None,'A0':'T0','B0':'A0','T1':'T0','A2':'A0','expected-A0':'T1','expected-B0':'expected-A0','expected-A2':'expected-A0','expected-B-over-A2':'expected-A2'}
    for name,oid in m['commits'].items():
        raw=git('cat-file','commit',oid)
        assert hashlib.sha1(f'commit {len(raw.encode())}\0'.encode()+raw.encode()).hexdigest()==oid
        assert raw.count("Agent-authored-by: AI agent acting on joshlf's behalf")==1
        assert 'author Josh Liebow-Feeser <hello@joshlf.com> ' in raw
        actual_parents=[line.split()[1] for line in raw.split('\n\n',1)[0].splitlines() if line.startswith('parent ')]
        assert actual_parents==([] if parents[name] is None else [m['commits'][parents[name]]])
        assert set(git('ls-tree','-r','--name-only',oid).splitlines())==set(m['trees'][name])
        for path,content in m['trees'][name].items():
            assert git('show',oid+':'+path)==content
    assert git('diff','--name-only',*m['ranges']['A-v1']).splitlines()==['a.txt']
    assert git('diff','--name-only',*m['ranges']['A-v2']).splitlines()==['a.txt','late-a-marker.txt']
    assert git('diff','--name-only',*m['ranges']['B-v1']).splitlines()==['b.txt']
    for name,tree in m['expected_result_trees'].items():
        assert git('rev-parse',m['commits'][name]+'^{tree}').strip()==tree
    assert git('diff','--binary','--full-index',*m['ranges']['A-v2'])==git('diff','--binary','--full-index',m['commits']['T1'],m['commits']['expected-A2'])
    assert git('diff','--binary','--full-index',*m['ranges']['B-v1'])==git('diff','--binary','--full-index',m['commits']['expected-A2'],m['commits']['expected-B-over-A2'])
    assert git('remote','get-url','origin').strip()=='https://github.com/'+m['repository']+'.git'
    assert git('config','--get','core.hooksPath').strip()=='/dev/null'
    fsck=git('fsck','--full','--no-dangling')
    assert not list((ROOT/'records').glob('*.intent.json'))
    assert not (ROOT/'prepare-START.json').exists() and not (ROOT/'READY.json').exists()
    expected={m['refs'][role]:m['commits'][obj] for role,obj in [('trunk','T1'),('A','A2'),('B','B0'),('source','B0'),('archiveA','A0'),('archiveB','B0'),('archiveA2','A2')]}
    result=dict(source_only_local=True,prefix=m['prefix'],source_sha256=sha(SOURCE),inputs_sha256=sha(ROOT/'LOCAL-INPUTS.json'),helper_sha256=sha(HELPER),
        literal_prefix_replacements_only=True,logical_commits=9,named_refs=7,commits_trees_contents_parents_and_trailers_verified=True,
        expected_trees_and_full_per_layer_patches_verified=True,hooks_disabled=True,fsck_exit=0,fsck_stdout=fsck,
        no_network_or_hosted_process=True,no_native_intents_or_READY=True,expected_preload_vector=expected,
        proposed_prepare_effects=['atomic six-ref create','create A PR','create B PR','register A/B','atomic A2+trunk advance and archive-A2 create'],
        no_advance_action=True,local_command_count=len(CALLS),commands=CALLS,local_stdout=capture.getvalue())
    with (ROOT/'LOCAL-VERIFICATION.json').open('x') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({key:value for key,value in result.items() if key not in ('commands','local_stdout')},indent=2))


if __name__=='__main__':
    main()
