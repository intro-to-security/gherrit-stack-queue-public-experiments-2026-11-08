"""Stage lossless public copies of completed synthetic experiment evidence."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import tarfile


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'publication/repo/followup-2026-11-08'
EXTENSIONS = {'.md', '.py', '.json', '.jsonl', '.yml', '.yaml', '.txt',
              '.stdout', '.stderr', '.patch', '.diff', '.trace', '.csv'}
SKIP_DIRS = {'.git', 'git', 'repo', '__pycache__', 'bin'}
SECRET_PATTERNS = [re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),
                   re.compile(rb'github_pat_[A-Za-z0-9_]{20,}'),
                   re.compile(rb'Authorization: Bearer [A-Za-z0-9_=.-]{20,}')]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inputs(lane):
    source = ROOT / lane
    for folder, dirs, names in os.walk(source, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS
                         and not d.endswith(('-repo', '-sink', '.bare')))
        for name in sorted(names):
            path = Path(folder) / name
            if path.is_symlink():
                continue
            if path.suffix not in EXTENSIONS and name not in {'LICENSE', 'COPYING', 'NOTICE'}:
                continue
            if path.stat().st_size > 10 * 1024 * 1024:
                raise ValueError(f'Needs explicit large-file review: {path.relative_to(ROOT)}')
            data = path.read_bytes()
            try:
                data.decode('utf-8')
            except UnicodeDecodeError:
                continue
            if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                raise ValueError(f'Possible credential; do not publish: {path.relative_to(ROOT)}')
            yield path, data


def prepare(lane):
    target = DEST / lane
    target.mkdir(parents=True, exist_ok=True)
    archive = target / 'evidence.tar.gz'
    temporary = target / 'evidence.tar.gz.partial'
    manifest = []
    with temporary.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=6, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as tar:
                for path, data in inputs(lane):
                    before = path.stat()
                    relative = path.relative_to(ROOT / lane).as_posix()
                    info = tarfile.TarInfo(relative)
                    info.size = len(data)
                    info.mode = before.st_mode & 0o777
                    info.mtime = int(before.st_mtime)
                    # Keep content, executable modes and evidence timestamps;
                    # filesystem account identities are not needed for replay.
                    from io import BytesIO
                    tar.addfile(info, BytesIO(data))
                    after = path.stat()
                    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                        raise RuntimeError(f'Source changed while staging: {path}')
                    manifest.append({'path': relative, 'bytes': len(data),
                                     'sha256': digest(data), 'mode': info.mode,
                                     'mtime_seconds': info.mtime})
    by_path = {entry['path']: entry for entry in manifest}
    checked = set()
    with tarfile.open(temporary, 'r:gz') as tar:
        for member in tar:
            if not member.isfile() or member.name.startswith('/') or '..' in Path(member.name).parts:
                raise RuntimeError('Unexpected archive entry')
            stream = tar.extractfile(member)
            if stream is None:
                raise RuntimeError('Missing archive contents')
            data = stream.read()
            entry = by_path[member.name]
            if (digest(data), member.mode, member.mtime) != (entry['sha256'], entry['mode'], entry['mtime_seconds']):
                raise RuntimeError(f'Archive verification failed: {member.name}')
            checked.add(member.name)
    if checked != set(by_path):
        raise RuntimeError('Archive inventory mismatch')
    os.replace(temporary, archive)
    for path in sorted((ROOT / lane).iterdir()):
        if path.is_file() and path.suffix in EXTENSIONS:
            data = path.read_bytes()
            if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                raise ValueError(f'Possible credential in top-level file: {path.name}')
            shutil.copy2(path, target / path.name)
    index = {'lane': lane, 'files': manifest, 'file_count': len(manifest),
             'expanded_bytes': sum(x['bytes'] for x in manifest),
             'archive_bytes': archive.stat().st_size,
             'archive_sha256': digest(archive.read_bytes()), 'verified': True,
             'scope': 'UTF-8 source/reports/evidence only; local Git databases, executables, working trees and nontext payloads are retained locally, not removed',
             'restore': 'In a new empty directory: tar -xzf /path/to/evidence.tar.gz; verify every entry against SOURCE-INDEX.json before use.'}
    (target / 'SOURCE-INDEX.json').write_text(json.dumps(index, indent=2) + '\n')
    print(json.dumps({k: v for k, v in index.items() if k != 'files'}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('lanes', nargs='+', choices=['queue', 'local', 'ci-reviews', 'protocol', 'structure', 'ui'])
    args = parser.parse_args()
    for lane in args.lanes:
        prepare(lane)
