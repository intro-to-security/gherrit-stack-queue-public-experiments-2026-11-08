import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

SOURCE_ROOT=Path(__file__).resolve().parent
ROOT=SOURCE_ROOT/'capture-001'
FIXTURE=SOURCE_ROOT.parent/'fixture-a-prep'
REPO='joshlf/gherrit-native-stack-experiments-2026-11-08'
PREFIX='exh-1109-ui-stale-debug-a-5949ea0a29'
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


def main():
    ROOT.mkdir(exist_ok=False)
    if STORE.exists() or (ROOT/'RESULTS.json').exists() or (ROOT/'START.json').exists():
        raise RuntimeError('Fresh observer allocation required; do not replay or overwrite')
    inputs={name:(FIXTURE/name).read_bytes() for name in ('READY.json','READY-A-ARCHIVED.json','A-ADVANCED.json')}
    ready=json.loads(inputs['READY-A-ARCHIVED.json']);advanced=json.loads(inputs['A-ADVANCED.json'])
    assert ready['original_ready_sha256']==digest(inputs['READY.json'])
    assert ready['repository']==REPO and ready['prefix']==PREFIX
    assert ready['prs']==dict(A=664,B=665) and ready['stack']['number']==666
    expected=advanced['current_refs']
    assert len(expected)==7 and all(name.startswith(PREFIX+'-') for name in expected)
    assert advanced['before']==ready['commits']['A0'] and advanced['after']==ready['commits']['A2']
    assert advanced['range']==ready['ranges']['A-v2']
    assert set(expected)==set(ready['current_refs'])
    assert [name for name in expected if expected[name]!=ready['current_refs'][name]]==[ready['refs']['A']]
    assert advanced['selected_B_unchanged']==expected[ready['refs']['B']]==ready['commits']['B0']
    assert ready['current_refs'][ready['refs']['archiveA2']]==ready['commits']['A2']
    save(ROOT/'INPUT-PINS.json',{name:dict(bytes=len(body),sha256=digest(body)) for name,body in inputs.items()})
    save(ROOT/'START.json',dict(at=stamp(),repository=REPO,prefix=PREFIX,prs=ready['prs'],stack=666,
        expected_refs=expected,scope='GETs, exact owned-ref fetches into new independent bare store; no remote writes/native initiation'))
    git('init','init','--bare','--template=',str(STORE))
    start=time.monotonic()
    rows=[]
    for index,offset in enumerate((0,10,30)):
        delay=start+offset-time.monotonic()
        if delay>0:time.sleep(delay)
        label='cohort-'+str(index)
        began=stamp()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            frefs=pool.submit(refs,label+'-refs',list(expected))
            fa=pool.submit(api,label+'-pr-A','repos/'+REPO+'/pulls/664')
            fb=pool.submit(api,label+'-pr-B','repos/'+REPO+'/pulls/665')
            fs=pool.submit(api,label+'-stack','repos/'+REPO+'/stacks/666')
            actual,pa,pb,group=frefs.result(),fa.result(),fb.result(),fs.result()
        assert pa['number']==664 and pb['number']==665 and group['number']==666
        assert pa['node_id']==ready['nodes']['A'] and pb['node_id']==ready['nodes']['B']
        assert group['node_id']==ready['stack']['node_id']
        local={name:'refs/observed/outcome-a-'+str(index)+'/'+name for name in expected}
        git(label+'-fetch','fetch','--no-tags','--no-write-fetch-head',URL,
            *['refs/heads/'+name+':'+local[name] for name in expected])
        fetched={name:git(label+'-resolve-'+str(n),'rev-parse','--verify',ref).decode().strip() for n,(name,ref) in enumerate(local.items())}
        objects={}
        for n,oid in enumerate(dict.fromkeys(fetched.values())):
            raw=git(label+'-object-'+str(n),'cat-file','commit',oid).decode()
            tree=raw.splitlines()[0].split()[1]
            parents=[line.split()[1] for line in raw.split('\n\n',1)[0].splitlines() if line.startswith('parent ')]
            entries=git(label+'-tree-'+str(n),'ls-tree','-r',oid).decode()
            objects[oid]=dict(raw_commit=raw,tree=tree,parents=parents,tree_entries=entries)
        t0,a2=advanced['range']
        own=git(label+'-retained-A-v2-own-range','diff','--no-ext-diff','--no-textconv','--binary','--full-index',t0,a2,'--').decode()
        old_b_patch=git(label+'-retained-B-v1-own-range','diff','--no-ext-diff','--no-textconv','--binary','--full-index',*ready['ranges']['B-v1'],'--').decode()
        old_a_patch=git(label+'-retained-A-v1-own-range','diff','--no-ext-diff','--no-textconv','--binary','--full-index',*ready['ranges']['A-v1'],'--').decode()
        marker_delta=git(label+'-retained-A-v2-marker-delta','diff','--no-ext-diff','--no-textconv','--binary','--full-index',advanced['before'],a2,'--').decode()
        a_head=fetched[ready['refs']['A']]
        marker_proc=call(label+'-current-A-marker',['git','-c','core.hooksPath=/dev/null','--git-dir='+str(STORE),
            'show',a_head+':late-a-marker.txt'],allowed=(0,128))
        row=dict(index=index,requested_offset_seconds=offset,started=began,ended=stamp(),
            elapsed_from_observer_start_seconds=time.monotonic()-start,actual_refs=actual,fetched_refs=fetched,
            expected_refs=expected,actual_vector_matches=actual==expected,fetched_vector_matches=fetched==expected,
            REST_PRs=dict(A=pa,B=pb),native_group=group,objects=objects,
            retained_A_v2_range=advanced['range'],retained_A_v2_patch=own,retained_marker_delta=marker_delta,
            retained_original_v1_ranges={key:ready['ranges'][key] for key in ('A-v1','B-v1')},retained_A_v1_patch=old_a_patch,retained_B_v1_patch=old_b_patch,
            current_A_marker=marker_proc.decode(errors='replace'),expected_marker=ready['trees']['A2']['late-a-marker.txt'],
            marker_matches=marker_proc.decode(errors='replace')==ready['trees']['A2']['late-a-marker.txt'],
            projection_disagreements={role:dict(REST_head=pr['head']['sha'],actual_ref=actual.get(ready['refs'][role]),
                REST_base=pr['base']['sha'],base_name=pr['base']['ref']) for role,pr in [('A',pa),('B',pb)]
                if pr['head']['sha']!=actual.get(ready['refs'][role]) or pr['base']['sha']!=actual.get(pr['base']['ref'])})
        save(ROOT/(label+'.json'),row)
        rows.append(row)
        print(json.dumps(dict(cohort=index,at=row['ended']['utc'],vector_exact=row['actual_vector_matches'],marker_matches=row['marker_matches'],projection_disagreements=row['projection_disagreements'])),flush=True)
    git('fsck','fsck','--full','--no-dangling')
    save(ROOT/'RESULTS.json',dict(repository=REPO,prefix=PREFIX,prs=ready['prs'],stack=666,
        observations=rows,all_vectors_exact=all(r['actual_vector_matches'] and r['fetched_vector_matches'] for r in rows),
        all_markers_retained=all(r['marker_matches'] for r in rows),
        effect_status='Observer sent no native request or remote mutation. Root reports the resumed initiation returned409/Stack contents have changed with A/B Skipped; actual POST carried old A0 while selected B0 was unchanged; this observer independently records bounded graph outcomes only.',
        limits='No HAR/website job-status endpoint inspected; no no-job/cancellation/continuous-silence/future-write guarantee from these cohorts'))


if __name__=='__main__':
    main()
