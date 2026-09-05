#!/usr/bin/env python3
"""按文件安装个人配置；所有修改须显式 --apply，备份和事务仅用标准库。"""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile

STATE = '.codex-config-state'
VERSION = 2


class Conflict(Exception):
    pass


def absolute(value):
    path = Path(os.path.abspath(os.path.expanduser(str(value))))
    return path.parent.resolve() / path.name


def exists(path):
    return path.exists() or path.is_symlink()


def snapshot(path):
    if path.is_symlink():
        return {'kind': 'link', 'target': os.readlink(path)}
    if not path.exists():
        return {'kind': 'absent'}
    mode = stat.S_IMODE(path.stat().st_mode)
    if path.is_file():
        return {'kind': 'file', 'data': base64.b64encode(path.read_bytes()).decode(), 'mode': mode}
    if path.is_dir():
        return {'kind': 'dir', 'mode': mode,
                'children': {p.name: snapshot(p) for p in sorted(path.iterdir())}}
    raise Conflict(f'不支持特殊文件，未修改：{path}')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def file_value(text, mode=0o600):
    return {'kind': 'file', 'data': base64.b64encode(text.encode()).decode(), 'mode': mode}


def validate_snapshot(value, label='快照'):
    if not isinstance(value, dict):
        raise Conflict(f'{label} 必须是对象')
    kind = value.get('kind')
    fields = {'absent': {'kind'}, 'link': {'kind', 'target'},
              'file': {'kind', 'data', 'mode'}, 'dir': {'kind', 'children', 'mode'}}
    if not isinstance(kind, str) or kind not in fields or set(value) != fields[kind]:
        raise Conflict(f'{label} 的类型或字段不合法')
    if kind in ('file', 'dir') and (type(value['mode']) is not int or not 0 <= value['mode'] <= 0o7777):
        raise Conflict(f'{label} 的权限 mode 不合法')
    if kind == 'link' and (not isinstance(value['target'], str) or not value['target'] or '\0' in value['target']):
        raise Conflict(f'{label} 的软链接目标不合法')
    if kind == 'file':
        if not isinstance(value['data'], str):
            raise Conflict(f'{label} 的 base64 内容必须是字符串')
        try:
            base64.b64decode(value['data'], validate=True)
        except (ValueError, TypeError) as error:
            raise Conflict(f'{label} 的 base64 内容损坏') from error
    if kind == 'dir':
        if not isinstance(value['children'], dict):
            raise Conflict(f'{label} 的目录子项不合法')
        for name, child in value['children'].items():
            if not isinstance(name, str) or name in ('', '.', '..') or '/' in name or '\0' in name:
                raise Conflict(f'{label} 的目录子项名称不合法')
            validate_snapshot(child, f'{label}/{name}')
            if child['kind'] == 'absent':
                raise Conflict(f'{label}/{name} 是不存在的目录子项，快照可能在读取期间发生变化')


def validate_backups(backups, manifest):
    if not isinstance(backups, dict):
        raise Conflict('backups.json 应为对象')
    for key, value in backups.items():
        validate_snapshot(value, f'备份 {key}')
    if manifest:
        for name, entry in manifest['entries'].items():
            key = entry.get('backup')
            if key not in backups:
                raise Conflict(f'备份缺失：{name}')
            digest = entry.get('backup_digest')
            if manifest['version'] >= 2 and not digest:
                raise Conflict(f'备份摘要缺失，拒绝降级验证：{name}')
            if digest is not None and digest != fingerprint(backups[key]):
                raise Conflict(f'备份摘要不匹配，内容可能损坏：{name}')


