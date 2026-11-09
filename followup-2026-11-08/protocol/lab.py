"""Recorded synthetic GitHub operations; unknown effects are never retried."""
from pathlib import Path
import datetime
import hashlib
import http.client
import json
import os
import re
import socket
import ssl
import subprocess
import time
import urllib.parse

HOME = Path(__file__).resolve().parent
EVIDENCE = HOME / 'evidence'
GIT = HOME / 'git'
STATE = HOME / 'resources.json'
REPO = 'joshlf/gherrit-native-stack-experiments-2026-11-08'
PREFIX = 'exp/fu2/protocol/'
BASE = '/repos/' + REPO
NOTICE = "*Authored by an AI agent acting on joshlf's behalf.*"
TOKEN = None


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


def command(args, *, cwd=None, text=None, env=None):
    return subprocess.run(args, cwd=cwd, input=text, env=env,
                          capture_output=True, text=True)


def token():
    global TOKEN
    if TOKEN is None:
        result = command(['gh', 'auth', 'token'])
        if result.returncode:
            raise RuntimeError('Could not obtain authentication in process memory')
        TOKEN = result.stdout.strip()
        if not TOKEN or '\n' in TOKEN or '\r' in TOKEN:
            raise RuntimeError('Invalid authentication token shape')
    return TOKEN


def safe(label):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', label):
        raise ValueError('Unsafe evidence label')
    return label


def evidence_path(label, suffix):
    return EVIDENCE / (safe(label) + suffix)


def request_intent(label, method, path, payload):
    if not path.startswith(BASE + '/') and path != BASE:
        raise ValueError('Outside the synthetic repository')
    record = {'label': label, 'method': method, 'path': path,
              'payload': payload, 'started_at': now(),
              'monotonic_start': time.monotonic(), 'api_version': '2026-03-10'}
    target = evidence_path(label, '.intent.json')
    if target.exists():
        raise RuntimeError('Existing dispatch intent; reconcile without retry: ' + label)
    save(target, record)
    return record


def api(label, method, path, payload=None):
    receipt = evidence_path(label, '.receipt.json')
    if receipt.exists():
        value = json.loads(receipt.read_text())
        if (value['method'], value['path'], value['payload']) != (method, path, payload):
            raise RuntimeError('Receipt conflicts with planned request')
        if method not in ('GET', 'HEAD') and value['http'] >= 500:
            raise RuntimeError('Server-error write remains unknown; do not replay: ' + label)
        return value
    record = request_intent(label, method, path, payload)
    headers = {'Accept': 'application/vnd.github+json',
               'Authorization': 'Bearer ' + token(),
               'X-GitHub-Api-Version': '2026-03-10',
               'User-Agent': 'gherrit-synthetic-protocol-experiment'}
    body = None if payload is None else json.dumps(payload).encode()
    if body is not None:
        headers['Content-Type'] = 'application/json'
    connection = http.client.HTTPSConnection('api.github.com', timeout=30)
    try:
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw = response.read()
        record.update(http=response.status, response_headers=dict(response.getheaders()),
                      response_body=raw.decode('utf-8', errors='replace'))
        try:
            record['data'] = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            record['data'] = None
    except Exception as error:
        save(evidence_path(label, '.unknown.json'),
             {**record, 'at': now(), 'error_type': type(error).__name__,
              'decision': 'unknown; no retry; reconcile separately'})
        raise RuntimeError('Unknown request outcome: ' + label) from None
    finally:
        connection.close()
    record.update(finished_at=now(), monotonic_end=time.monotonic())
    save(receipt, record)
    if method not in ('GET', 'HEAD') and record['http'] >= 500:
        save(evidence_path(label, '.unknown.json'),
             {**record, 'decision': 'Server error does not settle effects; no retry or overlap'})
        raise RuntimeError('Server-error write remains unknown; stop driver: ' + label)
    if method not in ('GET', 'HEAD'):
        time.sleep(2)
    if record['http'] in (403, 429) and ('rate limit' in record['response_body'].lower()
                                        or 'retry-after' in record['response_headers']):
        raise RuntimeError('Rate limit stopped driver; no retry: ' + label)
    return record


def read(label, path):
    generation = 1
    original = label
    while evidence_path(label, '.intent.json').exists():
        generation += 1
        label = original + '-sample-' + str(generation)
    return api(label, 'GET', path)


