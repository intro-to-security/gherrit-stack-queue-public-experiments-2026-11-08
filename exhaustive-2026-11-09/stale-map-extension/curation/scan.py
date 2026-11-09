"""Scan only this frozen explicit three-case selection; never traverse stores."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

HERE=Path(__file__).resolve().parent
CAMPAIGN=HERE.parents[3]
paths=json.loads((HERE/'SELECTION-PATHS.json').read_text())['paths']
selected={x['path'] for x in paths}
sha=lambda data:hashlib.sha256(data).hexdigest()
records=[];hard=[];local=[];signatures=[];embedded=[];headers=[];private_false=0;json_count=0
node_ids=0;raw_commits=0;md=[]
secret_keys={'authorization','cookie','set-cookie','x-csrf-token','x-github-token','gh_token','github_token','access_token','client_secret','password'}
credential=re.compile(r'github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')

def walk(value,path,location='$'):
    global private_false,node_ids,raw_commits
    if isinstance(value,dict):
        for key,item in value.items():
            here=location+'.'+key;lower=key.lower()
            if lower in secret_keys and item not in (None,'',False,[],{}):hard.append(dict(path=path,kind='nonempty credential/header field',location=here))
            if lower=='private':
                if item is True:hard.append(dict(path=path,kind='private repository metadata',location=here))
                elif item is False:private_false+=1
            if lower=='node_id':node_ids+=1
            if lower=='raw_commit':raw_commits+=1
            if lower=='input' and isinstance(item,str) and item.lstrip().startswith(('{','[')):
                try:json.loads(item);embedded.append(dict(path=path,location=here,kind='JSON-encoded own native request body'))
                except ValueError:hard.append(dict(path=path,kind='malformed embedded request JSON',location=here))
            if lower in {'response_headers','request_headers'} and isinstance(item,list):
                for h in item:
                    name=h.get('name','').lower()
                    headers.append(dict(path=path,name=name))
                    if name not in {'content-type','date','x-github-request-id'}:hard.append(dict(path=path,kind='unexpected retained HTTP header',name=name))
            walk(item,path,here)
    elif isinstance(value,list):
        for i,item in enumerate(value):walk(item,path,location+'['+str(i)+']')

for entry in paths:
    rel=entry['path'];path=CAMPAIGN/rel
    assert not path.is_symlink() and path.is_file()
    assert not any(x.endswith('.git') or x.lower() in {'private','sealed','stores','model','refinement'} for x in path.parts)
    assert path.name!='config' and path.suffix.lower() not in {'.har','.zip','.gz','.img','.raw','.qcow2'}
    data=path.read_bytes();text=data.decode('utf-8')
    if b'\0' in data:hard.append(dict(path=rel,kind='NUL'))
    if len(data)>=1024*1024:hard.append(dict(path=rel,kind='file bound'))
    if credential.search(text):hard.append(dict(path=rel,kind='credential literal pattern'))
    if re.search(r'"private"\s*:\s*true',text,re.I):hard.append(dict(path=rel,kind='private:true text pattern'))
    if re.search(r'"(?:authorization|cookie|set-cookie|x-csrf-token|gh_token|github_token|access_token|client_secret|password)"\s*:\s*"[^"]+',text,re.I):hard.append(dict(path=rel,kind='nonempty credential-bearing text field'))
    if '/Users/' in text or '/private/' in text:local.append(rel)
    if '-----BEGIN PGP SIGNATURE-----' in text:signatures.append(rel)
    opaque=re.search(r'[A-Za-z0-9+/]{80,}={0,2}',text)
    if opaque and '-----BEGIN PGP SIGNATURE-----' not in text:hard.append(dict(path=rel,kind='unclassified long encoded-looking string'))
    if 'GIT binary patch' in text:hard.append(dict(path=rel,kind='unclassified binary patch payload'))
    if path.suffix=='.json':walk(json.loads(text),rel);json_count+=1
    if path.suffix=='.md':md.append((rel,text))
    records.append(dict(path=rel,bytes=len(data),sha256=sha(data),selected_by=entry['selected_by']))

by_name={}
for rel in selected:by_name.setdefault(Path(rel).name,[]).append(rel)

def availability(doc,target):
    target=unquote(target.strip().strip('<>')).split('#',1)[0]
    if not target:return 'same-document',[]
    if urlsplit(target).scheme:return 'external-not-fetched',[]
    if any(x.endswith('.git') for x in Path(target).parts) or target.endswith('.har'):return 'explicit-local-only-excluded',[]
    if target.startswith('refs/'):return 'Git-ref-identifier',[]
    absolute=Path(target) if target.startswith('/') else (CAMPAIGN/doc).parent/target
    try:rel=str(absolute.resolve().relative_to(CAMPAIGN))
    except ValueError:return 'outside-delivery-local-path',[]
    if rel in selected:return 'selected-file',[rel]
    prefix=rel.rstrip('/')+'/'
    descendants=[x for x in selected if x.startswith(prefix)]
    if descendants:return 'selected-directory-subset',descendants[:3]
    if '/' not in target and target in by_name:return 'selected-basename-reference',by_name[target][:3]
    return 'unselected-or-unresolved',[]

links=[];literals=[]
for doc,text in md:
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
        state,witnesses=availability(doc,target)
        if doc=='ui/stale-map-debug-prep/history/RESULTS-three-cases.md' and not urlsplit(target).scheme:
            original='ui/stale-map-debug-prep/'+target
            if original in selected:state,witnesses='requires-historical-link-context-remap',[original]
        elif state=='selected-basename-reference':state='requires-explicit-link-context'
        links.append(dict(document=doc,target=target,status=state,selected_witnesses=witnesses))
    for value in re.findall(r'`([^`\n]+)`',text):
        if not re.search(r'(?:\.(?:json|py|md|stdout|stderr|diff|log|har|git)(?:$|[/ :])|/)$',value):continue
        state,witnesses=availability(doc,value);literals.append(dict(document=doc,literal=value,status=state,selected_witnesses=witnesses))
manual_literals={
 ('ui/stale-map-debug-prep/RESULTS.md','NETWORK-*.json'):('selected-wildcard-family',['ui/stale-map-debug-prep/NETWORK-A.json','ui/stale-map-debug-prep/NETWORK-B.json','ui/stale-map-debug-prep/NETWORK-A-FRESH.json','ui/stale-map-debug-prep/NETWORK-HELD-FRESH.json']),
 ('ui/stale-map-debug-prep/fixture-prep/HANDOFF.md','control/rootlab.py'):('selected-campaign-relative-literal',['control/rootlab.py']),
 ('ui/stale-map-debug-prep/outcome-b/REPORT.md','fixture-prep/READY.json'):('selected-lane-relative-literal',['ui/stale-map-debug-prep/fixture-prep/READY.json'])}
manual_literals.update({
 ('ui/stale-map-debug-prep/fixture-held-fresh-prep/HANDOFF.md','fixture-a-fresh-prep/fixture.py'):('selected-lane-relative-literal',['ui/stale-map-debug-prep/fixture-a-fresh-prep/fixture.py']),
 ('ui/stale-map-debug-prep/history/RESULTS-three-cases.md','fixture-prep/'):('selected-historical-directory-subset',['ui/stale-map-debug-prep/fixture-prep/fixture.py']),
 ('ui/stale-map-debug-prep/history/RESULTS-three-cases.md','fixture-a-prep/'):('selected-historical-directory-subset',['ui/stale-map-debug-prep/fixture-a-prep/fixture.py']),
 ('ui/stale-map-debug-prep/history/RESULTS-three-cases.md','NETWORK-*.json'):('selected-historical-wildcard-family',['ui/stale-map-debug-prep/NETWORK-A.json','ui/stale-map-debug-prep/NETWORK-B.json','ui/stale-map-debug-prep/NETWORK-A-FRESH.json'])})
for row in literals:
    key=(row['document'],row['literal'])
    if key in manual_literals:
        state,witnesses=manual_literals[key]
        assert all(x in selected for x in witnesses)
        row.update(status=state,selected_witnesses=witnesses,resolution='Explicit context interpretation; original literal retained, no link/source rewrite')
prior=HERE/'FINAL-ALLOWLIST.json'
if prior.exists():
    old={x['path']:(x['bytes'],x['sha256']) for x in json.loads(prior.read_text())['entries']}
    changed=[x['path'] for x in records if old.get(x['path'])!=(x['bytes'],x['sha256'])]
    if changed:raise RuntimeError('Frozen source selection changed; prepare a new snapshot: '+str(changed))
scan=dict(selected_files=len(records),selected_bytes=sum(x['bytes'] for x in records),largest_file=max(x['bytes'] for x in records),json_parsed=json_count,
    utf8=True,text_private_and_credential_field_scan=True,hard_findings=hard,private_false_metadata_fields=private_false,public_node_id_fields=node_ids,raw_commit_fields=raw_commits,
    retained_header_fields=headers,public_Git_PGP_signature_text_files=signatures,embedded_JSON_request_bodies=embedded,
    local_path_context_files=local,source_manifest_hash_mismatches=json.loads((HERE/'SELECTION-PATHS.json').read_text())['input_manifest_hash_mismatches'],
    limits='Focused manual source/key-field review plus structural whole-byte reads. Not every-byte human review, root approval, external URL validation, HAR/store reading or signature verification.')
if scan['selected_bytes']>=4*1024*1024:hard.append(dict(kind='total bound'))
for name,value in [('FINAL-ALLOWLIST.json',dict(base='campaign root',historical_scope='Four completed cases, including held-fresh control; full semantic review remains coordinator-owned',entries=records)),('STRUCTURAL-SCAN.json',scan),('AVAILABILITY.json',dict(markdown_links=links,path_literals=literals,limits='No excluded-path existence probe or external fetch. Bare filenames may identify selected records by basename; source paths/prose are preserved.'))]:
    (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps(dict(files=len(records),bytes=scan['selected_bytes'],json_parsed=json_count,hard_findings=hard,MD_links=len(links),path_literals=len(literals)),indent=2))
