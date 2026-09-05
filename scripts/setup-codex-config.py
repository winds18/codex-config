#!/usr/bin/env python3
"""统一配置入口：源码预检、事务安装及安装后检查；默认只预览。"""

import argparse
import ast
import importlib.util
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_source(repo):
    """离线预检实际安装来源，不运行 hooks、回归测试或上游模板代码。"""
    required = (
        'AGENTS.md', 'install.sh', 'hooks/hooks.json', 'hooks/codex-policy-guard.py',
        'scripts/setup-codex-config.py', 'scripts/manage-codex-config.py',
        'scripts/validate-config.py',
        'scripts/restore-codex-global-links.sh', 'scripts/restore-codex-official-state.sh',
        'scripts/codex-config-doctor.sh',
    )
    missing = [name for name in required if not (repo / name).is_file()]
    template_checker = 'skills/refero-design-prompts/scripts/verify-template-dependencies.py'
    if (repo / 'skills/refero-design-prompts').is_dir() and not (repo / template_checker).is_file():
        missing.append(template_checker)
    for directory in ('agents', 'docs', 'prompts', 'skills'):
        if not (repo / directory).is_dir() or not any((repo / directory).iterdir()):
            missing.append(directory + '/')
    if missing:
        raise ValueError('安装来源不完整：' + '、'.join(missing))
    load('setup_validator', SCRIPTS / 'validate-config.py').check(repo)
    scripts = list((repo / 'scripts').glob('*.py')) + list((repo / 'hooks').glob('*.py'))
    scripts += [p for p in (repo / 'skills').glob('*/scripts/*.py')]
    for path in scripts:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    bash = shutil.which('bash')
    if not bash:
        raise ValueError('源码预检需要 Bash；未修改配置。')
    shell_files = [repo / 'install.sh', *sorted((repo / 'scripts').glob('*.sh')),
                   *sorted((repo / 'git-hooks').glob('*')),
                   *sorted((repo / 'skills').glob('*/scripts/*.sh'))]
    for path in shell_files:
        if path.is_file():
            subprocess.run([bash, '-n', str(path)], check=True)
    templates = repo / 'skills/refero-design-prompts/assets/templates'
    checker = REPO / 'skills/refero-design-prompts/scripts/verify-template-dependencies.py'
    if (repo / 'skills/refero-design-prompts').is_dir():
        rows, errors, notes, _ = load('setup_templates', checker).inspect(templates)
        if errors:
            raise ValueError('模板资产预检失败：\n' + '\n'.join(errors))
        print(f'模板离线预检通过：{len(rows)} 文件，{len(notes)} 个已知注记。')
    print('源码配置、引用及脚本语法预检通过。')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', default='install',
                        choices=('install', 'check', 'doctor', 'uninstall', 'recover'))
    parser.add_argument('--repo', default=str(REPO), help='安装来源；默认入口所在仓库，不自动拉取远程')
    parser.add_argument('--codex-home', default=os.environ.get('CODEX_HOME') or str(Path.home() / '.codex'))
    parser.add_argument('--skills-dir', help='唯一技能目录；默认沿用清单或配置根/skills')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true', help='执行 install/uninstall/recover；缺省只预览')
    mode.add_argument('--dry-run', action='store_true', help='明确只预览')
    args = parser.parse_args(argv)
    if args.apply and args.action in ('check', 'doctor'):
        parser.error('check/doctor 始终只读，不接受 --apply')
    try:
        installer = load('setup_installer', SCRIPTS / 'manage-codex-config.py')
    except (OSError, SyntaxError) as error:
        print(f'安装入口不完整或已损坏：{error}', file=sys.stderr)
        return 1
    repo = installer.absolute(args.repo).resolve()
    root = installer.absolute(args.codex_home)
    options = ['--repo', str(repo), '--codex-home', str(root)]
    if args.skills_dir:
        options += ['--skills-dir', str(installer.absolute(args.skills_dir))]
    try:
        if args.action in ('install', 'check'):
            print(f'源码预检：{repo}', flush=True)
            check_source(repo)
            if args.action == 'check':
                return 0
        if args.action == 'doctor':
            return installer.main(['doctor', *options])
        print(f'{"执行" if args.apply else "预览"} {args.action}：{root}', flush=True)
        result = installer.main([args.action, *options, '--apply' if args.apply else '--dry-run'])
        if result:
            return result
        if not args.apply:
            print('应用此操作：' + shlex.join(['bash', str(REPO / 'install.sh'), args.action, *options, '--apply']))
            return 0
        if args.action == 'install':
            print('安装后检查：', flush=True)
            result = installer.main(['doctor', *options])
            if result:
                print('配置已写入，但安装后检查失败。请按诊断修复；需撤销时先预览 uninstall。', file=sys.stderr)
                return result
            print('文件安装及自检完成。开启新任务核对规则/技能；自定义 hook 仍需在客户端审查信任。')
        return 0
    except (installer.Conflict, OSError, ValueError, SyntaxError, subprocess.CalledProcessError) as error:
        print(f'操作未完成：{error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