def validate_manifest(manifest, root):
    if not isinstance(manifest, dict) or type(manifest.get('version')) is not int or manifest['version'] not in (1, VERSION) or manifest.get('root') != str(root):
        raise Conflict('清单版本或配置根不匹配；不会猜测或覆盖备份。')
    if not isinstance(manifest.get('skills_dir'), str) or not Path(manifest['skills_dir']).is_absolute() or not isinstance(manifest.get('entries'), dict):
        raise Conflict('清单技能目录或入口表不合法')
    for name, entry in manifest['entries'].items():
        if not isinstance(name, str) or not Path(name).is_absolute() or not isinstance(entry, dict) or not isinstance(entry.get('backup'), str) or not isinstance(entry.get('installed'), str):
            raise Conflict('清单入口或备份引用不合法')
        if manifest['version'] >= 2 and not isinstance(entry.get('backup_digest'), str):
            raise Conflict(f'备份摘要缺失，拒绝降级验证：{name}')
    if not isinstance(manifest.get('owned_hooks'), dict) or not isinstance(manifest.get('baseline_hooks'), dict):
        raise Conflict('清单 hook 记录不合法')
    if not isinstance(manifest.get('created_dirs'), list) or any(not isinstance(name, str) or not Path(name).is_absolute() for name in manifest['created_dirs']):
        raise Conflict('清单新建目录记录不合法')


def remove(path):
    validate_snapshot(snapshot(path), str(path))
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def write_staged(path, value):
    """只写新建的私有暂存树；调用者已递归验证整个快照。"""
    kind = value['kind']
    if kind == 'link':
        path.symlink_to(value['target'])
    elif kind == 'file':
        path.write_bytes(base64.b64decode(value['data'], validate=True))
        path.chmod(value['mode'])
    elif kind == 'dir':
        path.mkdir()
        for name, child in value['children'].items():
            write_staged(path / name, child)
        path.chmod(value['mode'])
    else:
        raise Conflict(f'未知备份类型：{kind}')


def check_staging_item(transaction, item):
    path = Path(item['directory'])
    if not exists(path):
        return
    if path.is_symlink() or not path.is_dir() or [path.stat().st_dev, path.stat().st_ino] != item['identity']:
        raise Conflict(f'暂存目录被外部替换，未清理：{path}')
    if any(child.name not in ('payload', 'previous') for child in path.iterdir()):
        raise Conflict(f'暂存目录出现外来文件，未清理：{path}')
    previous = path / 'previous'
    if exists(previous):
        current = snapshot(previous)
        validate_snapshot(current, str(previous))
        expected_digest = item.get('previous_digest')
        allowed = {expected_digest} if expected_digest else {
            fingerprint(transaction['changes'][item['path']][side]) for side in ('before', 'after')}
        if fingerprint(current) not in allowed:
            raise Conflict(f'暂存的原入口被外部修改，保留其内容及事务：{previous}')


def clean_staging(state, transaction):
    for item in list(transaction.get('staging', [])):
        path = Path(item['directory'])
        check_staging_item(transaction, item)
        if exists(path):
            shutil.rmtree(path)
        transaction['staging'].remove(item)
        atomic_json(state / 'transaction.json', transaction)


def put(path, value, transaction_context=None, expected=None):
    validate_snapshot(value, str(path))
    before = snapshot(path)
    validate_snapshot(before, str(path))
    if expected is not None:
        validate_snapshot(expected, f'{path} 预期状态')
        if before != expected:
            raise Conflict(f'写入前入口与已核对状态不同，未覆盖：{path}')
    if before == value:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.codex-config-stage-', dir=path.parent))
    item = {'path': str(path), 'directory': str(stage), 'identity': [stage.stat().st_dev, stage.stat().st_ino],
            'previous_digest': fingerprint(before)}
    if transaction_context:
        state, transaction = transaction_context
        transaction.setdefault('staging', []).append(item)
        atomic_json(state / 'transaction.json', transaction)
    try:
        if value['kind'] != 'absent':
            write_staged(stage / 'payload', value)
        if snapshot(path) != before:
            raise Conflict(f'暂存期间入口被外部修改，未覆盖：{path}')
        if exists(path):
            os.replace(path, stage / 'previous')
            if snapshot(stage / 'previous') != before:
                if not exists(path):
                    os.replace(stage / 'previous', path)
                raise Conflict(f'移开入口时发现外部改动，已保留其内容：{path}')
        if value['kind'] != 'absent':
            if exists(path):
                raise Conflict(f'替换期间入口被外部创建，未覆盖：{path}')
            os.replace(stage / 'payload', path)
        if transaction_context:
            clean_staging(state, transaction)
        else:
            shutil.rmtree(stage)
    except BaseException:
        if not transaction_context and exists(stage / 'previous') and not exists(path):
            os.replace(stage / 'previous', path)
        raise


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def restore_metadata(path, value):
    validate_snapshot(value, str(path))
    if value['kind'] == 'absent':
        path.unlink(missing_ok=True)
        return
    if value['kind'] != 'file':
        raise Conflict(f'事务元数据备份应为普通文件：{path}')
    fd, staging = tempfile.mkstemp(prefix='.restore-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(base64.b64decode(value['data'], validate=True))
            os.fchmod(stream.fileno(), value['mode'])
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staging, path)
    finally:
        if os.path.exists(staging):
            os.unlink(staging)


