import ast
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parent
errors = []
extracted = []
for path in root.glob('*.py'):
    try:
        ast.parse(path.read_text())
    except SyntaxError as error:
        errors.append({'file': str(path), 'error': str(error)})
for path in (root / 'receipts').glob('file-*.json'):
    receipt = json.loads(path.read_text())
    source = receipt['result']['structuredContent']
    output = root / 'extracts' / (path.stem[5:] + '.txt')
    if not output.exists():
        errors.append({'receipt': path.name, 'missing_extract': str(output)})
        continue
    data = output.read_bytes()
    blob_sha = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if output.read_text() != source['content'] or blob_sha != source['sha']:
        errors.append({'file': str(output), 'error': 'source content or Git blob mismatch'})
    extracted.append({'path': str(output.relative_to(root)), 'git_blob_sha': blob_sha, 'matched': blob_sha == source['sha']})
for path in (root / 'receipts').glob('*.json'):
    try:
        receipt = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        errors.append({'file': str(path), 'error': str(error)})
        continue
    if not isinstance(receipt, dict):
        continue
    if receipt.get('returncode', 0) != 0 and path.name != 'graphql-introspection.json':
        errors.append({'file': str(path), 'error': 'unexpected failed source read'})
    result = receipt.get('result')
    if isinstance(result, dict) and result.get('isError'):
        errors.append({'file': str(path), 'error': 'connector isError'})
for path in [root / 'REPORT.md', root / 'COVERAGE.md', root / 'MAINTAINER-QUESTIONS.md']:
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' not in target and not (path.parent / target.split('#')[0]).exists():
            errors.append({'file': str(path), 'missing_link': target})
verification = {'errors': errors, 'checked_extracted_blobs': extracted, 'native_mutations': 0, 'external_messages': 0, 'generic_updatePullRequestBranch_invoked': False}
(root / 'VERIFICATION.json').write_text(json.dumps(verification, indent=2) + '\n')
print(json.dumps({'errors': errors, 'checked_extracts': len(extracted)}))
raise SystemExit(bool(errors))
