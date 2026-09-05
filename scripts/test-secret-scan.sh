#!/usr/bin/env bash
set -euo pipefail

resolve_script_dir() {
  local source_path="${BASH_SOURCE[0]}"
  while [ -L "$source_path" ]; do
    local dir
    dir="$(cd -P "$(dirname "$source_path")" && pwd)"
    source_path="$(readlink "$source_path")"
    case "$source_path" in /*) ;; *) source_path="$dir/$source_path" ;; esac
  done
  cd -P "$(dirname "$source_path")" && pwd
}
SCRIPT_DIR="$(resolve_script_dir)"
python3 - "$SCRIPT_DIR/secret-scan.py" <<'PY'
import os
from pathlib import Path
import subprocess
import sys
import tempfile

scanner = Path(sys.argv[1])
secret = ('sk' + '-' + 'A' * 24).encode()
zero = '0' * 40
count = 0


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()


def commit(repo, message='test change'):
    git(repo, 'add', '-A')
    git(repo, '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', message)
    return git(repo, 'rev-parse', 'HEAD')


def scan(repo, *, expected, records=None, env=None):
    global count
    result = subprocess.run([sys.executable, str(scanner), *(['--pre-push'] if records is not None else [])],
                            cwd=repo, input=records, text=True, capture_output=True,
                            env={**os.environ, **(env or {})})
    assert (result.returncode == 0) == expected, result.stdout + result.stderr
    assert secret.decode() not in result.stdout + result.stderr, 'scanner exposed a matching secret'
    count += 1
    return result


def outgoing(repo, remote=zero, local=None):
    return f'refs/heads/main {local or git(repo, "rev-parse", "HEAD")} refs/heads/main {remote}\n'


with tempfile.TemporaryDirectory(prefix='codex-secret-test-') as temp:
    root = Path(temp)
    repo = root / 'linear'
    git(root, 'init', '-q', str(repo))
    git(repo, 'config', 'user.name', 'Codex Guard Test')
    git(repo, 'config', 'user.email', 'codex-guard@example.invalid')
    (repo / 'README.md').write_text('safe\n')
    base = commit(repo)
    scan(repo, expected=True, records=outgoing(repo))
    (repo / 'temporary-secret.txt').write_bytes(secret)
    introduction = commit(repo)
    (repo / 'temporary-secret.txt').unlink()
    clean = commit(repo)
    scan(repo, expected=False, records=outgoing(repo))
    scan(repo, expected=False, records=outgoing(repo, base))
    git(repo, 'update-ref', 'refs/remotes/private/main', clean)
    scan(repo, expected=False, records=outgoing(repo))
    # Stale destination tracking refs must not replace the advertised tip.
    git(repo, 'update-ref', 'refs/remotes/origin/main', clean)
    scan(repo, expected=False, records=outgoing(repo, base))
    scan(repo, expected=False, records=outgoing(repo, '1' * 40))
    scan(repo, expected=True, records=outgoing(repo, introduction))
    scan(repo, expected=True, records=outgoing(repo, clean, zero))
    scan(repo, expected=False, records='malformed\n')
    scan(repo, expected=False, records=outgoing(repo, local='--all'))
    # A non-commit tag cannot silently skip a raw secret blob.
    blob = subprocess.run(['git', '-C', str(repo), 'hash-object', '-w', '--stdin'],
                          input=secret, capture_output=True, check=True).stdout.decode().strip()
    scan(repo, expected=False, records=outgoing(repo, local=blob))
    # Type changes (regular file -> symlink) carry new Git blob contents too.
    (repo / 'typed-file').write_text('safe\n')
    type_base = commit(repo)
    (repo / 'typed-file').unlink()
    (repo / 'typed-file').symlink_to(secret.decode())
    git(repo, 'add', 'typed-file')
    scan(repo, expected=False)
    commit(repo)
    (repo / 'typed-file').unlink()
    commit(repo)
    scan(repo, expected=False, records=outgoing(repo, type_base))
    # Safe filenames do not exempt a later sensitive path sharing the same blob.
    (repo / 'safe-file').write_text('SAFE=true\n')
    safe_base = commit(repo)
    (repo / 'safe-file').rename(repo / '.env')
    commit(repo)
    scan(repo, expected=False, records=outgoing(repo, safe_base))
    scan(repo, expected=False)
    (repo / '.env').unlink()
    (repo / '.env.example').write_text('SAFE_PLACEHOLDER=true\n')
    git(repo, 'add', '-A')
    scan(repo, expected=True)
    # Staged bytes are checked even if the working copy has already been fixed.
    (repo / 'staged.txt').write_bytes(secret)
    git(repo, 'add', 'staged.txt')
    (repo / 'staged.txt').write_text('safe\n')
    scan(repo, expected=False)
    git(repo, 'add', 'staged.txt')
    scan(repo, expected=True)
    (repo / 'large-safe.bin').write_bytes(b'\0' * (17 * 1024 * 1024))
    git(repo, 'add', 'large-safe.bin')
    scan(repo, expected=True)
    scan(repo, expected=False, env={'CODEX_SECRET_SCAN_MAX_BYTES': '1024'})

    merge = root / 'merge'
    git(root, 'init', '-q', str(merge))
    git(merge, 'config', 'user.name', 'Codex Guard Test')
    git(merge, 'config', 'user.email', 'codex-guard@example.invalid')
    (merge / 'base').write_text('base\n')
    commit(merge)
    branch = git(merge, 'branch', '--show-current')
    git(merge, 'checkout', '-qb', 'side')
    (merge / 'side').write_text('side\n')
    commit(merge)
    git(merge, 'checkout', '-q', branch)
    (merge / 'main').write_text('main\n')
    destination = commit(merge)
    git(merge, 'merge', '--no-ff', '--no-commit', 'side')
    (merge / 'only in merge.txt').write_bytes(secret)
    commit(merge, 'merge with synthetic secret')
    (merge / 'only in merge.txt').unlink()
    commit(merge, 'remove synthetic secret')
    result = scan(merge, expected=False, records=outgoing(merge, destination))
    assert 'only in merge.txt@' in result.stderr, 'merge finding missing source location'
    # Duplicate ref updates should not duplicate the same object/path finding.
    duplicate = scan(merge, expected=False, records=outgoing(merge, destination) * 2)
    assert duplicate.stderr == result.stderr, 'duplicate refs produced duplicate findings'
print(f'敏感信息扫描行为测试通过：{count} 个用例。')
PY
