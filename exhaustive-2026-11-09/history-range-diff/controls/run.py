import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
REPO = ROOT/'repo.git'
OUT = ROOT/'evidence'
ENV = {key:value for key,value in os.environ.items() if not key.startswith('GIT_')}
ENV.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', GIT_TERMINAL_PROMPT='0',
           GIT_AUTHOR_NAME='Josh Liebow-Feeser', GIT_AUTHOR_EMAIL='hello@joshlf.com',
           GIT_COMMITTER_NAME='Josh Liebow-Feeser', GIT_COMMITTER_EMAIL='hello@joshlf.com',
           GIT_AUTHOR_DATE='2026-11-09T12:00:00+00:00', GIT_COMMITTER_DATE='2026-11-09T12:00:00+00:00',
           LC_ALL='C')
COMMANDS, BLOBS, COMMITS = [], {}, []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args, data=None, cwd=REPO):
    argv = ['git','-c','core.hooksPath=/dev/null','-c','core.pager=cat','-c','commit.gpgsign=false',*args]
    result = subprocess.run(argv,cwd=cwd,input=data,capture_output=True,env=ENV)
    identity = f'{len(COMMANDS)+1:03}'
    for suffix, body in (('stdout',result.stdout),('stderr',result.stderr)):
        (OUT/(identity+'.'+suffix)).write_bytes(body)
    if data is not None:
        (OUT/(identity+'.stdin')).write_bytes(data)
    COMMANDS.append(dict(id=identity,argv=argv,cwd=str(cwd),exit=result.returncode,
                         stdin_sha256=None if data is None else sha(data),stdout_sha256=sha(result.stdout),stderr_sha256=sha(result.stderr)))
    if result.returncode:
        raise RuntimeError(json.dumps(COMMANDS[-1])+':'+result.stderr.decode(errors='replace'))
    return result.stdout


def blob(data):
    if data not in BLOBS:
        BLOBS[data] = git('hash-object','-w','--stdin',data=data).decode().strip()
    return BLOBS[data]


def commit(name, subject, files, parent=None):
    entries = b''.join(f'{mode} blob {blob(data)}\t{path}\n'.encode() for path,(mode,data) in sorted(files.items()))
    tree = git('mktree',data=entries).decode().strip()
    message = subject+"\n\nAgent-authored-by: AI agent acting on joshlf's behalf\n"
    args = ['commit-tree',tree] + ([] if parent is None else ['-p',parent])
    oid = git(*args,data=message.encode()).decode().strip()
    git('update-ref','refs/controls/'+name,oid,'0'*40)
    COMMITS.append(dict(name=name,subject=subject,commit=oid,tree=tree,parent=parent,
        files={path:dict(mode=mode,blob=BLOBS[data],bytes=len(data),sha256=sha(data),hex=data.hex()) for path,(mode,data) in files.items()}))
    return oid


def alter(files, **changes):
    return dict(files,**changes)


def compare(name, old_base, old_tip, new_base, new_tip, purpose):
    folder = OUT/name
    folder.mkdir()
    outputs = {}
    for label, extra in (('default',[]),('factor100',['--creation-factor=100'])):
        data = git('range-diff','--no-color','--no-ext-diff','--no-textconv',*extra,old_base+'..'+old_tip,new_base+'..'+new_tip)
        (folder/(label+'.range-diff.txt')).write_bytes(data)
        outputs[label] = data.decode()
    patches = []
    for label, base, tip in (('old',old_base,old_tip),('new',new_base,new_tip)):
        patch = git('diff','--no-color','--no-ext-diff','--no-textconv','--full-index',base,tip,'--')
        (folder/(label+'.patch')).write_bytes(patch)
        (folder/(label+'.binary.patch')).write_bytes(git('diff','--no-color','--no-ext-diff','--no-textconv','--full-index','--binary',base,tip,'--'))
        (folder/(label+'.raw.txt')).write_bytes(git('diff','--raw','--no-abbrev',base,tip,'--'))
        patches.append(patch.decode())
    literal = ''.join(difflib.unified_diff(patches[0].splitlines(True),patches[1].splitlines(True),fromfile='old.patch',tofile='new.patch'))
    (folder/'literal-diff-of-patches.diff').write_text(literal)
    return dict(id=name,purpose=purpose,old=dict(base=old_base,tip=old_tip),new=dict(base=new_base,tip=new_tip),
                range_diff=outputs,literal_diff_of_patches=literal)