def lost_send(label, method, path, payload=None, *, incomplete=False, hold_ms=0):
    outcome = evidence_path(label, '.transport.json')
    if outcome.exists() or evidence_path(label, '.intent.json').exists():
        raise RuntimeError('Never repeat an uncertain dispatch: ' + label)
    record = request_intent(label, method, path, payload)
    body = b'' if payload is None else json.dumps(payload).encode()
    public_headers = {'Host': 'api.github.com', 'Accept': 'application/vnd.github+json',
                      'X-GitHub-Api-Version': '2026-03-10',
                      'User-Agent': 'gherrit-synthetic-protocol-experiment',
                      'Content-Type': 'application/json',
                      'Content-Length': str(len(body)), 'Connection': 'close'}
    header_lines = [method + ' ' + path + ' HTTP/1.1']
    header_lines += [key + ': ' + value for key, value in public_headers.items()]
    header_lines += ['Authorization: Bearer ' + token(), '', '']
    wire = '\r\n'.join(header_lines).encode() + body
    dispatched = wire[:-1] if incomplete else wire
    save(evidence_path(label, '.wire-description.json'),
         {'headers_without_credentials': public_headers,
          'body_sha256': hashlib.sha256(body).hexdigest(),
          'complete_request_bytes': len(wire),
          'planned_send_bytes': len(dispatched),
          'incomplete_by_bytes': len(wire) - len(dispatched),
          'http_receive_calls_planned': 0, 'post_send_hold_ms': hold_ms})
    sent = 0
    chunks = []
    context = ssl.create_default_context()
    connected = None
    try:
        raw_socket = socket.create_connection(('api.github.com', 443), timeout=20)
        connected = context.wrap_socket(raw_socket, server_hostname='api.github.com')
        record.update(tls_version=connected.version(), cipher=connected.cipher(),
                      peer=connected.getpeername(), tls_ready_at=now())
        while sent < len(dispatched):
            before = time.monotonic()
            amount = connected.send(memoryview(dispatched)[sent:])
            if amount <= 0:
                raise RuntimeError('TLS send made no progress')
            sent += amount
            chunks.append({'bytes': amount, 'start': before, 'end': time.monotonic()})
        record.update(send_completed_at=now(), send_completed_monotonic=time.monotonic())
        if hold_ms:
            time.sleep(hold_ms / 1000)
    except Exception as error:
        record['transport_error_type'] = type(error).__name__
    finally:
        if connected is not None:
            connected.close()
        record.update(closed_at=now(), closed_monotonic=time.monotonic(),
                      tls_bytes_send_returned=sent, expected_send_bytes=len(dispatched),
                      send_chunks=chunks, post_send_hold_ms=hold_ms,
                      http_receive_calls=0, server_http_status=None,
                      limit='Local TLS send counts do not prove server receipt/execution')
        save(outcome, record)
    decision = {'label': label, 'at': now(), 'monotonic': time.monotonic(),
                'client_knowledge': 'No HTTP response read; effect unknown',
                'decision': 'retain unknown; do not resend or overlap this fixture',
                'resent': False, 'oracle_read_started': False}
    save(evidence_path(label, '.recovery-before-oracle.json'), decision)
    return record


def git(*args, text=None, env=None):
    result = command(['git', '-C', str(GIT), *args], text=text, env=env)
    if result.returncode:
        raise RuntimeError('Git operation failed: ' + ' '.join(args) + '\n' + result.stderr)
    return result.stdout.strip()


