"""Assemble only explicit four-case text paths after the new inputs are frozen."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
CAMPAIGN=HERE.parents[3]
LANE=CAMPAIGN/'ui/stale-map-debug-prep'
OLD=HERE.parent/'final/FINAL-ALLOWLIST.json'
MASTER=LANE/'RESULTS.md'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()


def main(held_manifest,held_base,history):
    old=json.loads(OLD.read_text());assert len(old['entries'])==933
    old_master=next(x for x in old['entries'] if x['path']=='ui/stale-map-debug-prep/RESULTS.md')
    if sha(MASTER)==old_master['sha256']:
        raise ValueError('Wait for the four-case master report; current master is still the three-case version')
    history=history.resolve()
    if (not history.is_relative_to(LANE) or history==MASTER or history.suffix!='.md'
            or any(x.endswith('.git') or x.lower() in {'private','sealed','stores','model','refinement','critic'} for x in history.parts)
            or sha(history)!=old_master['sha256']):
        raise ValueError('Exact retained three-case master history required')
    if held_manifest.resolve().parent!=LANE/'outcome-held-fresh' or held_manifest.name not in {'SOURCE-MANIFEST.json','MANIFEST.json'}:
        raise ValueError('Expected only the owned held-fresh outcome manifest')
    root=CAMPAIGN if held_base=='campaign' else held_manifest.parent
    selected={};mismatches=[]
    def add(path,origin):
        if path.is_symlink():raise ValueError('Symlink not selected')
        path=path.resolve();rel=str(path.relative_to(CAMPAIGN))
        if any(x.endswith('.git') or x.lower() in {'private','sealed','stores','model','refinement','critic'} for x in path.parts):
            raise ValueError('Excluded tree reference: '+rel)
        if path.name in {'config','caffeinate-session.json','caffeinate-session.log'} or path.suffix.lower() in {'.har','.gz','.zip','.img','.raw','.qcow2'}:
            raise ValueError('Excluded artifact: '+rel)
        if not path.is_file():raise ValueError('Expected exact text file: '+rel)
        path.read_bytes().decode('utf8')
        selected.setdefault(rel,[]).append(origin)
    for record in old['entries']:
        path=CAMPAIGN/record['path']
        if path!=MASTER and (path.stat().st_size!=record['bytes'] or sha(path)!=record['sha256']):
            mismatches.append(record['path'])
        add(path,'prior933 explicit selection; master has a separately retained new source version')
    if mismatches:raise ValueError('Unexpected changes outside master: '+str(mismatches))
    add(history,'exact historical three-case master bytes')
    def manifest(path,base,label):
        value=json.loads(path.read_text())
        entries=value.get('files',value.get('entries'))
        if not isinstance(entries,list):raise ValueError('Explicit safe text entry list required')
        for record in entries:
            rel=Path(record['path'])
            if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe manifest path')
            target=base/rel
            add(target,label)
            if target.stat().st_size!=record['bytes'] or sha(target)!=record['sha256']:
                raise ValueError('Supplied manifest identity mismatch: '+str(target))
        add(path,label+' provenance')
    fixture=LANE/'fixture-held-fresh-prep'
    manifest(fixture/'SOURCE-MANIFEST.json',fixture,'held local source preparation')
    for path in fixture.iterdir():
        if path.is_file():add(path,'exact held fixture source/local/READY/verification/preparation record')
    for name in ['prepare-source','source-inputs','records']:
        folder=fixture/name
        if folder.is_dir():
            for path in folder.iterdir():
                if not path.is_file():raise ValueError('Unexpected nested fixture directory')
                add(path,'owned held fixture snapshot/native intent/receipt')
    for name in ['NETWORK-HELD-FRESH.json','INITIATION-HELD-FRESH-INTENT.json','PAUSE-HELD-FRESH.json','PAUSE-HELD-FRESH-AFTER-HOLD.json','RESUME-HELD-FRESH-INTENT.json','hold_unchanged.py']:
        add(LANE/name,'actual held-fresh UI/monitor record')
    for name in ['START.json','sample-0.json','sample-1.json','sample-2.json','HOLD-VERIFIED.json']:
        add(LANE/'held-timer'/name,'one-process monotonic hold with three bounded exact-ref samples')
    add(CAMPAIGN/'control/ui-stale-debug-grant-007.json','exact held preparation coordinator grant')
    manifest(held_manifest,root,'independent held outcome safe text list')
    assert not any('caffeinate-session' in x for x in selected)
    data=dict(base='campaign root',paths=[dict(path=x,selected_by=selected[x]) for x in sorted(selected)],input_manifest_hash_mismatches=[],
        source_versions=dict(three_case_allowlist_sha256=sha(OLD),three_case_master_sha256=old_master['sha256'],history_path=str(history.relative_to(CAMPAIGN)),new_master_sha256=sha(MASTER),held_manifest_path=str(held_manifest.relative_to(CAMPAIGN)),held_manifest_base=held_base,held_manifest_sha256=sha(held_manifest)),
        local_only_operational_record='caffeinate-session.json/.log (PID9648); not read or selected as product evidence')
    target=HERE/'SELECTION-PATHS.json'
    if target.exists():raise ValueError('New four-case selection already exists; preserve it rather than overwrite')
    target.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(files=len(selected),source_bytes=sum((CAMPAIGN/x).stat().st_size for x in selected),selection_sha256=sha(target)),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--held-manifest',required=True,type=Path)
    parser.add_argument('--held-base',required=True,choices=['campaign','manifest-directory'])
    parser.add_argument('--three-case-history',required=True,type=Path)
    a=parser.parse_args();main(a.held_manifest.resolve(),a.held_base,a.three_case_history)
