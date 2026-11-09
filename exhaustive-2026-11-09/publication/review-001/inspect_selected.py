import base64
import collections
import hashlib
import json
from pathlib import Path
import re
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = ROOT/'publication/prep/root-review-manifest-initial.json'
INSPECTION = ROOT/'publication/prep/root-inspection-initial.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads(MANIFEST.read_bytes())
    inspection = json.loads(INSPECTION.read_bytes())
    selected = {row['path']:row for row in manifest['files']}
    assert len(selected) == len(manifest['files']) == 893
    forbidden = {'.git','private','sealed','rawhuman','thirdpartycache','cache','caches','checkouts'}
    contents, mismatches, nontext, json_errors, headers, visibility, payloads, hard = {}, [], [], [], [], [], [], []
    local_paths = collections.Counter()
    tokens = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|(?:AKIA|ASIA)[A-Z0-9]{16})\b|-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----|https?://[^\s/@:]+:[^\s/@]+@')
    def walk(value, where, source):
        if isinstance(value,dict):
            for key,item in value.items():
                point = where+'/'+key
                if (key == 'private' and item is True) or (key == 'visibility' and item == 'private'):
                    visibility.append(dict(path=source,pointer=point))
                if key == 'encoding' and item == 'base64':
                    payloads.append(dict(path=source,pointer=where,name=value.get('name'),source_url=value.get('html_url')))
                walk(item,point,source)
        elif isinstance(value,list):
            for index,item in enumerate(value):
                walk(item,where+'/'+str(index),source)
    for name, entry in selected.items():
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts and not forbidden.intersection(path.parts)
        current = ROOT
        for part in path.parts:
            current = current/part
            assert not current.is_symlink()
        assert stat.S_ISREG(current.stat().st_mode)
        data = current.read_bytes()
        actual = dict(bytes=len(data),sha256=sha(data))
        if actual != {key:entry[key] for key in ('bytes','sha256')}:
            mismatches.append(dict(path=name,expected={key:entry[key] for key in ('bytes','sha256')},actual=actual))
        if b'\0' in data:
            nontext.append(name)
        text = data.decode('utf-8')
        contents[name] = text
        for match in tokens.finditer(text):
            hard.append(dict(path=name,line=text.count('\n',0,match.start())+1,match_sha256=sha(match.group().encode())))
        for number,line in enumerate(text.splitlines(),1):
            match = re.match(r'(?i)^(authorization|set-cookie|cookie):\s*(.*)',line)
            if match:
                headers.append(dict(path=name,line=number,name=match.group(1).lower(),value_sha256=sha(match.group(2).encode()),masked=match.group(2).lower() in ('[redacted]','***')))
        for match in re.finditer(r'/(Users|home)/([^/\s"\'<>]+)',text):
            local_paths[match.group()] += 1
        if name.endswith('.json'):
            try:
                walk(json.loads(text),'',name)
            except json.JSONDecodeError as error:
                json_errors.append(dict(path=name,error=str(error)))
    source = json.loads(contents['target/ci-source.json'])
    decoded = base64.b64decode(source['content'])
    ci = dict(bytes=len(decoded),sha256=sha(decoded),git_blob_sha1=hashlib.sha1(f'blob {len(decoded)}\0'.encode()+decoded).hexdigest(),
              expected_blob=source['sha'],url=source['html_url'],decoded_equal_selected_yaml=decoded == contents['target/actual-ci.yml'].encode())
    assert ci['git_blob_sha1'] == ci['expected_blob'] and ci['decoded_equal_selected_yaml']
    license_records = json.loads(contents['code-survey/LICENSES.json'])
    pins = json.loads(contents['code-survey/CASE-PINS.json'])
    assert {row['repo']:row['ref'] for row in pins} == {row['repository']:row['ref'] for row in license_records}
    links=[]
    pattern=re.compile(r'(?<!!)\[([^\]\n]+)\]\(([^\s)>]+)\)')
    for name,text in contents.items():
        if name.endswith('.md'):
            for match in pattern.finditer(text):
                target=match.group(2)
                if '://' not in target and not target.startswith('#'):
                    import posixpath
                    resolved=posixpath.normpath(str(Path(name).parent/target.split('#')[0]))
                    if resolved not in selected:
                        links.append(dict(path=name,target=target,resolved=resolved))
    record=dict(method='Read all exact allowlisted current bytes for hashes/structural scan; manual review is separately bounded in REPORT.md. No omitted directory opened.',
        manifest_sha256=sha(MANIFEST.read_bytes()),inspection_sha256=sha(INSPECTION.read_bytes()),files=len(contents),bytes=sum(len(v.encode()) for v in contents.values()),
        mismatches=mismatches,nontext=nontext,json_errors=json_errors,hard_token_patterns=hard,actual_unmasked_header_lines=[row for row in headers if not row['masked']],
        header_lines=headers,private_visibility_json=visibility,base64_payloads=payloads,ci_payload=ci,
        local_path_prefixes=dict(local_paths),license_projects=len(license_records),license_nonstandard=[row['repository'] for row in license_records if row['github_license_metadata'].get('spdx_id') == 'NOASSERTION'],
        omitted_markdown_links_current_bytes=links,root_initial_heuristic_counts=dict(collections.Counter(row['rule'] for row in inspection['review_findings'])),
        limitations='Pattern scans do not detect all credentials/privacy/license concerns; runtime/disk inputs and newer omitted lanes were not audited.')
    (HERE/'FINDINGS.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({key:value for key,value in record.items() if key not in ('header_lines','omitted_markdown_links_current_bytes')},indent=2))


if __name__ == '__main__':
    main()
