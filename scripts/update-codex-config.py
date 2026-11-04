#!/usr/bin/env python3
"""Daily, fast-forward-only maintenance of an installed configuration source."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

try:
    import fcntl
except ImportError:
    fcntl = None

INTERVAL = 24 * 60 * 60


def git_environment():
    environment = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    local = subprocess.run(['git', 'rev-parse', '--local-env-vars'], check=True,
                           capture_output=True, text=True, timeout=5)
    for name in local.stdout.splitlines():
        environment.pop(name, None)
    return environment


def git(repo, *args):
    result = subprocess.run(
        ['git', '-C', str(repo), *args], text=True, capture_output=True,
        timeout=120, env=git_environment())
    if result.returncode:
        raise ValueError(f'Git {args[0]} 未完成；请检查来源、连接或仓库状态。')
    return result.stdout.strip()


def tracking(repo):
    branch = git(repo, 'symbolic-ref', '--quiet', '--short', 'HEAD')
    remote = git(repo, 'config', '--get', f'branch.{branch}.remote')
    ref = git(repo, 'config', '--get', f'branch.{branch}.merge')
    if remote == '.' or not ref.startswith('refs/heads/'):
        raise ValueError('自更新需要已配置的远程跟踪分支。')
    return branch, remote, ref


def clean(repo):
    if git(repo, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('规范来源有未提交或未跟踪文件；保持原样，未自动更新。')


def ancestor(repo, before, after):
    result = subprocess.run(
        ['git', '-C', str(repo), 'merge-base', '--is-ancestor', before, after],
        capture_output=True, timeout=30, env=git_environment())
    if result.returncode not in (0, 1):
        raise ValueError('无法确定规范版本的祖先关系。')
    return result.returncode == 0


def save(path, state):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def registered(repo, candidate):
    return f'worktree {candidate}' in git(repo, 'worktree', 'list', '--porcelain', '-z').split('\0')


def update(repo, root, *, apply=False, check_source, install_source, now=None):
    repo, root = Path(repo).resolve(), Path(root).resolve()
    state_dir = root / '.codex-config-state'
    state_path = state_dir / 'daily-update.json'
    if not apply:
        print(f'预览每日更新：{repo} → {root}；未联网、未修改。')
        return 0
    state = {}
    lock = None
    attempted = False
    try:
        if fcntl is None:
            raise ValueError('当前 Python 不提供所需文件锁；未联网或修改配置。')
        if not (state_dir / 'manifest.json').is_file():
            raise ValueError('未找到安装清单；先确认安装来源，不自动安装新实例。')
        entry = root / 'AGENTS.md'
        if not entry.is_symlink() or entry.resolve() != repo / 'AGENTS.md':
            raise ValueError('所选仓库不是当前规范入口的安装来源。')
        if Path(git(repo, 'rev-parse', '--show-toplevel')).resolve() != repo:
            raise ValueError('安装来源不是独立 Git 检出根；不更新其父仓库。')
        common = Path(git(repo, 'rev-parse', '--git-common-dir'))
        if not common.is_absolute():
            common = repo / common
        lock = (common / 'codex-config-update.lock').open('a')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('已有同源更新在运行，本次不重复执行。')
            return 0
        now = time.time() if now is None else now
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding='utf-8'))
            if not isinstance(state, dict):
                raise ValueError('每日更新记录必须是对象。')
            last = state.get('last_attempt', 0)
            if not isinstance(last, (int, float)):
                raise ValueError('每日更新记录不合法。')
            if now - last < INTERVAL:
                print('距上次更新检查不足 24 小时，本次未联网。')
                return 0
        retained = state.get('candidate_path')
        if retained and (Path(retained).parent.exists() or registered(repo, retained)):
            raise ValueError(f'前次候选目录尚未清理：{retained}；本次不再创建候选。')
        pending = state.get('pending_install', False)
        manifest = json.loads((state_dir / 'manifest.json').read_text(encoding='utf-8'))
        installed = manifest.get('source_revision', state.get('installed_head'))
        validated = state.get('validated_head')
        state = {'last_attempt': now, 'status': 'checking', 'pending_install': pending,
                 'installed_head': installed, 'validated_head': validated}
        save(state_path, state)
        attempted = True
        clean(repo)
        original = git(repo, 'rev-parse', 'HEAD')
        source = tracking(repo)
        _, remote, ref = source
        url = git(repo, 'remote', 'get-url', remote)
        state['old_head'] = original
        save(state_path, state)
        git(repo, 'fetch', '--no-tags', '--no-recurse-submodules', remote, ref)
        target = git(repo, 'rev-parse', 'FETCH_HEAD^{commit}')
        state['upstream_head'] = target
        if ancestor(repo, target, original):
            if pending or installed != original:
                if validated != original:
                    check_source(repo)
                    state['validated_head'] = original
                state['pending_install'] = True
                save(state_path, state)
                if install_source(repo, root):
                    raise ValueError('前次更新的配置应用仍未完成；版本与恢复记录已保留。')
                state['pending_install'] = False
                state['installed_head'] = original
                state['new_head'] = original
                state['status'] = 'updated'
                save(state_path, state)
                print('本实例的配置应用及诊断已完成。')
                return 0
            state['status'] = 'up_to_date'
            save(state_path, state)
            print('上游无待应用更新；保留当前版本及本地提交。')
            return 0
        if not ancestor(repo, original, target):
            raise ValueError('规范来源与上游已分叉；未合并、重置或推送。')

        # Validate away from the source tree referenced by live configuration links.
        temporary = Path(tempfile.mkdtemp(prefix='codex-config-update-')).resolve()
        candidate = temporary / 'candidate'
        state['candidate_path'] = str(candidate)
        try:
            save(state_path, state)
            git(repo, 'worktree', 'add', '--detach', str(candidate), target)
            check_source(candidate)
            state['validated_head'] = target
            save(state_path, state)
        finally:
            try:
                if registered(repo, candidate):
                    git(repo, 'worktree', 'remove', str(candidate))
                shutil.rmtree(temporary)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                raise ValueError(f'候选清理未完成，保留目录：{candidate}') from error
            state.pop('candidate_path', None)
            save(state_path, state)

        clean(repo)
        if (git(repo, 'rev-parse', 'HEAD') != original or tracking(repo) != source
                or git(repo, 'remote', 'get-url', remote) != url):
            raise ValueError('验证期间来源发生变化；本次不激活更新。')
        git(repo, 'update-ref', 'refs/codex-config/previous', original)
        state['pending_install'] = True
        save(state_path, state)
        git(repo, 'merge', '--ff-only', '--no-edit', target)
        state['new_head'] = git(repo, 'rev-parse', 'HEAD')
        save(state_path, state)
        if install_source(repo, root):
            raise ValueError('源码已快进，但配置应用或诊断未完成；保留版本记录，不自动回退。')
        state['pending_install'] = False
        state['installed_head'] = state['new_head']
        state['status'] = 'updated'
        save(state_path, state)
        print(f'规范已更新：{original[:12]} → {state["new_head"][:12]}；信任状态未自动更改。')
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        if attempted:
            state['status'] = 'failed'
            state['error'] = str(error)
            save(state_path, state)
        print(f'每日更新未完成：{error}')
        return 1
    finally:
        if lock:
            lock.close()