def read_json(path, fallback=None):
    if not exists(path):
        return copy.deepcopy(fallback)
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise Conflict(f'无法读取 JSON，未修改：{path}: {error}') from error


def check_parents(path, root):
    # 不穿过外来的目录软链接写入其他位置，也不改写旧版整目录链接的真源。
    cursor = path.parent
    while cursor == root or root in cursor.parents:
        if cursor.is_symlink():
            raise Conflict(f'父目录是软链接，拒绝穿透写入：{cursor}。旧版整目录安装须先用明确的原备份还原；不会猜测最近备份。')
        if exists(cursor) and not cursor.is_dir():
            raise Conflict(f'父路径不是目录：{cursor}')
        if cursor == root:
            break
        cursor = cursor.parent


def protect_source(path, repo):
    if path == repo or repo in path.parents or path in repo.parents:
        raise Conflict(f'安装目标与真源相交，拒绝覆盖源码：{path}')


def validate_hooks(data, path):
    if not isinstance(data, dict) or not isinstance(data.get('hooks', {}), dict):
        raise Conflict(f'hooks 配置格式不合法：{path}')
    for event, groups in data.get('hooks', {}).items():
        if not isinstance(groups, list) or any(not isinstance(g, dict) for g in groups):
            raise Conflict(f'hooks.{event} 必须是对象数组：{path}')
    return data


def read_hooks(path):
    if not exists(path) or (path.is_symlink() and not path.exists()):
        return {}
    return validate_hooks(read_json(path), path)


def without_owned(current, owned):
    result = copy.deepcopy(current)
    events = result.setdefault('hooks', {})
    for event, groups in owned.items():
        for group in groups:
            if group not in events.get(event, []):
                raise Conflict(f'已管理的 {event} hook 被改动或删除；请先恢复该条目，保留其他自定义条目。')
            events[event].remove(group)
        if not events[event]:
            del events[event]
    if not events:
        result.pop('hooks', None)
    return result


def normalized_hooks(data):
    result = copy.deepcopy(data)
    if isinstance(result.get('hooks'), dict):
        result['hooks'] = {event: groups for event, groups in result['hooks'].items() if groups}
    if not result.get('hooks'):
        result.pop('hooks', None)
    return result


def owned_hooks(repo, root):
    config = validate_hooks(read_json(repo / 'hooks/hooks.json'), repo / 'hooks/hooks.json')
    groups = copy.deepcopy(config.get('hooks', {}))
    # 安装产物绑定选中的配置根：客户端不传 CODEX_HOME 时仍不会执行真实 home 中另一份 hook。
    command = f'CODEX_HOME={shlex.quote(str(root))} python3 {shlex.quote(str(root / "hooks/codex-policy-guard.py"))}'
    for event_groups in groups.values():
        for group in event_groups:
            for hook in group.get('hooks', []):
                if hook.get('type') != 'command' or 'codex-policy-guard.py' not in hook.get('command', ''):
                    raise Conflict('仓库出现未识别的 hook 命令；请更新安装器的受控命令绑定。')
                hook['command'] = command
    return groups


