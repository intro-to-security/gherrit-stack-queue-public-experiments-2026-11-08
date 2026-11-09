"""Scoped, recorded hosted operations for after-ack restart experiments."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import subprocess
import time

HOME = Path(__file__).resolve().parent
EVIDENCE = HOME / 'evidence'
GIT = HOME / 'git'
REPO = 'joshlf/gherrit-native-stack-experiments-2026-11-08'
PREFIX = 'exp/fu2/structure/'
BASE = 'repos/' + REPO
NOTICE = "*Authored by an AI agent acting on joshlf's behalf.*"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def command(args, *, text=None, env=None):
    return subprocess.run(args, input=text, env=env, capture_output=True, text=True)


def git(*args, text=None, env=None, check=True):
    result = command(['git', '-C', str(GIT), *args], text=text, env=env)
    if check and result.returncode:
        raise RuntimeError('Git failed: ' + result.stderr)
    return result.stdout.strip() if check else result


def label_path(label, suffix):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', label):
        raise ValueError('Unsafe evidence label')
    return EVIDENCE / (label + suffix)


def manifests():
    return [json.loads(path.read_text()) for path in (HOME / 'fixtures').glob('*/fixture.json')]


def check_write(method, path, payload):
    if method == 'GET':
        if not path.startswith(BASE):
            raise ValueError('Read outside synthetic repository')
        return
    fixtures = manifests()
    owned_prs = {number for fixture in fixtures for number in fixture['prs'].values()}
    owned_stacks = {fixture['stack'] for fixture in fixtures}
    for receipt in EVIDENCE.glob('*-effect-create-D.receipt.json'):
        record = json.loads(receipt.read_text())
        if record.get('http') == 201 and record['payload']['head'].startswith(PREFIX):
            owned_prs.add(record['data']['number'])
    for receipt in EVIDENCE.glob('*-register.receipt.json'):
        data = json.loads(receipt.read_text()).get('data') or {}
        if 'number' in data:
            owned_stacks.add(data['number'])
    if method == 'POST' and path == BASE + '/pulls':
        if not payload['head'].startswith(PREFIX) or not payload['base'].startswith(PREFIX):
            raise ValueError('PR ref outside allocation')
        return
    if method == 'POST' and path == BASE + '/stacks':
        if not set(payload['pull_requests']).issubset(owned_prs):
            raise ValueError('Unowned registration member')
        return
    match = re.fullmatch(re.escape(BASE) + r'/pulls/(\d+)', path)
    if method == 'PATCH' and match and int(match[1]) in owned_prs:
        if set(payload) != {'base'} or not payload['base'].startswith(PREFIX):
            raise ValueError('Unowned metadata mutation')
        return
    match = re.fullmatch(re.escape(BASE) + r'/stacks/(\d+)/unstack', path)
    if method == 'POST' and match and int(match[1]) in owned_stacks:
        return
    raise ValueError('Mutation outside structural allocation: ' + method + ' ' + path)


def api(label, method, path, payload=None):
    check_write(method, path, payload)
    receipt = label_path(label, '.receipt.json')
    if receipt.exists():
        record = json.loads(receipt.read_text())
        if (record['method'], record['path'], record['payload']) != (method, path, payload):
            raise RuntimeError('Receipt does not match intent')
        return record
    intent = label_path(label, '.intent.json')
    if intent.exists():
        raise RuntimeError('Unreceipted dispatch; no replay: ' + label)
    record = {'label': label, 'method': method, 'path': path, 'payload': payload,
              'started_at': now(), 'api_version': '2026-03-10'}
    save(intent, record)
    args = ['gh', 'api', '--include', '-H', 'X-GitHub-Api-Version: 2026-03-10', '-X', method, path]
    if payload is not None:
        request = label_path(label, '.request.json')
        save(request, payload)
        args += ['--input', str(request)]
    result = command(args)
    label_path(label, '.response.txt').write_text(result.stdout)
    label_path(label, '.stderr.txt').write_text(result.stderr)
    match = re.search(r'^HTTP/\S+\s+(\d+)', result.stdout)
    record.update(finished_at=now(), exit=result.returncode,
                  http=int(match[1]) if match else None)
    parts = re.split(r'\r?\n\r?\n', result.stdout, maxsplit=1)
    try:
        record['data'] = json.loads(parts[1]) if len(parts) > 1 and parts[1].strip() else None
    except json.JSONDecodeError:
        record['data'] = None
    save(receipt, record)
    if method != 'GET':
        time.sleep(2)
    if record['http'] is None:
        raise RuntimeError('Unknown network outcome; no retry: ' + label)
    return record


def read(label, path):
    generation = 0
    while label_path(label + '-r' + str(generation), '.intent.json').exists():
        generation += 1
    return api(label + '-r' + str(generation), 'GET', path)


def require(record, statuses):
    if record['http'] not in statuses:
        raise RuntimeError(json.dumps({'label': record['label'], 'http': record['http'],
                                       'data': record['data']}))
    return record


def push(label, updates, expected):
    for ref in updates:
        if not ref.startswith(('refs/heads/' + PREFIX, 'refs/tags/' + PREFIX)):
            raise ValueError('Push outside structural allocation')
    receipt = label_path(label, '.receipt.json')
    if receipt.exists():
        old = json.loads(receipt.read_text())
        if old['updates'] != updates or old['expected'] != expected:
            raise RuntimeError('Push receipt does not match intent')
        return old
    intent = label_path(label, '.intent.json')
    if intent.exists():
        raise RuntimeError('Unreceipted push; no replay: ' + label)
    args = ['push', '--atomic']
    for ref in updates:
        args += ['--force-with-lease=' + ref + ':' + expected.get(ref, '')]
    args += ['origin'] + [sha + ':' + ref for ref, sha in updates.items()]
    record = {'label': label, 'started_at': now(), 'updates': updates,
              'expected': expected, 'args': args}
    save(intent, record)
    result = git(*args, check=False)
    record.update(finished_at=now(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    save(receipt, record)
    time.sleep(2)
    if result.returncode:
        raise RuntimeError('Push rejected or uncertain; no replay: ' + label)
    return record


def commit(label, parent, files):
    path = label_path(label, '.commit.json')
    if path.exists():
        return json.loads(path.read_text())['sha']
    index = HOME / (label + '.index')
    environment = dict(os.environ, GIT_INDEX_FILE=str(index))
    git('read-tree', parent, env=environment)
    for name, content in files.items():
        blob = git('hash-object', '-w', '--stdin', text=content)
        git('update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + name, env=environment)
    tree = git('write-tree', env=environment)
    message = ('Record structural fixture ' + label + '\n\n'
               "Agent-authored-by: AI agent acting on joshlf's behalf\n")
    sha = git('commit-tree', tree, '-p', parent, text=message)
    git('update-ref', 'refs/experiment-inputs/' + label, sha)
    save(path, {'sha': sha, 'tree': tree, 'parent': parent, 'files': files, 'message': message})
    return sha


def refs(fixture):
    raw = git('ls-remote', 'origin', 'refs/heads/' + fixture['prefix'] + '/*',
              'refs/tags/' + fixture['prefix'] + '/*')
    return dict((ref, sha) for sha, ref in (line.split('\t') for line in raw.splitlines()))


def snapshot(fixture, label, extra_prs=None):
    current = {'at': now(), 'prs': {}, 'refs': refs(fixture)}
    for letter, number in {**fixture['prs'], **(extra_prs or {})}.items():
        record = require(read(label + '-pr-' + letter, BASE + '/pulls/' + str(number)), [200])
        value = record['data']
        current['prs'][letter] = {key: value.get(key) for key in ['number', 'node_id', 'state', 'merged', 'merged_at', 'stack']}
        current['prs'][letter].update(head_ref=value['head']['ref'], head_sha=value['head']['sha'],
                                      base_ref=value['base']['ref'], base_sha=value['base']['sha'])
    save(label_path(label, '.snapshot.json'), current)
    return current