def main():
    if REPO.exists() or OUT.exists() or (ROOT/'RESULTS.json').exists():
        raise RuntimeError('fresh_control_outputs_required; preserve prior observations')
    OUT.mkdir()
    version = git('--version',cwd=ROOT).decode().strip()
    git('init','--bare','--template=',str(REPO),cwd=ROOT)
    base_files = {'unrelated.txt':('100644',b'trunk = 0\n'),
        'context.txt':('100644',b'context = old\nvalue = 0\nfooter\n'),
        'data.bin':('100644',b'\x00base\xff\n'),
        'script.sh':('100644',b'#!/bin/sh\necho base\n'),
        'alpha.txt':('100644',b'alpha = 0\n'),'beta.txt':('100644',b'beta = 0\n')}
    base = commit('base','Create local comparison baseline',base_files)
    drift_files = alter(base_files,**{'unrelated.txt':('100644',b'trunk = 1\n')})
    drift = commit('unrelated-base','Advance unrelated base file',drift_files,base)
    alpha = {'alpha.txt':('100644',b'alpha = 1\n')}
    old_alpha = commit('old-alpha','Update alpha',alter(base_files,**alpha),base)
    new_alpha = commit('new-alpha','Update alpha',alter(drift_files,**alpha),drift)
    rows = [compare('A-unrelated-base',base,old_alpha,drift,new_alpha,'Identical alpha edit across unrelated-file ancestry drift')]
    context_old = commit('context-old','Update value',alter(base_files,**{'context.txt':('100644',b'context = old\nvalue = 1\nfooter\n')}),base)
    context_files = alter(base_files,**{'context.txt':('100644',b'context = new\nvalue = 0\nfooter\n')})
    context_base = commit('context-base','Advance adjacent context',context_files,base)
    context_new = commit('context-new','Update value',alter(context_files,**{'context.txt':('100644',b'context = new\nvalue = 1\nfooter\n')}),context_base)
    rows.append(compare('B-context-drift',base,context_old,context_base,context_new,'Same value 0-to-1 authored edit; base changes adjacent context only'))
    binary_old = commit('binary-old','Replace binary payload',alter(base_files,**{'data.bin':('100644',b'\x00revision-one\xff\n')}),base)
    binary_new = commit('binary-new','Replace binary payload',alter(base_files,**{'data.bin':('100644',b'\x00revision-two\xfe\n')}),base)
    rows.append(compare('C-binary-change',base,binary_old,base,binary_new,'Different binary replacement bytes with identical metadata and paths'))
    script = b'#!/bin/sh\necho authored\n'
    mode_old = commit('mode-old','Update script',alter(base_files,**{'script.sh':('100755',script)}),base)
    mode_new = commit('mode-new','Update script',alter(base_files,**{'script.sh':('100644',script)}),base)
    rows.append(compare('D-mode-change',base,mode_old,base,mode_new,'Same authored text; executable mode omitted in second revision'))
    beta = {'beta.txt':('100644',b'beta = 1\n')}
    series_old = commit('series-old','Update beta',alter(base_files,**alpha,**beta),old_alpha)
    series_first = commit('series-new-first','Update beta',alter(drift_files,**beta),drift)
    series_new = commit('series-new','Update alpha',alter(drift_files,**alpha,**beta),series_first)
    rows.append(compare('E-series-reorder',base,series_old,drift,series_new,'Same two disjoint edits in reversed order across unrelated base drift'))
    git('fsck','--full','--no-dangling')
    git('for-each-ref','--format=%(refname) %(objectname)')
    record = dict(git_version=version,cases=rows,commits=COMMITS,command_count=len(COMMANDS),commit_count=len(COMMITS),
        environment=ENV,limits='One fresh local bare repo; explicit synthetic intent; no hosted effects or semantic equivalence oracle')
    record['environment'] = {key:value for key,value in ENV.items() if key.startswith('GIT_') or key == 'LC_ALL'}
    (ROOT/'COMMANDS.json').write_text(json.dumps(COMMANDS,indent=2)+'\n')
    (ROOT/'RESULTS.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(git_version=version,commits=len(COMMITS),commands=len(COMMANDS),outputs={row['id']:row['range_diff'] for row in rows}),indent=2))


if __name__ == '__main__':
    main()
