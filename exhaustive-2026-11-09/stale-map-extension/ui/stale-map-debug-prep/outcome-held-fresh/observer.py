import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import sys

SOURCE_ROOT=Path(__file__).resolve().parent
ROOT=SOURCE_ROOT/'capture-001'
FIXTURE=SOURCE_ROOT.parent/'fixture-held-fresh-prep'
REPO='joshlf/gherrit-native-stack-experiments-2026-11-08'
PREFIX='exh-1109-ui-stale-debug-held-fresh-0a10ffe99c'
URL='https://github.com/'+REPO+'.git'
STORE=ROOT/'objects.git'
ENV={key:value for key,value in os.environ.items() if not key.startswith('GIT_')}
ENV.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_TERMINAL_PROMPT='0',LC_ALL='C')
COMMANDS=[]


def stamp():
    return dict(utc=datetime.now(timezone.utc).isoformat(),monotonic_ns=time.monotonic_ns())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path,value):
    data=(json.dumps(value,indent=2)+'\n').encode()
    with path.open('xb') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())


def call(label,argv,allowed=(0,)):
    started=stamp()
    result=subprocess.run(argv,cwd=ROOT,env=ENV,capture_output=True,timeout=45)
    ended=stamp()
    for suffix,body in [('stdout',result.stdout),('stderr',result.stderr)]:
        with (ROOT/(label+'.'+suffix)).open('xb') as stream:
            stream.write(body)
    record=dict(label=label,argv=argv,started=started,ended=ended,exit=result.returncode,
                stdout_sha256=digest(result.stdout),stderr_sha256=digest(result.stderr))
    save(ROOT/(label+'.command.json'),record)
    if result.returncode not in allowed:
        raise RuntimeError(label+': unexpected exit '+str(result.returncode))
    return result.stdout


def git(label,*args):
    return call(label,['git','-c','core.hooksPath=/dev/null','-c','core.pager=cat',
        '-c','gc.auto=0','-c','maintenance.auto=false','--git-dir='+str(STORE),*args])


def api(label,path):
    return json.loads(call(label,['gh','api','--method','GET','-H','Accept: application/vnd.github+json',
        '-H','X-GitHub-Api-Version: 2026-03-10','-H','Cache-Control: no-cache',path]))


def refs(label,names):
    data=git(label,'ls-remote','--refs',URL,*['refs/heads/'+name for name in names])
    return {line.split()[1].removeprefix('refs/heads/'):line.split()[0] for line in data.decode().splitlines()}


def patch(label, base, head):
    return git(label,'diff','--no-ext-diff','--no-textconv','--binary','--full-index',base,head,'--').decode()


def commit_record(label, oid):
    raw=git(label+'-raw','cat-file','commit',oid).decode()
    headers,message=raw.split('\n\n',1)
    lines=headers.splitlines()
    return dict(raw_commit=raw,tree=lines[0].split()[1],
        parents=[line.split()[1] for line in lines if line.startswith('parent ')],
        author=next(line[7:] for line in lines if line.startswith('author ')),
        committer=next(line[10:] for line in lines if line.startswith('committer ')),
        has_gpgsig=any(line.startswith('gpgsig ') for line in lines),
        agent_trailers=[line for line in message.splitlines() if line.startswith('Agent-authored-by:')],
        message=message,tree_entries=git(label+'-tree','ls-tree','-r',oid).decode())