def desired_links(repo, root, skills):
    links = {str(root / 'AGENTS.md'): {'kind': 'link', 'target': str(repo / 'AGENTS.md')}}
    for directory in ('agents', 'prompts', 'docs', 'hooks'):
        for source in sorted((repo / directory).rglob('*')):
            if source.is_file() and source.name != 'hooks.json' and '__pycache__' not in source.parts:
                links[str(root / source.relative_to(repo))] = {'kind': 'link', 'target': str(source)}
    for source in sorted((repo / 'skills').iterdir()):
        if (source / 'SKILL.md').is_file():
            links[str(skills / source.name)] = {'kind': 'link', 'target': str(source)}
    for target, source in [('restore-global-setup.sh', 'restore-codex-global-links.sh'),
                           ('restore-official-state.sh', 'restore-codex-official-state.sh')]:
        links[str(root / target)] = {'kind': 'link', 'target': str(repo / 'scripts' / source)}
    if (repo / 'install.sh').is_file():
        links[str(root / 'codex-config.sh')] = {'kind': 'link', 'target': str(repo / 'install.sh')}
    for value in links.values():
        if not Path(value['target']).exists():
            raise Conflict(f'真源缺失：{value["target"]}')
    return links


def backup_key(path):
    return hashlib.sha256(path.encode()).hexdigest()


def build_plan(args, root, repo, state, old):
    skills = absolute(args.skills_dir or (old or {}).get('skills_dir') or root / 'skills')
    if not old and exists(state / 'backups.json'):
        raise Conflict('存在孤立备份但缺少 manifest；保持原备份，先恢复清单或事务，不能重新安装覆盖。')
    backups = read_json(state / 'backups.json', {})
    validate_backups(backups, old)
    if old and old['version'] == 1:
        print('警告：旧清单没有完整的历史备份摘要；仅验证现有结构。更新将记录当前备份摘要，不能追溯此前内容。')
    entries = (old or {}).get('entries', {})
    changes = {}
    next_entries = {}
    installing = args.action == 'install'
    links = desired_links(repo, root, skills) if installing else {}
    for name in sorted(set(entries) | set(links)):
        if name == str(root / 'hooks.json'):
            continue
        path = Path(name)
        protect_source(path, repo)
        allowed_root = root if path == root or root in path.parents else absolute((old or {}).get('skills_dir', skills))
        if name in links and skills in path.parents:
            allowed_root = skills
        if path != allowed_root and allowed_root not in path.parents:
            raise Conflict(f'清单入口超出配置和技能目录：{path}')
        if path == state or state in path.parents:
            raise Conflict(f'清单入口不能指向安装状态目录：{path}')
        check_parents(path, allowed_root)
        current = snapshot(path)
        prior = entries.get(name)
        if prior and fingerprint(current) != prior['installed']:
            raise Conflict(f'已管理入口被外部修改，未覆盖：{path}')
        if prior and prior['backup'] not in backups:
            raise Conflict(f'备份丢失，未修改：{path}')
        if name in links:
            key = prior['backup'] if prior else backup_key(name)
            if not prior:
                backups[key] = current
            desired = links[name]
            next_entries[name] = {'backup': key, 'backup_digest': fingerprint(backups[key]), 'installed': fingerprint(desired)}
        else:
            desired = backups[prior['backup']]
        if current != desired:
            changes[name] = {'before': current, 'after': desired}
    hook_path = root / 'hooks.json'
    check_parents(hook_path, root)
    hook_name = str(hook_path)
    current_hooks = read_hooks(hook_path)
    retained = without_owned(current_hooks, (old or {}).get('owned_hooks', {}))
    hook_entry = entries.get(hook_name)
    if installing:
        new_owned = owned_hooks(repo, root)
        merged = copy.deepcopy(retained)
        for event, groups in new_owned.items():
            merged.setdefault('hooks', {}).setdefault(event, []).extend(groups)
        key = hook_entry['backup'] if hook_entry else backup_key(hook_name)
        if not hook_entry:
            backups[key] = snapshot(hook_path)
        if key not in backups:
            raise Conflict(f'备份丢失：{hook_path}')
        desired = file_value(json.dumps(merged, ensure_ascii=False, indent=2) + '\n')
        next_entries[hook_name] = {'backup': key, 'backup_digest': fingerprint(backups[key]), 'installed': fingerprint(desired)}
        baseline_hooks = (old or {}).get('baseline_hooks', current_hooks)
    elif hook_entry:
        if hook_entry['backup'] not in backups:
            raise Conflict(f'备份丢失：{hook_path}')
        # 外来 hook 在安装后有新增时保留；内容未变则精确恢复原文件/软链接和权限。
        desired = backups[hook_entry['backup']] if normalized_hooks(retained) == normalized_hooks(old['baseline_hooks']) else file_value(json.dumps(retained, ensure_ascii=False, indent=2) + '\n')
    else:
        desired = snapshot(hook_path)
    current = snapshot(hook_path)
    if current != desired:
        changes[hook_name] = {'before': current, 'after': desired}
    if installing:
        manifest = {'version': VERSION, 'root': str(root), 'repo': str(repo), 'skills_dir': str(skills),
                    'entries': next_entries, 'owned_hooks': new_owned, 'baseline_hooks': baseline_hooks,
                    'created_dirs': (old or {}).get('created_dirs', [])}
        backups = {entry['backup']: backups[entry['backup']] for entry in next_entries.values()}
    else:
        manifest = None
        backups = None
    for name, change in changes.items():
        validate_snapshot(change['before'], f'{name} 修改前')
        validate_snapshot(change['after'], f'{name} 修改后')
    if manifest:
        validate_backups(backups, manifest)
    return changes, manifest, backups


