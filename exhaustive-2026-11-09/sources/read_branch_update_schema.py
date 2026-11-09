import datetime
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
queries = {
    'UpdatePullRequestBranchInput': 'query { __type(name:"UpdatePullRequestBranchInput") { name description inputFields { name description type { kind name ofType { kind name } } defaultValue } } }',
    'UpdatePullRequestBranchPayload': 'query { __type(name:"UpdatePullRequestBranchPayload") { name description fields { name description type { kind name ofType { kind name } } } } }',
    'PullRequestBranchUpdateMethod': 'query { __type(name:"PullRequestBranchUpdateMethod") { name description enumValues { name description } } }',
}
for name, query in queries.items():
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    run = subprocess.run(['gh', 'api', 'graphql', '-f', 'query=' + query], text=True, capture_output=True, timeout=90)
    receipt = {'query': query, 'started': started, 'ended': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'returncode': run.returncode, 'stderr': run.stderr, 'response': json.loads(run.stdout) if run.stdout else None}
    (root / 'receipts' / ('schema-' + name + '.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt['response']))
