#!/usr/bin/env python3
"""安装/卸载当前 worktree 的 Git hooks，默认只预览；中断后用 --recover。"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def run(repo, *arguments, optional=False):
    result = subprocess.run(['git', '-C', str(repo), *arguments], text=True, capture_output=True)
    if result.returncode and not (optional and result.returncode in (1, 5)):
        raise RuntimeError(result.stderr.strip() or 'Git 命令失败')
    return result.stdout[:-1] if result.stdout.endswith('\n') else result.stdout


def values(repo, scope, key):
    result = run(repo, 'config', '--null', scope, '--get-all', key, optional=True)
    return result.split('\0')[:-1] if result else []


def set_values(repo, scope, key, items):
    run(repo, 'config', scope, '--unset-all', key, optional=True)
    for value in items:
        run(repo, 'config', scope, '--add', key, value)


def atomic_json(path, data):
    descriptor, staging = tempfile.mkstemp(prefix='.codex-hooks-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staging, path)
    finally:
        if os.path.exists(staging):
            os.unlink(staging)


def worktree_configs(common):
    return [common / 'config.worktree', *common.glob('worktrees/*/config.worktree')]


def release_stale_lock(lock):
    if not lock.exists():
        return
    try:
        pid = int((lock / 'pid').read_text())
        os.kill(pid, 0)
    except ProcessLookupError:
        (lock / 'pid').unlink()
        lock.rmdir()
    except (OSError, ValueError) as error:
        raise RuntimeError(f'无法确认锁已失效：{lock}，请先人工核实进程。') from error
    else:
        raise RuntimeError(f'安装器进程 {pid} 仍在运行，未恢复。')


def restore_pending(repo, common, git_dir, pending, manifest):
    saved = json.loads(pending.read_text())
    worktree_config = git_dir / 'config.worktree'
    raw = run(repo, 'config', '--null', '--file', str(worktree_config), '--get-all', 'core.hooksPath', optional=True)
    current = raw.split('\0')[:-1] if raw else []
    if current != saved['before'][:len(current)] and current != saved['desired'][:len(current)]:
        raise RuntimeError('中断后 core.hooksPath 又被外部修改，拒绝覆盖；保留 pending 供人工处理。')
    # 直接编辑当前 worktree 文件；不依赖骤停时 extensions.worktreeConfig 是否已写完。
    run(repo, 'config', '--file', str(worktree_config), '--unset-all', 'core.hooksPath', optional=True)
    for value in saved['before']:
        run(repo, 'config', '--file', str(worktree_config), '--add', 'core.hooksPath', value)
    if not saved['config_existed'] and worktree_config.exists() and not run(repo, 'config', '--file', str(worktree_config), '--list'):
        worktree_config.unlink(missing_ok=True)
    if saved['extension_enabled'] or not any(path.exists() and path.read_text().strip() for path in worktree_configs(common)):
        set_values(repo, '--local', 'extensions.worktreeConfig', saved['extension_before'])
    else:
        print('中断后发现其他 worktree 配置，保留共享扩展，避免停用其他设置。')
    if saved['manifest_before'] is None:
        manifest.unlink(missing_ok=True)
    else:
        atomic_json(manifest, saved['manifest_before'])
    pending.unlink()


def manage(args, repo, hooks, git_dir, common):
    manifest = git_dir / 'codex-config-hooks.json'
    pending = git_dir / 'codex-config-hooks-pending.json'
    if args.recover:
        if not pending.exists():
            print('没有待恢复的 Git hooks 事务。')
        elif args.apply:
            restore_pending(repo, common, git_dir, pending, manifest)
            print('已恢复 Git hooks 中断前配置；保留其他新增设置。')
        else:
            print(f'待恢复事务：{pending}；加 --apply 才会恢复。')
        return
    interrupted = [path for path in [common / 'codex-config-hooks-pending.json', *common.glob('worktrees/*/codex-config-hooks-pending.json')] if path.exists()]
    if interrupted:
        raise RuntimeError(f'存在未完成事务：{interrupted[0]}；在对应 worktree 使用 --recover 预览，再 --recover --apply 恢复。')
    previous = json.loads(manifest.read_text()) if manifest.exists() else None
    extension = values(repo, '--local', 'extensions.worktreeConfig')
    enabled = run(repo, 'config', '--local', '--bool', 'extensions.worktreeConfig', optional=True) == 'true'
    if not enabled:
        if run(repo, 'config', '--local', '--get', 'core.worktree', optional=True) or run(repo, 'config', '--local', '--bool', 'core.bare', optional=True) == 'true':
            raise RuntimeError('当前仓库需要先按 Git 文档迁移 core.worktree/core.bare；未修改共享配置。')
        if any(path.exists() and path.read_text().strip() for path in worktree_configs(common)):
            raise RuntimeError('发现尚未启用的 config.worktree 内容；先审查再启用，避免意外激活配置。')
    current = values(repo, '--worktree', 'core.hooksPath') if enabled else []
    if previous and current != [previous['installed']]:
        raise RuntimeError('core.hooksPath 在安装后被修改，未覆盖。')
    if args.uninstall:
        if not previous:
            print('无本安装器清单；保持现有 Git hooks 配置。')
            return
        desired = previous['before']
    else:
        if not (hooks / 'pre-commit').is_file() or not (hooks / 'pre-push').is_file():
            raise RuntimeError(f'缺少 Git hooks：{hooks}')
        desired = [str(hooks)]
    print(f'worktree: {repo}\ncore.hooksPath: {current or "继承已有配置"} -> {desired or "继承已有配置"}')
    if not enabled:
        print('将启用共享 extensions.worktreeConfig；仅在不存在待激活配置时执行。')
    if not args.apply:
        print('仅预览；加 --apply 才会写入。不会执行任何 hook。')
        return
    if not args.uninstall and previous and current == desired:
        print('已安装，无需修改。')
        return
    worktree_config = git_dir / 'config.worktree'
    config_existed = worktree_config.exists()
    # 在第一次修改 Git 配置前持久化。进程被 kill 后也能恢复，不能仅依赖异常处理。
    atomic_json(pending, {'before': current, 'desired': desired, 'config_existed': config_existed,
                          'extension_before': extension, 'extension_enabled': enabled,
                          'manifest_before': previous})
    try:
        if not enabled:
            run(repo, 'config', '--local', 'extensions.worktreeConfig', 'true')
        set_values(repo, '--worktree', 'core.hooksPath', desired)
        if args.uninstall:
            if not run(repo, 'config', '--worktree', '--list') and not previous['config_existed']:
                worktree_config.unlink(missing_ok=True)
            if not previous['extension_enabled'] and not any(path.exists() and path.read_text().strip() for path in worktree_configs(common)):
                set_values(repo, '--local', 'extensions.worktreeConfig', previous['extension_before'])
            elif not previous['extension_enabled']:
                print('其他 worktree 配置已生效，保留 extensions.worktreeConfig，避免停用其他设置。')
            manifest.unlink()
        else:
            saved = previous or {'before': current, 'extension_before': extension,
                                  'extension_enabled': enabled, 'config_existed': config_existed}
            saved['installed'] = str(hooks)
            atomic_json(manifest, saved)
        pending.unlink()
    except BaseException:
        restore_pending(repo, common, git_dir, pending, manifest)
        raise
    print('Git hooks 配置已更新；未执行 hook。')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument('--hooks-dir')
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--uninstall', action='store_true')
    actions.add_argument('--recover', action='store_true')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--apply', action='store_true')
    modes.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    repo = Path(args.repo).expanduser().resolve()
    hooks = Path(args.hooks_dir).expanduser().resolve() if args.hooks_dir else repo / 'git-hooks'
    git_dir = Path(run(repo, 'rev-parse', '--absolute-git-dir'))
    common = Path(run(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
    lock = common / 'codex-config-hooks-lock'
    if args.apply:
        if args.recover:
            release_stale_lock(lock)
        try:
            lock.mkdir()
            (lock / 'pid').write_text(str(os.getpid()))
        except FileExistsError as error:
            raise RuntimeError(f'其他安装器持有 {lock}；若进程已结束，用 --recover --apply 恢复。') from error
    try:
        manage(args, repo, hooks, git_dir, common)
    finally:
        if args.apply:
            (lock / 'pid').unlink(missing_ok=True)
            lock.rmdir()


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError) as error:
        print(f'Git hooks 配置失败：{error}', file=sys.stderr)
        sys.exit(1)