def validate_transaction(transaction):
    if not isinstance(transaction, dict) or transaction.get('version', 1) not in (1, 2, 3):
        raise Conflict('事务格式或版本不支持')
    for key in ('changes', 'old_state'):
        if not isinstance(transaction.get(key), dict):
            raise Conflict(f'事务 {key} 必须是对象')
    if set(transaction['old_state']) != {'manifest.json', 'backups.json'}:
        raise Conflict('事务元数据路径不合法')
    for name, change in transaction['changes'].items():
        if not isinstance(name, str) or not Path(name).is_absolute() or not isinstance(change, dict):
            raise Conflict('事务入口路径或修改记录不合法')
        for side in ('before', 'after'):
            validate_snapshot(change.get(side), f'{name} {side}')
            digest = change.get(side + '_digest')
            if transaction.get('version', 1) >= 2 and not digest:
                raise Conflict(f'事务快照摘要缺失：{name} {side}')
            if digest is not None and digest != fingerprint(change[side]):
                raise Conflict(f'事务快照摘要不匹配：{name} {side}')
    for name, value in transaction['old_state'].items():
        validate_snapshot(value, f'事务元数据 {name}')
        if value['kind'] not in ('absent', 'file'):
            raise Conflict(f'事务元数据不是普通文件：{name}')
        digest = transaction.get('old_state_digests', {}).get(name)
        if transaction.get('version', 1) >= 2 and not digest:
            raise Conflict(f'事务元数据摘要缺失：{name}')
        if digest is not None and digest != fingerprint(value):
            raise Conflict(f'事务元数据摘要不匹配：{name}')
    started = transaction.get('started', list(transaction['changes']))
    if not isinstance(started, list) or any(not isinstance(name, str) for name in started) or len(set(started)) != len(started) or any(name not in transaction['changes'] for name in started):
        raise Conflict('事务已开始入口清单不合法')
    if not isinstance(transaction.get('created_dirs'), list) or any(not isinstance(name, str) or not Path(name).is_absolute() for name in transaction['created_dirs']):
        raise Conflict('事务新建目录清单不合法')
    if not isinstance(transaction.get('staging', []), list):
        raise Conflict('事务暂存清单不合法')
    for item in transaction.get('staging', []):
        if not isinstance(item, dict) or item.get('path') not in transaction['changes']:
            raise Conflict('事务暂存记录不合法')
        directory = item.get('directory')
        if not isinstance(directory, str) or Path(directory).parent != Path(item['path']).parent or not Path(directory).name.startswith('.codex-config-stage-'):
            raise Conflict('事务暂存目录不合法')
        identity = item.get('identity')
        if not isinstance(identity, list) or len(identity) != 2 or any(type(number) is not int or number < 0 for number in identity):
            raise Conflict('事务暂存目录身份不合法')
        digest = item.get('previous_digest')
        if transaction.get('version', 1) >= 3 and not digest:
            raise Conflict('事务暂存原入口摘要缺失')
        known_digests = {fingerprint(transaction['changes'][item['path']][side]) for side in ('before', 'after')}
        known_digests.add(fingerprint({'kind': 'absent'}))
        if digest is not None and digest not in known_digests:
            raise Conflict('事务暂存原入口摘要不匹配')


