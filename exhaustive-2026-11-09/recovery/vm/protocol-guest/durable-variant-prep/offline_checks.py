import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('durable_refs', ROOT / 'durable_refs.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
CASE = Path('/state/scope/case-after_return')
OLD, NEW = '1' * 40, '2' * 40
INTENT = dict(id='op-case-after_return', continuation='refs/retained/completed-case-after_return',
              provider=str(CASE / 'provider'), input=OLD, expected=OLD, result=NEW)


class MemoryOS:
    def __init__(self):
        self.nodes, self.fds, self.synced = {}, {}, []
        self.next_fd, self.fail_sync = 10, None
        for repo in (CASE / 'repo', CASE / 'provider/repo'):
            self.mkdir(repo / '.git/refs/heads')
            self.mkdir(repo / '.git/refs/retained')
        self.put(CASE / 'provider/repo/.git/refs/heads/A', (OLD + '\n').encode())

    def mkdir(self, path):
        for part in (Path('/'), *reversed(path.parents), path):
            if part not in self.nodes:
                self.nodes[part] = dict(st_mode=stat.S_IFDIR | 0o700, st_nlink=1,
                    st_uid=1000, st_dev=1, st_ino=len(self.nodes)+1, data=b'')

    def put(self, path, data):
        self.mkdir(path.parent)
        self.nodes[path] = dict(st_mode=stat.S_IFREG | 0o600, st_nlink=1,
            st_uid=1000, st_dev=1, st_ino=len(self.nodes)+100, data=data)

    def path(self, name, dir_fd):
        return Path(name) if dir_fd is None else self.fds[dir_fd][0] / name

    def info(self, path):
        if path not in self.nodes:
            raise FileNotFoundError(str(path))
        node = self.nodes[path]
        return SimpleNamespace(**{k:v for k,v in node.items() if k != 'data'}, st_size=len(node['data']))

    def open(self, name, flags, dir_fd=None):
        path = self.path(name, dir_fd)
        info = self.info(path)
        if flags & os.O_NOFOLLOW and stat.S_ISLNK(info.st_mode):
            raise OSError(errno.ELOOP, 'symlink')
        if flags & os.O_DIRECTORY and not stat.S_ISDIR(info.st_mode):
            raise NotADirectoryError(str(path))
        fd = self.next_fd
        self.next_fd += 1
        self.fds[fd] = [path, 0]
        return fd

    def fstat(self, fd):
        return self.info(self.fds[fd][0])

    def stat(self, name, dir_fd=None, follow_symlinks=False):
        return self.info(self.path(name, dir_fd))

    def read(self, fd, size):
        path, offset = self.fds[fd]
        data = self.nodes[path]['data'][offset:offset+size]
        self.fds[fd][1] += len(data)
        return data

    def fsync(self, fd):
        path = self.fds[fd][0]
        if path == self.fail_sync:
            raise OSError(errno.EIO, 'injected fsync failure')
        self.synced.append(str(path))

    def close(self, fd):
        del self.fds[fd]

    def geteuid(self):
        return 1000


def fixture(mode='success', module=d):
    ops = MemoryOS()
    calls, reports = [], []
    result = SimpleNamespace(returncode=0)
    class Git:
        def __init__(self, root):
            self.root = Path(root)
        def run(self, *args, **kwargs):
            calls.append((args, kwargs))
            if mode == 'raise':
                raise RuntimeError('command failure or unknown effect')
            if mode == 'nonzero':
                return SimpleNamespace(returncode=1)
            if args and args[0] == 'update-ref':
                ops.put(self.root / '.git' / args[1], (args[2] + '\n').encode())
            return result
    protocol = SimpleNamespace(Git=Git, ENV={})
    module.install(protocol, CASE, INTENT, files=module.LooseFiles(ops), report=reports.append)
    return ops, calls, reports, protocol, result


def required(repo, ref):
    target = Path(repo) / '.git' / ref
    return [str(target), *[str(path) for path in target.parents if path == CASE or CASE in path.parents]]


def rejects(thunk, code=None):
    try:
        thunk()
    except (d.DurableRefError, RuntimeError) as error:
        if code is not None:
            assert code in str(error), (code, str(error))
        return str(error)
    raise AssertionError('known violation was accepted')


def run():
    results = []
    for (repo, ref), (new, old, role) in d.scoped_plans(CASE, INTENT).items():
        ops, calls, reports, p, result = fixture()
        assert p.Git(repo).run('update-ref', ref, new, old) is result
        expected = required(repo, ref)
        assert ops.synced == expected, (ops.synced, expected)
        assert reports[0]['synchronized'] == expected
        assert len(calls) == len(reports) == 1 and not ops.fds
        results.append(dict(case=role, expected_sync_order=expected))
    source = (ROOT/'durable_refs.py').read_text()
    mutations = {'missing_file_sync': ('self.ops.fsync(descriptor)', 'pass'),
                 'missing_new_parent_link_sync': ('self.ops.fsync(fd)', 'if path.name != "refs": self.ops.fsync(fd)'),
                 'missing_case_anchor_sync': ('self.ops.fsync(fd)', 'if path != case: self.ops.fsync(fd)')}
    for name, (before, after) in mutations.items():
        assert source.count(before) == 1
        mutated = source.replace(before,after)
        module = SimpleNamespace(__name__='known_bad_'+name)
        exec(compile(mutated,'<known_bad_'+name+'>','exec'),module.__dict__)
        ops, calls, reports, p, _ = fixture(module=module)
        repo = str(CASE/'provider/repo')
        ref = 'refs/archives/' + INTENT['id']
        p.Git(repo).run('update-ref',ref,NEW,'0'*40)
        expected = required(repo,ref)
        assert reports[0]['synchronized'] == expected
        assert ops.synced != expected, 'known-bad barrier omission escaped observed-call oracle'
        assert len(calls) == 1 and not ops.fds
        results.append(dict(case=name, mutated_source_sha256=hashlib.sha256(mutated.encode()).hexdigest(),
            falsely_reported_complete=True, rejected_by_observed_calls=True, observed=ops.synced, required=expected))
    repo, ref = str(CASE/'provider/repo'), 'refs/heads/A'
    for mode in ('raise', 'nonzero'):
        ops, calls, reports, p, _ = fixture(mode)
        rejects(lambda:p.Git(repo).run('update-ref', ref, NEW, OLD))
        assert len(calls) == 1 and not ops.synced and not reports and not ops.fds
        results.append(dict(case='failed_command_'+mode, dispatched_once=True, barriers=0))
    for path in (Path(repo)/'.git'/ref, Path(repo)/'.git/refs/heads', CASE):
        ops, calls, reports, p, _ = fixture()
        ops.fail_sync = path
        rejects(lambda:p.Git(repo).run('update-ref', ref, NEW, OLD), 'ref_barrier_io_error')
        assert len(calls) == 1 and not reports and not ops.fds
        results.append(dict(case='fsync_failure', at=str(path), acknowledgement_suppressed=True))
    mutations = {
        'leaf_symlink': lambda o:o.nodes[Path(repo)/'.git'/ref].update(st_mode=stat.S_IFLNK|0o777),
        'parent_symlink': lambda o:o.nodes[Path(repo)/'.git/refs/heads'].update(st_mode=stat.S_IFLNK|0o777),
        'hardlink': lambda o:o.nodes[Path(repo)/'.git'/ref].update(st_nlink=2),
        'foreign_owner': lambda o:o.nodes[Path(repo)/'.git'/ref].update(st_uid=1001),
        'foreign_device': lambda o:o.nodes[Path(repo)/'.git/refs'].update(st_dev=2),
        'symbolic_ref': lambda o:o.nodes[Path(repo)/'.git'/ref].update(data=b'ref: refs/heads/B\n'),
        'wrong_sha': lambda o:o.nodes[Path(repo)/'.git'/ref].update(data=(NEW+'\n').encode()),
        'trailing_bytes': lambda o:o.nodes[Path(repo)/'.git'/ref].update(data=(OLD+'\n\n').encode()),
        'packed_refs': lambda o:o.put(Path(repo)/'.git/packed-refs', b''),
        'commondir': lambda o:o.put(Path(repo)/'.git/commondir', b'other\n')}
    for name, mutate in mutations.items():
        ops, calls, reports, p, _ = fixture()
        mutate(ops)
        rejects(lambda:p.Git(repo).run('update-ref', ref, NEW, OLD))
        assert not calls and not ops.synced and not reports and not ops.fds
        results.append(dict(case=name, rejected_before_dispatch=True))
    for args, kwargs in [ (('update-ref',ref,NEW,NEW),{}), (('update-ref','refs/heads/B',NEW,OLD),{}),
                          (('update-ref','--stdin'),{}), (('update-ref',ref,NEW,OLD),{'allowed':(0,1)}),
                          (('update-ref',ref,NEW,OLD),{'env':{}}), (('update-ref',ref,NEW,OLD),{'stdin':''}) ]:
        ops, calls, reports, p, _ = fixture()
        rejects(lambda:p.Git(repo).run(*args,**kwargs))
        assert not calls and not ops.synced and not reports
    ops,calls,reports,p,result = fixture()
    assert p.Git(repo).run('rev-parse','--verify',ref) is result
    assert len(calls) == 1 and not ops.synced and not reports
    results.append(dict(case='unsupported_forms_and_read_passthrough', scope_rejections=6))
    rejects(lambda:d.install(p,CASE,INTENT), 'wrapper_already_installed')
    for key in ('GIT_DIR','GIT_COMMON_DIR','GIT_NAMESPACE','GIT_WORK_TREE','GIT_CONFIG_COUNT','GIT_CONFIG_PARAMETERS'):
        class Git:
            run = lambda *a,**kw:None
        rejects(lambda:d.install(SimpleNamespace(Git=Git,ENV={key:'x'}),CASE,INTENT),'environment_redirect')
    rejects(lambda:d.scoped_plans(CASE,dict(INTENT,continuation='refs/heads/main')),'frozen_scope_mismatch')
    rejects(lambda:d.scoped_plans(Path('/tmp/case-after_return'),INTENT),'outside_owned_case')
    for name, expected in json.loads((ROOT/'ORIGINAL-PINS.json').read_text()).items():
        assert hashlib.sha256((ROOT/'original'/name).read_bytes()).hexdigest() == expected
    for path in ROOT.rglob('*.py'):
        compile(path.read_bytes(), str(path), 'exec')
    return dict(pass_=True, cases=results, limits='MemoryOS only; no Git, runtime, container, network, or durability experiment executed')


if __name__ == '__main__':
    def forbidden(*args, **kwargs):
        raise AssertionError('offline checks attempted an external effect')
    subprocess.Popen = forbidden
    socket.socket = forbidden
    os.sync = forbidden
    record = run()
    target = ROOT/'OFFLINE-CHECKS.json'
    if target.exists():
        raise RuntimeError('retain existing offline checks; use a new record name')
    target.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(pass_=True, recorded_cases=len(record['cases']), external_effects='blocked')))
