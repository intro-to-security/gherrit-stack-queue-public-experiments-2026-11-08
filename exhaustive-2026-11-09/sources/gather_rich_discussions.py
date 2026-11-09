import concurrent.futures
import datetime
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
selection = json.loads((ROOT / 'discussion-selection.json').read_text())['selected']

def fetch(item):
    number = item['number']
    query = '''query { repository(owner:"github",name:"gh-stack") { discussion(number:NUMBER) { id url title body closed isAnswered createdAt updatedAt author { login } comments(first:100) { totalCount nodes { id url author { login } authorAssociation body createdAt isAnswer replies(first:100) { totalCount nodes { id url author { login } authorAssociation body createdAt } pageInfo { hasNextPage endCursor } } } pageInfo { hasNextPage endCursor } } } } }'''.replace('NUMBER', str(number))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    process = subprocess.run(['gh', 'api', 'graphql', '-f', 'query=' + query], capture_output=True, text=True, timeout=90)
    ended = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = {'query': query, 'started': started, 'ended': ended, 'returncode': process.returncode, 'stderr': process.stderr}
    try:
        result['response'] = json.loads(process.stdout)
    except json.JSONDecodeError:
        result['stdout'] = process.stdout
    (ROOT / 'receipts' / ('discussion-' + str(number) + '-rich.json')).write_text(json.dumps(result, indent=2) + '\n')
    discussion = result.get('response', {}).get('data', {}).get('repository', {}).get('discussion')
    return {'number': number, 'returncode': process.returncode, 'comments': discussion.get('comments', {}).get('totalCount') if discussion else None, 'error': result.get('response', {}).get('errors')}

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    results = list(pool.map(fetch, selection))
(ROOT / 'rich-discussion-index.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps({'selected': len(results), 'failures': [r for r in results if r['returncode'] or r['error']]}))