def initialize():
    EVIDENCE.mkdir(exist_ok=True)
    if not (GIT / '.git').exists():
        result = command(['git', 'clone', '--single-branch', '--branch', 'main',
                          'https://github.com/' + REPO + '.git', str(GIT)])
        save(EVIDENCE / 'clone.json', {'exit': result.returncode,
                                      'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            raise RuntimeError('Synthetic clone failed')
    git('config', 'core.hooksPath', str(HOME / 'empty-hooks'))
    git('config', 'user.name', 'Josh Liebow-Feeser')
    git('config', 'user.email', 'hello@joshlf.com')
    return git('rev-parse', 'refs/remotes/origin/main')


def commit(label, parent, files, *, empty_tree=False):
    path = evidence_path(label, '.commit.json')
    if path.exists():
        return json.loads(path.read_text())['sha']
    index = HOME / (safe(label) + '.index')
    environment = dict(os.environ, GIT_INDEX_FILE=str(index))
    git('read-tree', '--empty', env=environment) if empty_tree else git('read-tree', parent, env=environment)
    for path_name, value in files.items():
        if path_name.startswith('/') or '..' in Path(path_name).parts:
            raise ValueError('Unsafe fixture path')
        blob = git('hash-object', '-w', '--stdin', text=value)
        git('update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + path_name,
            env=environment)
    tree = git('write-tree', env=environment)
    message = 'Record synthetic protocol fixture ' + label + '\n\n' + \
        "Agent-authored-by: AI agent acting on joshlf's behalf\n"
    sha = git('commit-tree', tree, '-p', parent, text=message)
    git('update-ref', 'refs/experiment-inputs/' + label, sha)
    save(path, {'sha': sha, 'tree': tree, 'parent': parent, 'files': files,
                'message': message, 'workflow_free_tree': empty_tree})
    return sha


def push(label, updates, expected=None):
    receipt = evidence_path(label, '.push.json')
    if receipt.exists():
        return json.loads(receipt.read_text())
    intent = evidence_path(label, '.push-intent.json')
    if intent.exists():
        raise RuntimeError('Unresolved push; do not retry: ' + label)
    expected = expected or {}
    for ref in updates:
        if not ref.startswith(('refs/heads/' + PREFIX, 'refs/tags/' + PREFIX)):
            raise ValueError('Outside allocated refs')
    args = ['push', '--atomic']
    args += ['--force-with-lease=' + ref + ':' + expected.get(ref, '') for ref in updates]
    args += ['origin'] + [sha + ':' + ref for ref, sha in updates.items()]
    record = {'at': now(), 'updates': updates, 'expected': expected, 'args': args}
    save(intent, record)
    result = command(['git', '-C', str(GIT), *args])
    record.update(exit=result.returncode, stdout=result.stdout,
                  stderr=result.stderr, ended_at=now())
    save(receipt, record)
    if result.returncode:
        raise RuntimeError('Push failed; retain and reconcile: ' + label)
    time.sleep(2)
    return record


def resources():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def store_fixture(case):
    state = resources()
    state[case['name']] = case
    save(STATE, state)


def fixture(name, count=2, *, create_prs=True):
    case = resources().get(name)
    if case is None:
        seed = initialize()
        prefix = PREFIX + name
        trunk = prefix + '/trunk'
        trunk_sha = commit(name + '-trunk', seed, {'fixture.txt': name + '\n'}, empty_tree=True)
        heads = []
        parent = trunk_sha
        updates = {'refs/heads/' + trunk: trunk_sha}
        for number in range(1, count + 1):
            letter = str(number).zfill(3)
            sha = commit(name + '-' + letter, parent,
                         {'layers/' + letter + '.txt': name + ':' + letter + '\n'})
            ref = prefix + '/' + letter
            heads.append({'ref': ref, 'sha': sha})
            updates['refs/heads/' + ref] = sha
            updates['refs/tags/' + prefix + '/authored/' + letter] = sha
            parent = sha
        push(name + '-initial', updates)
        case = {'name': name, 'prefix': prefix, 'trunk': trunk,
                'trunk_sha': trunk_sha, 'heads': heads, 'prs': [],
                'workflow_files': git('ls-tree', '-r', '--name-only', trunk_sha, '.github/workflows')}
        store_fixture(case)
    if create_prs:
        previous = case['trunk']
        for index, head in enumerate(case['heads']):
            if index >= len(case['prs']):
                result = api(name + '-pr-' + str(index + 1).zfill(3), 'POST', BASE + '/pulls',
                             pr_payload(case, index, previous))
                if result['http'] != 201:
                    raise RuntimeError('PR fixture creation rejected; do not retry: ' + name)
                case['prs'].append(result['data']['number'])
                store_fixture(case)
            previous = head['ref']
    return case


def pr_payload(case, index, base=None):
    return {'head': case['heads'][index]['ref'],
            'base': base or (case['trunk'] if index == 0 else case['heads'][index - 1]['ref']),
            'title': 'Synthetic protocol ' + case['name'] + ' layer ' + str(index + 1),
            'body': 'Synthetic protocol fixture ' + case['name'] + ':' + str(index + 1) + '\n\n' + NOTICE}


def register(case, label=None, numbers=None):
    result = api(label or case['name'] + '-register', 'POST', BASE + '/stacks',
                 {'pull_requests': numbers if numbers is not None else case['prs']})
    if result['http'] != 201:
        raise RuntimeError('Expected stack registration rejected: ' + str(result['http']))
    return result['data']['number']


def summary(record):
    data = record.get('data')
    return {'http': record['http'], 'data': data,
            'receipt': str(evidence_path(record['label'], '.receipt.json').relative_to(HOME))}


def observe(case, label, *, stack=None, include_refs=False):
    value = {'at': now(), 'monotonic_start': time.monotonic(), 'prs': []}
    for number in case['prs']:
        response = read(label + '-pr-' + str(number), BASE + '/pulls/' + str(number))
        data = response.get('data') or {}
        value['prs'].append({'number': number, 'http': response['http'],
                             'state': data.get('state'), 'merged': data.get('merged'),
                             'head': data.get('head'), 'base': data.get('base'),
                             'stack': data.get('stack'), 'merged_at': data.get('merged_at')})
    if stack is not None:
        value['stack'] = summary(read(label + '-stack', BASE + '/stacks/' + str(stack)))
    if include_refs:
        value['refs'] = git('ls-remote', 'origin', 'refs/heads/' + case['prefix'] + '/*')
    value['monotonic_end'] = time.monotonic()
    save(evidence_path(label, '.observation.json'), value)
    return value