def restore_transaction(state, transaction, check=False):
    validate_transaction(transaction)
    for item in transaction.get('staging', []):
        check_staging_item(transaction, item)
    started = transaction.get('started', list(transaction['changes']))
    observed = {}
    for name in started:
        change = transaction['changes'][name]
        current = snapshot(Path(name))
        if check and current not in (change['before'], change['after'], {'kind': 'absent'}):
            raise Conflict(f'中断后入口又被外部修改，拒绝覆盖：{name}')
        observed[name] = current
    for name in reversed(started):
        put(Path(name), transaction['changes'][name]['before'], (state, transaction), expected=observed[name])
    clean_staging(state, transaction)
    for filename, value in transaction['old_state'].items():
        restore_metadata(state / filename, value)
    (state / 'transaction.json').unlink(missing_ok=True)
    for name in sorted(transaction['created_dirs'], key=lambda s: len(Path(s).parts), reverse=True):
        try:
            Path(name).rmdir()
        except OSError:
            pass


def apply_plan(state, changes, manifest, backups, old, setup_dirs=()):
    for name, change in changes.items():
        validate_snapshot(change['before'], f'{name} 修改前')
        validate_snapshot(change['after'], f'{name} 修改后')
    if manifest:
        validate_backups(backups, manifest)
    created = set()
    for name, change in changes.items():
        if change['after']['kind'] == 'absent':
            continue
        parent = Path(name).parent
        while not exists(parent):
            created.add(str(parent))
            parent = parent.parent
    if manifest:
        manifest['created_dirs'] = sorted(set(manifest['created_dirs']) | created)
    transaction = {'version': 3, 'changes': copy.deepcopy(changes), 'started': [], 'staging': [],
                   'created_dirs': sorted(created | set(setup_dirs)),
                   'old_state': {name: snapshot(state / name) for name in ('manifest.json', 'backups.json')}}
    for change in transaction['changes'].values():
        for side in ('before', 'after'):
            change[side + '_digest'] = fingerprint(change[side])
    transaction['old_state_digests'] = {name: fingerprint(value) for name, value in transaction['old_state'].items()}
    validate_transaction(transaction)
    atomic_json(state / 'transaction.json', transaction)
    try:
        for name, change in changes.items():
            if snapshot(Path(name)) != change['before']:
                raise Conflict(f'预检后入口发生变化：{name}')
            transaction['started'].append(name)
            atomic_json(state / 'transaction.json', transaction)
            put(Path(name), change['after'], (state, transaction), expected=change['before'])
        if manifest:
            atomic_json(state / 'backups.json', backups)
            atomic_json(state / 'manifest.json', manifest)
        else:
            (state / 'manifest.json').unlink(missing_ok=True)
            (state / 'backups.json').unlink(missing_ok=True)
        (state / 'transaction.json').unlink()
    except BaseException:
        restore_transaction(state, transaction, check=True)
        raise
    if not manifest:
        for name in sorted((old or {}).get('created_dirs', []), key=lambda s: len(Path(s).parts), reverse=True):
            try:
                Path(name).rmdir()
            except OSError:
                pass


