import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CAPTURE=ROOT/'capture-001'
FIXTURE=ROOT.parent/'fixture-a-prep'


def main():
    ready=json.loads((FIXTURE/'READY-A-ARCHIVED.json').read_bytes())
    advanced=json.loads((FIXTURE/'A-ADVANCED.json').read_bytes())
    result=json.loads((CAPTURE/'RESULTS.json').read_bytes())
    assert len(result['observations'])==3
    assert set(ready['current_refs'])==set(advanced['current_refs'])
    assert [k for k in ready['current_refs'] if ready['current_refs'][k]!=advanced['current_refs'][k]]==[ready['refs']['A']]
    assert ready['current_refs'][ready['refs']['archiveA2']]==ready['commits']['A2']
    assert advanced['selected_B_unchanged']==ready['commits']['B0']
    rows=[]
    for row in result['observations']:
        assert row['actual_refs']==row['fetched_refs']==advanced['current_refs']
        assert row['retained_A_v2_range']==ready['ranges']['A-v2']==advanced['range']
        assert row['marker_matches'] and row['current_A_marker']==ready['trees']['A2']['late-a-marker.txt']
        assert 'diff --git a/a.txt b/a.txt\n' in row['retained_A_v2_patch']
        assert 'diff --git a/late-a-marker.txt b/late-a-marker.txt\n' in row['retained_A_v2_patch']
        assert row['retained_marker_delta'].count('diff --git ')==1
        assert row['retained_original_v1_ranges']=={k:ready['ranges'][k] for k in ('A-v1','B-v1')}
        assert row['retained_B_v1_patch'].count('diff --git ')==1 and 'diff --git a/b.txt b/b.txt' in row['retained_B_v1_patch']
        assert row['retained_A_v1_patch'].count('diff --git ')==1 and 'diff --git a/a.txt b/a.txt' in row['retained_A_v1_patch']
        for oid,record in row['objects'].items():
            raw=record['raw_commit'].encode()
            assert hashlib.sha1(f'commit {len(raw)}\0'.encode()+raw).hexdigest()==oid
            name=next(name for name,value in ready['commits'].items() if value==oid)
            assert record['raw_commit'].strip()==ready['objects'][name].strip()
        group=row['native_group']
        assert group['number']==666 and group['node_id']==ready['stack']['node_id']
        assert [member['number'] for member in group['pull_requests']]==[664,665]
        for role in ('A','B'):
            pr=row['REST_PRs'][role]
            assert pr['number']==ready['prs'][role] and pr['node_id']==ready['nodes'][role]
            assert pr['state']=='open' and not pr['merged']
            assert pr['head']['ref']==ready['refs'][role]
            assert pr['head']['sha']==row['actual_refs'][ready['refs'][role]]
        rows.append(dict(index=row['index'],started=row['started'],ended=row['ended'],seven_refs_exact=True,
            immutable_commit_bodies_match=True,canonical_open_order_exact=True,A_v2_marker_retained=True,
            REST_A_base_is_old_T0=row['REST_PRs']['A']['base']['sha']==ready['commits']['T0'],
            actual_trunk_is_T1=row['actual_refs'][ready['refs']['trunk']]==ready['commits']['T1'],
            REST_B_base_is_old_A0=row['REST_PRs']['B']['base']['sha']==ready['commits']['A0'],actual_A_is_A2=row['actual_refs'][ready['refs']['A']]==ready['commits']['A2']))
    output=dict(passed=True,rows=rows,git_fsck_exit=json.loads((CAPTURE/'fsck.command.json').read_bytes())['exit'],
        source_results_sha256=hashlib.sha256((CAPTURE/'RESULTS.json').read_bytes()).hexdigest(),
        limits='Pure retained-readback check; no HAR/job-status/remote query; no future-write or continuous-silence inference')
    assert output['git_fsck_exit']==0
    print(json.dumps(output,indent=2))
    target=ROOT/'CHECKS.json'
    with target.open('x') as stream:
        json.dump(output,stream,indent=2);stream.write('\n')


if __name__=='__main__':
    main()