def main():
    ROOT.mkdir(exist_ok=False)
    inputs={name:(FIXTURE/name).read_bytes() for name in ('READY.json','LOCAL-INPUTS.json','fixture.py')}
    network_path=SOURCE_ROOT.parent/'NETWORK-HELD-FRESH.json'
    inputs['NETWORK-HELD-FRESH.json']=network_path.read_bytes()
    ready=json.loads(inputs['READY.json']);network=json.loads(inputs['NETWORK-HELD-FRESH.json'])
    assert ready['repository']==REPO and ready['prefix']==PREFIX
    assert ready['prs']==dict(A=670,B=671) and ready['stack']['number']==672
    assert network['selected_entries'][0]['request_body']['expectedHeadOids']=={'670':ready['commits']['A2'],'671':ready['commits']['B0']}
    assert network['selected_entries'][0]['status']==200
    fixed={name:oid for name,oid in ready['current_refs'].items() if name not in (ready['refs']['A'],ready['refs']['B'])}
    assert len(fixed)==5 and len(ready['current_refs'])==7
    pins={name:dict(bytes=len(body),sha256=digest(body)) for name,body in inputs.items()}
    pins['observer.py']=dict(bytes=Path(__file__).stat().st_size,sha256=digest(Path(__file__).read_bytes()))
    save(ROOT/'INPUT-PINS.json',pins)
    save(ROOT/'START.json',dict(at=stamp(),repository=REPO,prefix=PREFIX,prs=ready['prs'],stack=672,
        fixed_refs=fixed,scope='GETs and exact seven-ref fetches into new owned bare store; no remote mutation/private HAR/browser action'))
    git('init','init','--bare','--template=',str(STORE))
    versions=dict(git=call('git-version',['git','--version']).decode().strip(),
        gh=call('gh-version',['gh','--version']).decode().splitlines()[0],python=sys.version)
    start=time.monotonic();rows=[]
    for index,offset in enumerate((0,10,30)):
        delay=start+offset-time.monotonic()
        if delay>0:time.sleep(delay)
        label='cohort-'+str(index);began=stamp()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            frefs=pool.submit(refs,label+'-refs',list(ready['current_refs']))
            fa=pool.submit(api,label+'-pr-A','repos/'+REPO+'/pulls/670')
            fb=pool.submit(api,label+'-pr-B','repos/'+REPO+'/pulls/671')
            fs=pool.submit(api,label+'-stack','repos/'+REPO+'/stacks/672')
            actual,pa,pb,group=frefs.result(),fa.result(),fb.result(),fs.result()
        assert pa['number']==670 and pb['number']==671 and group['number']==672
        assert pa['node_id']==ready['nodes']['A'] and pb['node_id']==ready['nodes']['B'] and group['node_id']==ready['stack']['node_id']
        local={name:'refs/observed/held-fresh-'+str(index)+'/'+name for name in ready['current_refs']}
        git(label+'-fetch','fetch','--no-tags','--no-write-fetch-head',URL,
            *['refs/heads/'+name+':'+local[name] for name in local])
        fetched={name:git(label+'-resolve-'+str(n),'rev-parse','--verify',ref).decode().strip() for n,(name,ref) in enumerate(local.items())}
        a,b,t=(fetched[ready['refs'][role]] for role in ('A','B','trunk'))
        arange=git(label+'-A-full-range','rev-list','--reverse',t+'..'+a).decode().splitlines()
        brange=git(label+'-B-full-range','rev-list','--reverse',a+'..'+b).decode().splitlines()
        object_ids=list(dict.fromkeys([*fetched.values(),*arange,*brange]))
        objects={oid:commit_record(label+'-object-'+str(n),oid) for n,oid in enumerate(object_ids)}
        source_A=patch(label+'-source-A-full',*ready['ranges']['A-v2'])
        source_B=patch(label+'-source-B-full',*ready['ranges']['B-v1'])
        actual_A=patch(label+'-actual-A-full',t,a);actual_B=patch(label+'-actual-B-full',a,b)
        markers={role:call(label+'-marker-'+role,['git','-c','core.hooksPath=/dev/null','--git-dir='+str(STORE),'show',head+':late-a-marker.txt'],allowed=(0,128)).decode(errors='replace') for role,head in [('A',a),('B',b)]}
        marker=ready['trees']['A2']['late-a-marker.txt']
        checks=dict(seven_ref_names=set(actual)==set(ready['current_refs']),actual_equals_fetched=actual==fetched,
            five_protected_refs_exact=all(actual.get(name)==oid for name,oid in fixed.items()),
            A_changed_from_A2=a!=ready['commits']['A2'],B_changed_from_B0=b!=ready['commits']['B0'],
            canonical_open_order=group['open'] and [q['number'] for q in group['pull_requests']]==[670,671] and all(q['state']=='open' and not q['merged'] for q in (pa,pb)),
            PR_names_heads_exact=all(q['head']['ref']==ready['refs'][role] and q['head']['sha']==actual[ready['refs'][role]] and q['base']['ref']==ready['refs'][parent] for role,parent,q in [('A','trunk',pa),('B','A',pb)]),
            A_full_two_commits=len(arange)==2,B_full_one_commit=len(brange)==1,
            A_first_parent_T1=bool(arange) and objects[arange[0]]['parents']==[t],
            A_tip_parent_first=len(arange)==2 and objects[a]['parents']==[arange[0]],
            B_sole_parent_actual_A=objects[b]['parents']==[a],
            A_expected_tree=objects[a]['tree']==ready['expected_result_trees']['expected-A2'],
            B_expected_tree=objects[b]['tree']==ready['expected_result_trees']['expected-B-over-A2'],
            A_full_patch_exact=actual_A==source_A,B_full_patch_exact=actual_B==source_B,
            marker_survives_both=all(value==marker for value in markers.values()))
        row=dict(index=index,requested_offset_seconds=offset,started=began,ended=stamp(),actual_refs=actual,fetched_refs=fetched,
            fixed_refs=fixed,REST_PRs=dict(A=pa,B=pb),native_group=group,objects=objects,
            source_ranges=dict(A=ready['ranges']['A-v2'],B=ready['ranges']['B-v1']),actual_ranges=dict(A=[t,a],B=[a,b]),
            A_rewritten_commits=arange,B_rewritten_commits=brange,
            source_A_full_patch=source_A,actual_A_full_patch=actual_A,source_B_full_patch=source_B,actual_B_full_patch=actual_B,
            markers=markers,checks=checks,all_checks=all(checks.values()),
            projection_disagreements={role:dict(REST_head=q['head']['sha'],actual_head=actual[ready['refs'][role]],REST_base=q['base']['sha'],actual_named_base=actual.get(q['base']['ref']),base_name=q['base']['ref']) for role,q in [('A',pa),('B',pb)] if q['head']['sha']!=actual[ready['refs'][role]] or q['base']['sha']!=actual.get(q['base']['ref'])})
        save(ROOT/(label+'.json'),row);rows.append(row)
        print(json.dumps(dict(cohort=index,at=row['ended']['utc'],all_checks=row['all_checks'],A=a,B=b,checks=checks)),flush=True)
    git('fsck','fsck','--full','--no-dangling')
    save(ROOT/'RESULTS.json',dict(repository=REPO,prefix=PREFIX,prs=ready['prs'],stack=672,versions=versions,
        observations=rows,all_checks=all(r['all_checks'] for r in rows),
        scope='Fresh-map website outcome; actual graph independently read. No private HAR or job-status replay; no remote write, public-interface promise or future-write-fence claim.',
        producer_limit='Raw commit author/committer/message/gpgsig presence retained. Presence is not signature cryptographic verification or proof of internal producer implementation.'))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if ROOT.exists() and not (ROOT/'FAILED.json').exists():
            save(ROOT/'FAILED.json',dict(at=stamp(),error=repr(error),scope='Read-only observer stopped; retained reads are not a passing result; no remote writes to retry'))
        raise
