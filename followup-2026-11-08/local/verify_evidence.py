#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
ENV = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
ENV.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0', LC_ALL='C')
rows = []
for current, directories, files in os.walk(ROOT):
    path = Path(current)
    if 'HEAD' in files and (path / 'objects').is_dir() and (path / 'refs').is_dir():
        p = subprocess.run(['git', '--git-dir=' + str(path), 'fsck', '--full', '--no-reflogs'], env=ENV, capture_output=True, text=True)
        rows.append({'git_directory': str(path.relative_to(ROOT)), 'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
        directories[:] = []
source_names = ['PLAN.md', 'baseline-harness.py', 'followup.py', 'interface.py', 'recovery_adversarial.py', 'HARNESS-CORRECTIONS.md', 'verify_evidence.py']
result = {'repository_count': len(rows), 'fsck_failures': sum(row['exit'] != 0 for row in rows), 'repositories': rows, 'sources': [{'path': name, 'sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), 'bytes': (ROOT / name).stat().st_size} for name in source_names], 'scope': 'Object connectivity/integrity of all retained local fixture Git stores, including negative controls; this does not validate protocol semantics.'}
(ROOT / 'OBJECT-VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['repositories', 'sources']}))
raise SystemExit(bool(result['fsck_failures']))
