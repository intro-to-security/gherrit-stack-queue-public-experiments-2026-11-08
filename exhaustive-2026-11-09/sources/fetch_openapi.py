import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

root = Path(__file__).resolve().parent
url = 'https://raw.githubusercontent.com/github/rest-api-description/2f8f80e47ea4d3292cf4e37ba9d9b25475e06140/descriptions/api.github.com/api.github.com.json'
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
with urllib.request.urlopen(url, timeout=90) as response:
    data = response.read()
schema = json.loads(data)
paths = {path: value for path, value in schema['paths'].items() if '/stacks' in path or 'merge-async' in path}
refs = set()
def collect(value):
    if isinstance(value, dict):
        if '$ref' in value:
            refs.add(value['$ref'])
        for child in value.values():
            collect(child)
    elif isinstance(value, list):
        for child in value:
            collect(child)
collect(paths)
direct_refs = {}
for ref in sorted(refs):
    if ref.startswith('#/'):
        value = schema
        for segment in ref[2:].split('/'):
            value = value[segment.replace('~1', '/').replace('~0', '~')]
        direct_refs[ref] = value
webhooks = {key: value for key, value in schema.get('webhooks', {}).items() if 'stack' in key.lower()}
receipt = {'source_url': url, 'retrieved_started': started, 'retrieved_ended': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'info': schema['info'], 'matching_path_names': list(paths), 'matching_paths': paths, 'ordinary_update_branch': schema['paths'].get('/repos/{owner}/{repo}/pulls/{pull_number}/update-branch'), 'direct_references': direct_refs, 'webhook_keys_containing_stack': webhooks, 'limit': 'Exact paths and their direct references retained, plus the ordinary update-branch path for comparison. Other source content is identified by pinned source URL and complete-download SHA256, not copied here. This is a public schema, not server implementation.'}
(root / 'receipts' / 'openapi-focused.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'bytes': len(data), 'sha256': receipt['sha256'], 'paths': list(paths), 'direct_refs': list(direct_refs), 'webhooks': list(webhooks)}))
