import datetime
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
names = ['PullRequestStack', 'PullRequestStackEntry', 'PullRequest', 'HeadRefForcePushedEvent', 'AutomaticBaseChangeSucceededEvent', 'AutomaticBaseChangeFailedEvent', 'AddedToMergeQueueEvent', 'RemovedFromMergeQueueEvent', 'Mutation']
for name in names:
    query = 'query { __type(name:' + json.dumps(name) + ') { name kind description fields(includeDeprecated:true) { name description args { name description type { kind name ofType { kind name } } } type { kind name ofType { kind name } } } } }'
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    run = subprocess.run(['gh', 'api', 'graphql', '-f', 'query=' + query], text=True, capture_output=True, timeout=90)
    ended = datetime.datetime.now(datetime.timezone.utc).isoformat()
    response = json.loads(run.stdout) if run.stdout else None
    receipt = {'query': query, 'started': started, 'ended': ended, 'returncode': run.returncode, 'stderr': run.stderr, 'response': response}
    (root / 'receipts' / ('schema-' + name + '.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'type': name, 'returncode': run.returncode, 'errors': response.get('errors') if response else run.stderr}))
