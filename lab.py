"""Recorded, lane-scoped operations for one authorized synthetic repository.

Acknowledged mutations are reused only when their request still matches. An
intent without a receipt stops execution instead of authorizing a retry.
"""
from pathlib import Path
import datetime, json, os, re, subprocess, time

ROOT = Path(__file__).resolve().parent
REPO = 'intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08'
NOTICE = "*Authored by an AI agent acting on joshlf's behalf.*"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temporary, path)


def command(args, **kwargs):
    return subprocess.run(args, capture_output=True, text=True, **kwargs)


class Lane:
    def __init__(self, name):
        assert name in ('native', 'ci', 'locks', 'control', 'edit')
        self.name = name
        self.home = ROOT / name
        self.evidence = self.home / 'evidence'
        self.evidence.mkdir(parents=True, exist_ok=True)
        self.gitdir = self.home / 'git'
        self.state_path = self.home / 'fixtures.json'

    def api(self, label, method, path, payload=None, *, fresh=False):
        assert re.fullmatch(r'[a-zA-Z0-9_.-]+', label)
        assert path == 'repos/' + REPO or path.startswith('repos/' + REPO + '/') or path == 'graphql'
        if fresh:
            original, n = label, 1
            while (self.evidence / (label + '.intent.json')).exists():
                n += 1
                label = original + '-read-' + str(n)
        prefix = self.evidence / label
        receipt = Path(str(prefix) + '.receipt.json')
        identity = {'method': method, 'path': path, 'payload': payload}
        if receipt.exists() and not fresh:
            previous = json.loads(receipt.read_text())
            assert all(previous[k] == v for k, v in identity.items()), 'Receipt belongs to another intent'
            return previous
        intent = Path(str(prefix) + '.intent.json')
        if intent.exists():
            raise RuntimeError('Unresolved prior dispatch: ' + label)
        record = dict(identity, label=label, start=now(), monotonic_start=time.monotonic())
        save(intent, record)
        args = ['gh', 'api', '--include', '-H', 'X-GitHub-Api-Version: 2026-03-10', '-X', method, path]
        if payload is not None:
            request = Path(str(prefix) + '.request.json')
            save(request, payload)
            args += ['--input', str(request)]
        result = command(args)
        Path(str(prefix) + '.response.txt').write_text(result.stdout)
        Path(str(prefix) + '.stderr.txt').write_text(result.stderr)
        status = re.search(r'^HTTP/\S+\s+(\d+)', result.stdout)
        parts = re.split(r'\r?\n\r?\n', result.stdout, maxsplit=1)
        record.update(end=now(), monotonic_end=time.monotonic(), exit=result.returncode,
                      http=int(status.group(1)) if status else None)
        try:
            record['data'] = json.loads(parts[1]) if len(parts) > 1 and parts[1].strip() else None
        except json.JSONDecodeError:
            record['data'] = None
            record['parse_error'] = True
        save(receipt, record)
        return record

    def graphql(self, label, query, variables=None, *, fresh=False):
        return self.api(label, 'POST', 'graphql', {'query': query, 'variables': variables or {}}, fresh=fresh)

    def git(self, *args, input=None, env=None, check=True):
        result = command(['git', '-C', str(self.gitdir), *args], input=input, env=env)
        if check and result.returncode:
            raise RuntimeError('Git failed: ' + repr(args) + '\n' + result.stderr)
        return result.stdout.strip() if check else result

    def init_git(self):
        if not (self.gitdir / '.git').exists():
            result = command(['git', 'clone', '--single-branch', '--branch', 'main',
                              'https://github.com/' + REPO + '.git', str(self.gitdir)])
            save(self.evidence / 'clone.json', {'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
            assert result.returncode == 0
            self.git('config', 'core.hooksPath', str(ROOT.parent / 'empty-hooks'))
            self.git('config', 'user.name', 'Josh Liebow-Feeser')
            self.git('config', 'user.email', 'hello@joshlf.com')
        assert self.git('remote', 'get-url', 'origin') == 'https://github.com/' + REPO + '.git'
        return self.git('rev-parse', 'refs/remotes/origin/main')

    def commit(self, label, parent, files):
        path = self.evidence / (label + '.commit.json')
        if path.exists():
            previous = json.loads(path.read_text())
            assert previous['parent'] == parent and previous['files'] == files
            return previous['sha']
        index = self.home / (label + '.index')
        env = dict(os.environ, GIT_INDEX_FILE=str(index))
        self.git('read-tree', parent, env=env)
        for name, contents in files.items():
            assert not name.startswith('/') and '..' not in Path(name).parts
            if contents is None:
                self.git('update-index', '--force-remove', '--', name, env=env)
            else:
                blob = self.git('hash-object', '-w', '--stdin', input=contents)
                self.git('update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + name, env=env)
        tree = self.git('write-tree', env=env)
        message = 'Record synthetic ' + label + "\n\nAgent-authored-by: AI agent acting on joshlf's behalf\n"
        sha = self.git('commit-tree', tree, '-p', parent, input=message)
        self.git('update-ref', 'refs/experiment-inputs/' + label, sha)
        save(path, {'sha': sha, 'tree': tree, 'parent': parent, 'files': files, 'message': message})
        return sha

    def push(self, label, updates, expected=None):
        receipt = self.evidence / (label + '.push.json')
        expected = expected or {}
        if receipt.exists():
            previous = json.loads(receipt.read_text())
            assert previous['updates'] == updates and previous['expected'] == expected
            return previous
        intent = self.evidence / (label + '.push-intent.json')
        if intent.exists():
            raise RuntimeError('Unresolved Git dispatch: ' + label)
        args = ['push', '--atomic']
        for ref in updates:
            assert ref.startswith(('refs/heads/exp/' + self.name + '/', 'refs/tags/exp/' + self.name + '/'))
            args += ['--force-with-lease=' + ref + ':' + expected.get(ref, '')]
        args += ['origin'] + [sha + ':' + ref for ref, sha in updates.items()]
        record = {'start': now(), 'updates': updates, 'expected': expected, 'args': args}
        save(intent, record)
        result = self.git(*args, check=False)
        record.update(end=now(), exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
        save(receipt, record)
        return record

    def get_fixture(self, name):
        return json.loads(self.state_path.read_text()).get(name) if self.state_path.exists() else None

    def save_fixture(self, case):
        all_cases = json.loads(self.state_path.read_text()) if self.state_path.exists() else {}
        all_cases[case['name']] = case
        save(self.state_path, all_cases)

    def fixture(self, name, count=2, *, native=True, files=None):
        assert re.fullmatch('[a-z0-9-]+', name) and 1 <= count <= 4
        case = self.get_fixture(name)
        if not case:
            seed = self.init_git()
            prefix = 'exp/' + self.name + '/' + name
            trunk = self.commit(name + '-trunk', seed, {name + '/base.txt': 'baseline=1\n'})
            parent, heads = trunk, {}
            updates = {'refs/heads/' + prefix + '/trunk': trunk}
            for letter in 'ABCD'[:count]:
                patch = dict((files or {}).get(letter, {}))
                patch[name + '/' + letter + '.txt'] = letter + '=1\n'
                sha = self.commit(name + '-' + letter, parent, patch)
                heads[letter] = {'ref': prefix + '/' + letter, 'sha': sha}
                updates['refs/heads/' + heads[letter]['ref']] = sha
                updates['refs/tags/' + prefix + '/authored/' + letter + '/v1'] = sha
                parent = sha
            pushed = self.push(name + '-initial', updates)
            assert pushed['exit'] == 0, pushed
            case = {'name': name, 'prefix': prefix, 'trunk': prefix + '/trunk', 'trunk_sha': trunk,
                    'heads': heads, 'prs': {}, 'created': now()}
            self.save_fixture(case)
        parent_ref = case['trunk']
        for letter, head in case['heads'].items():
            if letter not in case['prs']:
                result = self.api(name + '-create-' + letter, 'POST', 'repos/' + REPO + '/pulls',
                                  {'head': head['ref'], 'base': parent_ref,
                                   'title': 'Synthetic queue experiment ' + name + ': ' + letter,
                                   'body': 'Synthetic test data for native-stack queue research.\n\n' + NOTICE})
                assert result['http'] == 201, result
                case['prs'][letter] = result['data']['number']
                self.save_fixture(case)
            parent_ref = head['ref']
        if native and not case.get('stack'):
            result = self.api(name + '-register', 'POST', 'repos/' + REPO + '/stacks',
                              {'pull_requests': list(case['prs'].values())})
            assert result['http'] == 201, result
            case['stack'] = result['data']['number']
            self.save_fixture(case)
        return case

    def status(self, label, sha, state, context='experiment/queue-release'):
        return self.api(label, 'POST', 'repos/' + REPO + '/statuses/' + sha,
                        {'state': state, 'context': context, 'description': 'Synthetic experiment controller gate'})

    def snapshot(self, case, label):
        result = {'start': now(), 'prs': {}, 'stack': None}
        for letter, number in case['prs'].items():
            result['prs'][letter] = self.api(label + '-' + letter, 'GET',
                                            'repos/' + REPO + '/pulls/' + str(number), fresh=True)
        if case.get('stack'):
            result['stack'] = self.api(label + '-stack', 'GET',
                                       'repos/' + REPO + '/stacks/' + str(case['stack']), fresh=True)
        result['refs'] = self.git('ls-remote', 'origin', 'refs/heads/' + case['prefix'] + '/*',
                                  'refs/tags/' + case['prefix'] + '/*', 'refs/heads/gh-readonly-queue/*')
        result['end'] = now()
        target = self.evidence / (label + '.snapshot.json')
        assert not target.exists(), 'Preserve previous snapshot'
        save(target, result)
        return result