def doctor(root, repo, state, old, skills_dir=None):
    selected_skills = absolute(skills_dir or (old or {}).get('skills_dir') or root / 'skills')
    errors, warnings = [], []
    print(f'配置根：{root}\n真源：{repo}\n技能目录：{selected_skills}')
    for program in ('python3', 'git', 'rg', 'codex'):
        executable = shutil.which(program)
        version = '未发现'
        if executable:
            try:
                result = subprocess.run([executable, '--version'], text=True, capture_output=True, timeout=3)
                version = (result.stdout or result.stderr).splitlines()[0] if (result.stdout or result.stderr) else '未返回版本'
            except (OSError, subprocess.TimeoutExpired):
                version = '版本检查不可用'
        elif program == 'codex':
            warnings.append('未发现 codex CLI；不等于桌面客户端不可用，也不表示文件安装失败')
        else:
            warnings.append(f'未在 PATH 发现 {program}；相关工具命令需另行检查，当前文件完整性检查继续')
        print(f'{program}: {executable or "—"} · {version}')
    print(f'安装清单：{"存在" if old else "未安装/旧版无清单"}')
    print('Hook 信任：需在目标客户端 /hooks 审查；本脚本不修改信任状态。')
    print('技能发现：目标客户端实际加载列表才是生效证据；doctor 不迁移所选目录。')
    if (state / 'transaction.json').exists():
        errors.append('存在未完成事务，请先 recover 预览')
    if not old and exists(state / 'backups.json'):
        errors.append('存在孤立备份但缺少 manifest；先恢复清单或事务，不能重新安装覆盖')
    if (root / 'AGENTS.override.md').exists():
        warnings.append('配置根存在 AGENTS.override.md，可能替代本配置的 AGENTS.md；文件保持不变')
    installed_skills = absolute((old or {}).get('skills_dir') or root / 'skills')
    if old and selected_skills != installed_skills:
        warnings.append(f'所选技能目录与清单安装目录不同：{installed_skills}；文件完整性仍按清单核查，不自动迁移')
    alternatives = {root / 'skills', root.parent / '.agents/skills', installed_skills} - {selected_skills}
    skill_names = {source.name for source in (repo / 'skills').iterdir() if (source / 'SKILL.md').is_file()} if (repo / 'skills').is_dir() else set()
    if old:
        skill_names.update(Path(name).name for name in old['entries'] if Path(name).parent == installed_skills)
    for name in sorted(skill_names):
        if not exists(selected_skills / name):
            continue
        for alternative in sorted(alternatives):
            if exists(alternative / name):
                warnings.append(f'可能重复的技能入口：{selected_skills / name} 与 {alternative / name}')
    if old:
        if old['version'] == 1:
            warnings.append('旧清单未记录完整的历史备份摘要；仅验证结构，无法证明备份内容自安装以来未变')
        try:
            backups = read_json(state / 'backups.json', {})
            validate_backups(backups, old)
        except (Conflict, OSError, ValueError) as error:
            errors.append(f'备份不可读：{error}')
            backups = {}
        for name, entry in old['entries'].items():
            if entry['backup'] not in backups:
                errors.append(f'备份缺失：{name}')
            try:
                if name != str(root / 'hooks.json') and fingerprint(snapshot(Path(name))) != entry['installed']:
                    errors.append(f'入口漂移：{name}')
                elif Path(name).is_symlink() and not Path(name).exists():
                    errors.append(f'断链：{name}')
            except (Conflict, OSError, ValueError) as error:
                errors.append(f'入口不可读：{name}: {error}')
        try:
            without_owned(read_hooks(root / 'hooks.json'), old['owned_hooks'])
        except (Conflict, OSError, ValueError) as error:
            errors.append(f'Hook 完整性错误：{error}')
    for warning in warnings:
        print(f'警告：{warning}')
    for error in errors:
        print(f'错误：{error}')
    print(f'文件完整性：{"失败" if errors else "通过"}；{len(errors)} 项错误，{len(warnings)} 项环境/客户端发现警告')
    return 1 if errors else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'uninstall', 'doctor', 'recover'))
    parser.add_argument('--codex-home', default=os.environ.get('CODEX_HOME') or str(Path.home() / '.codex'))
    parser.add_argument('--repo', default=os.environ.get('BASE_DIR') or str(Path(__file__).resolve().parent.parent))
    parser.add_argument('--skills-dir', help='只安装到一个技能目录；默认使用已有清单或配置根/skills')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    root, repo = absolute(args.codex_home), absolute(args.repo).resolve()
    state = root / STATE
    protect_source(state, repo)
    check_parents(state / 'manifest.json', root)
    old = None if args.action == 'recover' else read_json(state / 'manifest.json')
    if old is not None:
        validate_manifest(old, root)
    elif args.action != 'recover' and exists(state / 'manifest.json'):
        raise Conflict('清单内容为空；不会视为未安装或覆盖备份。')
    if args.action == 'doctor':
        return doctor(root, repo, state, old, args.skills_dir)
    if args.action == 'recover':
        stale_lock = state / 'lock'
        if stale_lock.exists():
            try:
                owner = int((stale_lock / 'pid').read_text())
                os.kill(owner, 0)
            except ProcessLookupError:
                pass
            except (OSError, ValueError) as error:
                raise Conflict(f'无法确认安装锁已失效：{stale_lock}；请人工确认。') from error
            else:
                raise Conflict(f'安装器进程 {owner} 仍存活，未恢复。')
        transaction = read_json(state / 'transaction.json')
        if not transaction:
            print('没有待恢复事务。')
            if args.apply and stale_lock.exists():
                (stale_lock / 'pid').unlink()
                stale_lock.rmdir()
            return 0
        validate_transaction(transaction)
        print(f'恢复中断前状态：{len(transaction["changes"])} 个入口')
        if args.apply:
            restore_transaction(state, transaction, check=True)
            if stale_lock.exists():
                (stale_lock / 'pid').unlink()
                stale_lock.rmdir()
            for name in sorted(transaction['created_dirs'], key=lambda item: len(Path(item).parts), reverse=True):
                try:
                    Path(name).rmdir()
                except OSError:
                    pass
        else:
            print('预览完成；加 --apply 才会恢复。')
        return 0
    if (state / 'transaction.json').exists():
        raise Conflict('存在未完成事务。先运行 manage-codex-config.py recover [--apply]。')
    if args.action == 'uninstall' and not old:
        print('没有本安装器清单；保持所有文件，未猜测旧备份。')
        return 0
    changes, manifest, backups = build_plan(args, root, repo, state, old)
    for name, change in changes.items():
        print(f'{change["before"]["kind"]} -> {change["after"]["kind"]}: {name}')
    print(f'{args.action}: {len(changes)} 个入口变更；配置根 {root}')
    if not args.apply:
        print('仅预览；加 --apply 才会写入。备份关联清单，不按时间猜测。')
        return 0
    root_existed = root.exists()
    state_existed = state.exists()
    if manifest and not root_existed:
        manifest['created_dirs'] = sorted(set(manifest['created_dirs']) | {str(root)})
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = state / 'lock'
    try:
        lock.mkdir()
        (lock / 'pid').write_text(str(os.getpid()))
    except FileExistsError as error:
        raise Conflict(f'安装器锁已存在：{lock}；确认没有其他安装器运行后再清理锁。') from error
    try:
        # 锁内重新预检；并行安装不能使用陈旧清单覆盖彼此。
        if read_json(state / 'manifest.json') != old:
            raise Conflict('安装状态已改变，请重新预览。')
        setup_dirs = ([str(root)] if not root_existed else []) + ([str(state)] if not state_existed else [])
        apply_plan(state, changes, manifest, backups, old, setup_dirs)
    finally:
        (lock / 'pid').unlink(missing_ok=True)
        lock.rmdir()
        if not state_existed or not manifest:
            try:
                state.rmdir()
            except OSError:
                pass
        if not root_existed or (not manifest and str(root) in (old or {}).get('created_dirs', [])):
            try:
                root.rmdir()
            except OSError:
                pass
    print('已安装；请在 /hooks 审查信任，并以新任务验证技能发现。' if manifest else '已卸载本配置并恢复安装前入口；安装后新增的外来 hooks/文件保持。')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (Conflict, OSError, ValueError) as error:
        print(f'配置管理失败：{error}', file=sys.stderr)
        sys.exit(1)
