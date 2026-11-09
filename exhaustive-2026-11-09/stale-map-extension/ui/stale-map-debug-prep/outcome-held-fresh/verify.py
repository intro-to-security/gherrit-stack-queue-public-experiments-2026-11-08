"""Recheck the retained fresh-map graph without network or a Git store."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CAPTURE=ROOT/'capture-001'
FIXTURE=ROOT.parent/'fixture-held-fresh-prep'


def main():
    ready=json.loads((FIXTURE/'READY.json').read_bytes())
    result=json.loads((CAPTURE/'RESULTS.json').read_bytes())
    pins=json.loads((CAPTURE/'INPUT-PINS.json').read_bytes())
    for name,record in pins.items():
        path=ROOT/name if name=='observer.py' else ROOT.parent/name if name=='NETWORK-HELD-FRESH.json' else FIXTURE/name
        data=path.read_bytes()
        assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256']
    assert len(result['observations'])==3
    rows=[];producers=[]
    fixed={k:v for k,v in ready['current_refs'].items() if k not in (ready['refs']['A'],ready['refs']['B'])}
    for row in result['observations']:
        actual=row['actual_refs'];objects=row['objects']
        assert actual==row['fetched_refs'] and set(actual)==set(ready['current_refs'])
        assert all(actual[k]==v for k,v in fixed.items())
        a,b,t=(actual[ready['refs'][role]] for role in ('A','B','trunk'))
        first,last=row['A_rewritten_commits'];only,=row['B_rewritten_commits']
        assert last==a and only==b
        assert objects[first]['parents']==[t] and objects[a]['parents']==[first] and objects[b]['parents']==[a]
        assert row['actual_ranges']=={'A':[t,a],'B':[a,b]}
        assert row['source_ranges']=={'A':ready['ranges']['A-v2'],'B':ready['ranges']['B-v1']}
        assert row['actual_A_full_patch']==row['source_A_full_patch'] and row['actual_B_full_patch']==row['source_B_full_patch']
        assert 'diff --git a/a.txt b/a.txt\n' in row['actual_A_full_patch'] and 'diff --git a/late-a-marker.txt b/late-a-marker.txt\n' in row['actual_A_full_patch']
        assert row['actual_B_full_patch'].count('diff --git ')==1 and 'diff --git a/b.txt b/b.txt\n' in row['actual_B_full_patch']
        assert objects[a]['tree']==ready['expected_result_trees']['expected-A2']
        assert objects[b]['tree']==ready['expected_result_trees']['expected-B-over-A2']
        assert all(value==ready['trees']['A2']['late-a-marker.txt'] for value in row['markers'].values())
        group=row['native_group'];assert group['number']==672 and group['node_id']==ready['stack']['node_id'] and group['open']
        assert [q['number'] for q in group['pull_requests']]==[670,671]
        for role,parent in [('A','trunk'),('B','A')]:
            q=row['REST_PRs'][role]
            assert q['number']==ready['prs'][role] and q['node_id']==ready['nodes'][role] and q['state']=='open' and not q['merged']
            assert q['head']['repo']['id']==1450723431 and q['base']['repo']['id']==1450723431
            assert q['head']['ref']==ready['refs'][role] and q['head']['sha']==actual[ready['refs'][role]] and q['base']['ref']==ready['refs'][parent]
        for oid,record in objects.items():
            raw=record['raw_commit'].encode()
            assert hashlib.sha1(('commit '+str(len(raw))+'\0').encode()+raw).hexdigest()==oid
        for old,new in [(ready['commits']['A0'],first),(ready['commits']['A2'],a),(ready['commits']['B0'],b)]:
            src,dst=objects[old],objects[new]
            assert src['message']==dst['message'] and src['author']==dst['author']
            assert src['agent_trailers']==dst['agent_trailers']==["Agent-authored-by: AI agent acting on joshlf's behalf"]
            if row['index']==0:
                producers.append(dict(source=old,rewritten=new,author_preserved=True,message_preserved=True,single_agent_trailer_preserved=True,
                    source_committer=src['committer'],rewritten_committer=dst['committer'],source_has_gpgsig=src['has_gpgsig'],rewritten_has_gpgsig=dst['has_gpgsig']))
        rows.append(dict(index=row['index'],started=row['started'],ended=row['ended'],A=a,B=b,full_A_two_commit_chain=True,full_B_one_commit_chain=True,
            fixed_five_refs=True,canonical_open_order=True,full_source_patches_exact=True,expected_trees_exact=True,marker_both=True,raw_commit_hashes_valid=True))
    assert len({(r['A'],r['B']) for r in rows})==1
    fsck=json.loads((CAPTURE/'fsck.command.json').read_bytes());assert fsck['exit']==0
    output=dict(passed=True,cohorts=rows,producers=producers,fsck_exit=fsck['exit'],result_sha256=hashlib.sha256((CAPTURE/'RESULTS.json').read_bytes()).hexdigest(),
        limits='Retained-byte verification only; no network/store access, signature cryptographic verification, provider implementation or future-write-fence claim')
    with (ROOT/'CHECKS.json').open('x') as stream:json.dump(output,stream,indent=2);stream.write('\n')
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
