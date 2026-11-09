import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'RESULTS.json'


def main():
    record = json.loads(SOURCE.read_text())
    expected = {}
    for commit in record['commits']:
        expected[commit['commit']] = ('commit',commit)
        for path, entry in commit['files'].items():
            value = ('blob',bytes.fromhex(entry['hex']))
            assert expected.get(entry['blob'],value) == value
            expected[entry['blob']] = value
    argv = ['git','-c','core.hooksPath=/dev/null','-c','core.pager=cat','cat-file','--batch']
    data = ''.join(oid+'\n' for oid in expected).encode()
    env = {key:value for key,value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_TERMINAL_PROMPT='0',LC_ALL='C')
    result = subprocess.run(argv,cwd=ROOT/'repo.git',input=data,capture_output=True,env=env)
    out = ROOT/'readback'
    out.mkdir(exist_ok=False)
    (out/'stdin').write_bytes(data)
    (out/'stdout').write_bytes(result.stdout)
    (out/'stderr').write_bytes(result.stderr)
    assert result.returncode == 0
    offset = 0
    for oid, (expected_kind,value) in expected.items():
        newline = result.stdout.index(b'\n',offset)
        actual_oid, kind, size = result.stdout[offset:newline].decode().split()
        size = int(size)
        body = result.stdout[newline+1:newline+1+size]
        assert result.stdout[newline+1+size:newline+2+size] == b'\n'
        offset = newline+2+size
        assert actual_oid == oid and kind == expected_kind
        assert hashlib.sha1(f'{kind} {size}\0'.encode()+body).hexdigest() == oid
        if kind == 'blob':
            assert body == value
        else:
            assert body.startswith(('tree '+value['tree']+'\n').encode())
            if value['parent'] is not None:
                assert ('\nparent '+value['parent']+'\n').encode() in body
            for field in ('author','committer'):
                assert ('\n'+field+' Josh Liebow-Feeser <hello@joshlf.com> ').encode() in body
            assert body.endswith(b"\n\nAgent-authored-by: AI agent acting on joshlf's behalf\n")
    assert offset == len(result.stdout)
    rows = {row['id']:row for row in record['cases']}
    checks = []
    a = rows['A-unrelated-base']
    assert ' = ' in a['range_diff']['default'] and not a['literal_diff_of_patches']
    checks.append('unrelated base drift excluded from both exact patch and range-diff')
    b = rows['B-context-drift']
    assert ' < ' in b['range_diff']['default'] and ' > ' in b['range_diff']['default']
    assert ' ! ' in b['range_diff']['factor100']
    assert '- context = old' in b['range_diff']['factor100'] and '+ context = new' in b['range_diff']['factor100']
    for side in ('old','new'):
        patch = (ROOT/'evidence/B-context-drift'/(side+'.patch')).read_text()
        assert '-value = 0\n+value = 1\n' in patch
    checks.append('same authored line edit remains; context-only base drift changes displayed patch/matching')
    c = rows['C-binary-change']
    by_commit = {entry['commit']:entry for entry in record['commits']}
    old_bin = by_commit[c['old']['tip']]['files']['data.bin']
    new_bin = by_commit[c['new']['tip']]['files']['data.bin']
    assert old_bin['blob'] != new_bin['blob'] and old_bin['hex'] != new_bin['hex']
    assert all(' = ' in text for text in c['range_diff'].values())
    assert 'index ' in c['literal_diff_of_patches']
    for side in ('old','new'):
        assert 'GIT binary patch' in (ROOT/'evidence/C-binary-change'/(side+'.binary.patch')).read_text()
    checks.append('different verified binary bytes receive equals; full-index/binary patches retain distinct identities/payloads')
    d = rows['D-mode-change']
    old_mode = by_commit[d['old']['tip']]['files']['script.sh']
    new_mode = by_commit[d['new']['tip']]['files']['script.sh']
    assert old_mode['blob'] == new_mode['blob'] and (old_mode['mode'],new_mode['mode']) == ('100755','100644')
    assert '100644 => 100755' in d['range_diff']['default'] and ' ! ' in d['range_diff']['default']
    checks.append('mode difference displayed despite identical result script bytes')
    e = rows['E-series-reorder']['range_diff']['default'].splitlines()
    assert len(e) == 2 and e[0].startswith('2:') and ' = 1:' in e[0] and e[1].startswith('1:') and ' = 2:' in e[1]
    checks.append('two reordered disjoint commits paired by patch instead of ordinal')
    output = dict(passed=True,objects_read_back=len(expected),checks=checks,argv=argv,cwd=str(ROOT/'repo.git'),exit=result.returncode,
        stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),source_results_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        limits='Exact observations in these synthetic cases; no semantic equivalence inference from output markers')
    (ROOT/'VERIFICATION.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__ == '__main__':
    main()
