import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent


def main():
    inputs={name:(PARENT/name).read_bytes() for name in ('NETWORK-A.json','fixture-a-prep/READY-A-ARCHIVED.json','fixture-a-prep/A-ADVANCED.json')}
    network=json.loads(inputs['NETWORK-A.json'])
    ready=json.loads(inputs['fixture-a-prep/READY-A-ARCHIVED.json'])
    advanced=json.loads(inputs['fixture-a-prep/A-ADVANCED.json'])
    assert len(network['selected_entries'])==1
    entry=network['selected_entries'][0]
    assert entry['method']=='POST' and entry['url']=='https://github.com/'+ready['repository']+'/pull/665/page_data/stack_rebase'
    assert entry['request_body']=={'expectedHeadOids':{'664':ready['commits']['A0'],'665':ready['commits']['B0']}}
    assert entry['status']==409 and json.loads(entry['response_content'])=={'error':'Stack contents have changed'}
    assert advanced['selected_B_unchanged']==ready['commits']['B0']
    assert set(ready['current_refs'])==set(advanced['current_refs'])
    assert [k for k in ready['current_refs'] if ready['current_refs'][k]!=advanced['current_refs'][k]]==[ready['refs']['A']]
    assert ready['current_refs'][ready['refs']['archiveA2']]==ready['commits']['A2']
    result=dict(passed=True,input_sha256={name:hashlib.sha256(data).hexdigest() for name,data in inputs.items()},
        actual_map_old_A0=True,actual_map_selected_B0_unchanged=True,status=409,error='Stack contents have changed',
        archive_already_in_seven_ref_basis=True,only_existing_A_changed_during_advance=True,
        limits='Checks minimized root-retained network record and frozen ref vectors; no raw HAR, debugger/timing rederivation, remote query or native effect')
    with (ROOT/'NETWORK-CHECK.json').open('x') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
