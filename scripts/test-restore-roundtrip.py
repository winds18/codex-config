#!/usr/bin/env python3
"""安装器行为测试。仅使用 TemporaryDirectory，绝不访问真实 live 配置。"""
import base64
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('config_installer', SCRIPTS / 'manage-codex-config.py')
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codex-config-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "custom ' home $value"
        self.repo = self.base / 'source repo'
        for folder in ('agents', 'prompts', 'docs', 'hooks', 'skills/example', 'scripts'):
            (self.repo / folder).mkdir(parents=True)
        for path in ('AGENTS.md', 'agents/explorer.toml', 'docs/workflow.md', 'prompts/work.md', 'skills/example/SKILL.md'):
            (self.repo / path).write_text('source content\n')
        for name in ('restore-codex-global-links.sh', 'restore-codex-official-state.sh', 'manage-codex-config.py'):
            shutil.copy2(SCRIPTS / name, self.repo / 'scripts' / name)
        shutil.copy2(SCRIPTS.parent / 'hooks/codex-policy-guard.py', self.repo / 'hooks/codex-policy-guard.py')
        shutil.copy2(SCRIPTS.parent / 'hooks/hooks.json', self.repo / 'hooks/hooks.json')

    def invoke(self, action='install', *options):
        with contextlib.redirect_stdout(io.StringIO()):
            return INSTALLER.main([action, '--repo', str(self.repo), '--codex-home', str(self.root), *options])

    def original(self):
        return INSTALLER.snapshot(self.root)

    def doctor_report(self, *options):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = INSTALLER.main(['doctor', '--repo', str(self.repo), '--codex-home', str(self.root), *options])
        return code, output.getvalue()

    def test_doctor_uses_explicit_skill_directory_without_creating_it(self):
        selected = self.base / 'selected skill directory'
        code, output = self.doctor_report('--skills-dir', str(selected))
        self.assertEqual(code, 0)
        self.assertIn(f'技能目录：{INSTALLER.absolute(selected)}', output)
        self.assertFalse(selected.exists())
        self.assertFalse(self.root.exists())
        self.invoke('install', '--apply')
        before = self.original()
        code, output = self.doctor_report('--skills-dir', str(selected))
        self.assertEqual(code, 0)
        self.assertIn(f'技能目录：{INSTALLER.absolute(selected)}', output)
        self.assertIn('警告：所选技能目录与清单安装目录不同', output)
        self.assertEqual(self.original(), before)

    def test_doctor_discovery_warnings_do_not_fail_or_modify_installation(self):
        selected = self.base / '.agents/skills'
        self.invoke('install', '--skills-dir', str(selected), '--apply')
        (self.root / 'AGENTS.override.md').write_text('user override')
        (self.root / 'skills').mkdir()
        (self.root / 'skills/example').symlink_to(self.repo / 'skills/example')
        before = self.original()
        original_which = INSTALLER.shutil.which
        with patch.object(INSTALLER.shutil, 'which', side_effect=lambda program: None if program == 'codex' else original_which(program)):
            code, output = self.doctor_report('--skills-dir', str(selected))
        self.assertEqual(code, 0)
        self.assertIn('警告：配置根存在 AGENTS.override.md', output)
        self.assertIn('警告：可能重复的技能入口', output)
        self.assertIn('警告：未发现 codex CLI', output)
        self.assertIn('文件完整性：通过', output)
        self.assertNotIn('错误：', output)
        self.assertEqual(self.original(), before)

    def test_doctor_integrity_errors_return_one_without_modifying_files(self):
        self.invoke('install', '--apply')
        (self.root / 'AGENTS.md').unlink()
        (self.root / 'AGENTS.md').write_text('external modification')
        (self.root / 'hooks.json').write_text('{broken hooks')
        (self.root / INSTALLER.STATE / 'backups.json').write_text('{broken backups')
        (self.root / INSTALLER.STATE / 'transaction.json').write_text('{}')
        before = self.original()
        code, output = self.doctor_report()
        self.assertEqual(code, 1)
        for expected in ('错误：存在未完成事务', '错误：备份不可读', '错误：入口漂移', '错误：Hook 完整性错误'):
            self.assertIn(expected, output)
        self.assertIn('文件完整性：失败', output)
        self.assertEqual(self.original(), before)

    def test_optional_unified_entrypoint_is_installed_and_restored(self):
        (self.repo / 'install.sh').write_text('#!/usr/bin/env bash\nprintf "fixture"\n')
        self.root.mkdir()
        (self.root / 'codex-config.sh').write_text('user entrypoint')
        before = self.original()
        self.invoke('install', '--apply')
        self.assertTrue((self.root / 'codex-config.sh').is_symlink())
        self.assertEqual((self.root / 'codex-config.sh').resolve(), (self.repo / 'install.sh').resolve())
        manifest = json.loads((self.root / INSTALLER.STATE / 'manifest.json').read_text())
        self.assertIn(str(INSTALLER.absolute(self.root) / 'codex-config.sh'), manifest['entries'])
        self.invoke('uninstall', '--apply')
        self.assertEqual(self.original(), before)

    def test_minimal_source_without_unified_entrypoint_still_installs(self):
        self.invoke('install', '--apply')
        self.assertFalse(INSTALLER.exists(self.root / 'codex-config.sh'))
        self.invoke('uninstall', '--apply')
        self.assertFalse(self.root.exists())

    def test_config_root_cannot_overwrite_source_repository(self):
        self.root = self.repo
        before = self.original()
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('install', '--apply')
        self.assertEqual(self.original(), before)

    def test_skill_destination_cannot_overwrite_source_skills(self):
        before = INSTALLER.snapshot(self.repo)
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('install', '--skills-dir', str(self.repo / 'skills'), '--apply')
        self.assertEqual(INSTALLER.snapshot(self.repo), before)
        self.assertFalse(self.root.exists())

    def test_full_repository_shell_entrypoints_roundtrip_in_isolation(self):
        for script, options in [('restore-codex-global-links.sh', []),
                                ('restore-codex-global-links.sh', ['--apply']),
                                ('codex-config-doctor.sh', []),
                                ('restore-codex-official-state.sh', ['--apply'])]:
            result = subprocess.run(['bash', str(SCRIPTS / script), '--repo', str(SCRIPTS.parent), '--codex-home', str(self.root), *options], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            if script == 'restore-codex-global-links.sh' and not options:
                self.assertFalse(self.root.exists())
        self.assertFalse(self.root.exists())

    def test_default_preview_is_read_only(self):
        self.invoke()
        self.assertFalse(self.root.exists())
        self.invoke('uninstall')
        self.assertFalse(self.root.exists())

    def test_roundtrip_preserves_files_symlinks_modes_and_foreign_agents(self):
        (self.root / 'agents').mkdir(parents=True)
        (self.root / 'agents/foreign.toml').write_text('foreign agent')
        (self.root / 'AGENTS.md').write_text('prior')
        (self.root / 'AGENTS.md').chmod(0o640)
        (self.root / 'skills').mkdir()
        (self.root / 'skills/external').symlink_to(self.base / 'missing-external')
        (self.root / 'agents/explorer.toml').symlink_to(self.base / 'missing-original')
        (self.root / 'hooks.json').write_text('{"extra":true,"hooks":{"Stop":[{"hooks":[{"type":"command","command":"echo foreign"}]}]}}\n')
        before = self.original()
        self.invoke('install', '--apply')
        self.assertFalse((self.root / 'agents').is_symlink())
        self.assertEqual((self.root / 'agents/foreign.toml').read_text(), 'foreign agent')
        self.assertTrue((self.root / 'AGENTS.md').is_symlink())
        self.invoke('uninstall')
        self.assertTrue((self.root / 'AGENTS.md').is_symlink())
        self.invoke('uninstall', '--apply')
        self.assertEqual(self.original(), before)

    def test_empty_root_restored_to_absent(self):
        self.invoke('install', '--apply')
        self.invoke('uninstall', '--apply')
        self.assertFalse(self.root.exists())

    def test_idempotent_repeat_preserves_first_backups(self):
        self.root.mkdir()
        (self.root / 'AGENTS.md').write_text('original')
        self.invoke('install', '--apply')
        before = self.original()
        self.invoke('install', '--apply')
        self.assertEqual(self.original(), before)
        self.invoke('uninstall', '--apply')
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'original')

    def test_repository_move_updates_old_broken_links(self):
        self.invoke('install', '--apply')
        moved = self.base / 'moved repo'
        self.repo.rename(moved)
        self.repo = moved
        self.invoke('install', '--apply')
        self.assertEqual((self.root / 'AGENTS.md').resolve(), (self.repo / 'AGENTS.md').resolve())
        self.invoke('uninstall', '--apply')
        self.assertFalse(self.root.exists())

    def test_skill_directory_change_removes_managed_old_location(self):
        self.invoke('install', '--apply')
        selected = self.base / '.agents/skills'
        self.invoke('install', '--skills-dir', str(selected), '--apply')
        self.assertTrue((selected / 'example').is_symlink())
        self.assertFalse((self.root / 'skills/example').exists())
        self.invoke('uninstall', '--apply')
        self.assertFalse(selected.exists())

    def test_foreign_hook_added_after_install_survives_uninstall(self):
        self.invoke('install', '--apply')
        path = self.root / 'hooks.json'
        data = json.loads(path.read_text())
        foreign = {'hooks': [{'type': 'command', 'command': 'printf foreign'}]}
        data['hooks'].setdefault('SessionStart', []).append(foreign)
        path.write_text(json.dumps(data))
        self.invoke('install', '--apply')
        self.invoke('uninstall', '--apply')
        self.assertEqual(json.loads(path.read_text()), {'hooks': {'SessionStart': [foreign]}})

    def test_hook_command_uses_custom_root_without_runtime_environment(self):
        self.invoke('install', '--apply')
        config = json.loads((self.root / 'hooks.json').read_text())
        command = config['hooks']['PreToolUse'][0]['hooks'][0]['command']
        environment = {key: value for key, value in os.environ.items() if key != 'CODEX_HOME'}
        result = subprocess.run(command, shell=True, input=json.dumps({'hook_event_name': 'PreToolUse', 'tool_name': 'Bash', 'tool_input': {'command': 'git status'}}), text=True, capture_output=True, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('not found', result.stderr)
        self.assertIn(str(self.root), command.replace("'\"'\"'", "'"))

    def test_installed_restore_link_infers_its_own_custom_root(self):
        self.invoke('install', '--apply')
        environment = {key: value for key, value in os.environ.items() if key not in ('CODEX_HOME', 'BASE_DIR')}
        result = subprocess.run(['bash', str(self.root / 'restore-official-state.sh'), '--apply'], text=True, capture_output=True, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.root.exists())

    def test_changed_owned_hook_rejected_without_partial_mutation(self):
        self.invoke('install', '--apply')
        path = self.root / 'hooks.json'
        data = json.loads(path.read_text())
        data['hooks']['PreToolUse'][0]['hooks'][0]['command'] = 'user changed command'
        path.write_text(json.dumps(data))
        before = self.original()
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('uninstall', '--apply')
        self.assertEqual(self.original(), before)

    def test_external_entry_drift_rejected_before_any_change(self):
        self.invoke('install', '--apply')
        (self.root / 'AGENTS.md').unlink()
        (self.root / 'AGENTS.md').write_text('user changed')
        before = self.original()
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('uninstall', '--apply')
        self.assertEqual(self.original(), before)

    def test_invalid_hooks_rejected_without_partial_install(self):
        self.root.mkdir()
        (self.root / 'hooks.json').write_text('invalid json')
        before = self.original()
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('install', '--apply')
        self.assertEqual(self.original(), before)

    def test_legacy_directory_link_refused_without_touching_source(self):
        self.root.mkdir()
        (self.root / 'agents').symlink_to(self.repo / 'agents')
        before = self.original()
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('install', '--apply')
        self.assertEqual(self.original(), before)
        self.assertTrue((self.repo / 'agents/explorer.toml').is_file())

    def test_mid_install_failure_rolls_back_all_started_changes(self):
        self.root.mkdir()
        (self.root / 'AGENTS.md').write_text('original')
        before = self.original()
        real_put = INSTALLER.put
        count = 0
        def failing_put(path, value, *options, **named):
            nonlocal count
            count += 1
            if count == 4:
                raise OSError('injected write failure')
            return real_put(path, value, *options, **named)
        with patch.object(INSTALLER, 'put', side_effect=failing_put):
            with self.assertRaises(OSError):
                self.invoke('install', '--apply')
        self.assertEqual(self.original(), before)

    def test_user_edit_after_preflight_is_not_rolled_back(self):
        self.root.mkdir()
        (self.root / 'AGENTS.md').write_text('original')
        real_atomic = INSTALLER.atomic_json
        injected = False
        def concurrent_edit(path, value):
            nonlocal injected
            result = real_atomic(path, value)
            if path.name == 'transaction.json' and not injected:
                injected = True
                (self.root / 'agents').mkdir()
                (self.root / 'agents/explorer.toml').write_text('concurrent user content')
            return result
        with patch.object(INSTALLER, 'atomic_json', side_effect=concurrent_edit):
            with self.assertRaises(INSTALLER.Conflict):
                self.invoke('install', '--apply')
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'original')
        self.assertEqual((self.root / 'agents/explorer.toml').read_text(), 'concurrent user content')

    def test_journal_recovery_preserves_original(self):
        self.root.mkdir()
        path = self.root / 'AGENTS.md'
        path.write_text('before')
        before = INSTALLER.snapshot(path)
        after = {'kind': 'link', 'target': str(self.repo / 'AGENTS.md')}
        INSTALLER.put(path, after)
        state = self.root / INSTALLER.STATE
        INSTALLER.atomic_json(state / 'transaction.json', {'changes': {str(path): {'before': before, 'after': after}}, 'started': [str(path)], 'created_dirs': [], 'old_state': {'manifest.json': {'kind': 'absent'}, 'backups.json': {'kind': 'absent'}}})
        self.invoke('recover')
        self.assertTrue(path.is_symlink())
        self.invoke('recover', '--apply')
        self.assertEqual(path.read_text(), 'before')
        self.assertFalse((state / 'transaction.json').exists())

    def test_recover_uses_journal_when_manifest_is_incomplete(self):
        self.invoke('install', '--apply')
        state = self.root / INSTALLER.STATE
        original = {name: INSTALLER.snapshot(state / name) for name in ('manifest.json', 'backups.json')}
        INSTALLER.atomic_json(state / 'transaction.json', {'changes': {}, 'started': [], 'created_dirs': [], 'old_state': original})
        (state / 'manifest.json').write_text('{"partial')
        self.invoke('recover', '--apply')
        for name, saved in original.items():
            self.assertEqual(INSTALLER.snapshot(state / name), saved)
        self.assertFalse((state / 'transaction.json').exists())

    def test_empty_hook_event_roundtrip_preserves_original_bytes(self):
        self.root.mkdir()
        path = self.root / 'hooks.json'
        path.write_text('{ "hooks": { "PreToolUse": [] } }\n')
        before = self.original()
        self.invoke('install', '--apply')
        self.invoke('uninstall', '--apply')
        self.assertEqual(self.original(), before)

    def test_invalid_snapshots_are_rejected_before_any_removal(self):
        self.root.mkdir()
        victim = self.root / 'victim'
        victim.write_text('preserve this original')
        bad_values = [
            {'kind': 'unknown'},
            {'kind': 'file', 'data': '!!!!', 'mode': 0o600},
            {'kind': 'file', 'data': '', 'mode': True},
            {'kind': 'file', 'data': '', 'mode': 0o10000},
            {'kind': 'link', 'target': 'bad\0target'},
            {'kind': 'dir', 'mode': 0o700, 'children': {'../escape': INSTALLER.file_value('bad')}},
            {'kind': 'dir', 'mode': 0o700, 'children': {'file': {'kind': 'file', 'data': '!!!!', 'mode': 0o600}}},
        ]
        before = self.original()
        for value in bad_values:
            with self.subTest(value=value), self.assertRaises(INSTALLER.Conflict):
                INSTALLER.put(victim, value)
            self.assertEqual(self.original(), before)
        self.assertFalse((self.base / 'escape').exists())

    def test_corrupt_backup_bytes_never_pass_doctor_or_uninstall(self):
        self.root.mkdir()
        (self.root / 'AGENTS.md').write_text('original user guidance')
        self.invoke('install', '--apply')
        state = self.root / INSTALLER.STATE
        manifest = json.loads((state / 'manifest.json').read_text())
        key = manifest['entries'][str(INSTALLER.absolute(self.root) / 'AGENTS.md')]['backup']
        original = (state / 'backups.json').read_bytes()
        for data in ('!!!!', base64.b64encode(b'valid but corrupted content').decode()):
            with self.subTest(data=data):
                backups = json.loads(original)
                backups[key]['data'] = data
                (state / 'backups.json').write_text(json.dumps(backups))
                before = self.original()
                code, output = self.doctor_report()
                self.assertEqual(code, 1)
                self.assertIn('错误：备份不可读', output)
                self.assertEqual(self.original(), before)
                with self.assertRaises(INSTALLER.Conflict):
                    self.invoke('uninstall', '--apply')
                self.assertEqual(self.original(), before)
        (state / 'backups.json').write_bytes(original)
        self.invoke('uninstall', '--apply')
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'original user guidance')

    def test_legacy_manifest_warns_upgrades_and_cannot_drop_new_digest(self):
        self.invoke('install', '--apply')
        path = self.root / INSTALLER.STATE / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['version'] = 1
        for entry in manifest['entries'].values():
            entry.pop('backup_digest')
        path.write_text(json.dumps(manifest))
        code, output = self.doctor_report()
        self.assertEqual(code, 0)
        self.assertIn('警告：旧清单未记录完整的历史备份摘要', output)
        self.invoke('install', '--apply')
        upgraded = json.loads(path.read_text())
        self.assertEqual(upgraded['version'], 2)
        self.assertTrue(all(entry.get('backup_digest') for entry in upgraded['entries'].values()))
        next(iter(upgraded['entries'].values())).pop('backup_digest')
        path.write_text(json.dumps(upgraded))
        before = self.original()
        result = subprocess.run([sys.executable, str(SCRIPTS / 'manage-codex-config.py'), 'doctor', '--repo', str(self.repo), '--codex-home', str(self.root)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('拒绝降级验证', result.stderr)
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('install', '--apply')
        self.assertEqual(self.original(), before)

    def test_orphan_backups_are_preserved_and_block_reinstallation(self):
        self.root.mkdir()
        (self.root / 'AGENTS.md').write_text('original before first install')
        self.invoke('install', '--apply')
        (self.root / INSTALLER.STATE / 'manifest.json').unlink()
        before = self.original()
        code, output = self.doctor_report()
        self.assertEqual(code, 1)
        self.assertIn('孤立备份', output)
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('install', '--apply')
        self.assertEqual(self.original(), before)

    def test_absent_directory_child_is_rejected_even_with_matching_digest(self):
        self.prepare_original_skill_directory()
        self.invoke('install', '--apply')
        state = self.root / INSTALLER.STATE
        manifest = json.loads((state / 'manifest.json').read_text())
        entry = manifest['entries'][str(INSTALLER.absolute(self.root) / 'skills/example')]
        backups = json.loads((state / 'backups.json').read_text())
        bad = {'kind': 'dir', 'mode': 0o700, 'children': {'lost-child': {'kind': 'absent'}}}
        backups[entry['backup']] = bad
        entry['backup_digest'] = INSTALLER.fingerprint(bad)
        (state / 'manifest.json').write_text(json.dumps(manifest))
        (state / 'backups.json').write_text(json.dumps(backups))
        before = self.original()
        code, output = self.doctor_report()
        self.assertEqual(code, 1)
        self.assertIn('不存在的目录子项', output)
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('uninstall', '--apply')
        self.assertEqual(self.original(), before)

    def test_recovery_keeps_external_edit_after_global_precheck(self):
        self.root.mkdir()
        target = self.root / 'AGENTS.md'
        target.write_text('installed state')
        state = self.root / INSTALLER.STATE
        INSTALLER.atomic_json(state / 'transaction.json', {
            'changes': {str(INSTALLER.absolute(target)): {'before': INSTALLER.file_value('original state'), 'after': INSTALLER.snapshot(target)}},
            'started': [str(INSTALLER.absolute(target))], 'created_dirs': [],
            'old_state': {'manifest.json': {'kind': 'absent'}, 'backups.json': {'kind': 'absent'}},
        })
        original_snapshot = INSTALLER.snapshot
        changed = False
        def concurrent_snapshot(path):
            nonlocal changed
            captured = original_snapshot(path)
            if INSTALLER.absolute(path) == INSTALLER.absolute(target) and not changed:
                changed = True
                target.write_text('external edit after precheck')
            return captured
        with patch.object(INSTALLER, 'snapshot', side_effect=concurrent_snapshot):
            with self.assertRaises(INSTALLER.Conflict):
                self.invoke('recover', '--apply')
        self.assertEqual(target.read_text(), 'external edit after precheck')
        self.assertTrue((state / 'transaction.json').exists())

    def test_install_keeps_external_edit_between_journal_and_put(self):
        self.root.mkdir()
        target = self.root / 'AGENTS.md'
        target.write_text('original state')
        original_atomic = INSTALLER.atomic_json
        changed = False
        def concurrent_atomic(path, value):
            nonlocal changed
            result = original_atomic(path, value)
            if path.name == 'transaction.json' and value.get('started') == [str(INSTALLER.absolute(target))] and not changed:
                changed = True
                target.write_text('external edit after journal')
            return result
        with patch.object(INSTALLER, 'atomic_json', side_effect=concurrent_atomic):
            with self.assertRaises(INSTALLER.Conflict):
                self.invoke('install', '--apply')
        self.assertEqual(target.read_text(), 'external edit after journal')

    def test_move_rechecks_entry_changed_after_final_path_snapshot(self):
        self.root.mkdir()
        target = self.root / 'AGENTS.md'
        target.write_text('original state')
        original_replace = os.replace
        changed = False
        def concurrent_replace(source, destination):
            nonlocal changed
            if INSTALLER.absolute(source) == INSTALLER.absolute(target) and Path(destination).name == 'previous' and not changed:
                changed = True
                target.write_text('external edit immediately before move')
            return original_replace(source, destination)
        with patch.object(INSTALLER.os, 'replace', side_effect=concurrent_replace):
            with self.assertRaises(INSTALLER.Conflict):
                self.invoke('install', '--apply')
        self.assertEqual(target.read_text(), 'external edit immediately before move')

    def test_staged_previous_external_edit_is_retained_during_rollback_and_recovery(self):
        self.root.mkdir()
        target = self.root / 'AGENTS.md'
        target.write_text('original state')
        original_replace = os.replace
        changed = False
        held_previous = None
        def concurrent_replace(source, destination):
            nonlocal changed, held_previous
            result = original_replace(source, destination)
            if INSTALLER.absolute(destination) == INSTALLER.absolute(target) and Path(source).name == 'payload' and not changed:
                changed = True
                held_previous = Path(source).parent / 'previous'
                held_previous.write_text('external write to held previous')
            return result
        with patch.object(INSTALLER.os, 'replace', side_effect=concurrent_replace):
            with self.assertRaises(INSTALLER.Conflict):
                self.invoke('install', '--apply')
        self.assertIsNotNone(held_previous)
        self.assertEqual(held_previous.read_text(), 'external write to held previous')
        before = self.original()
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('recover', '--apply')
        self.assertEqual(self.original(), before)
        self.assertEqual(held_previous.read_text(), 'external write to held previous')

    def test_recover_validates_entire_legacy_snapshot_before_writing(self):
        self.root.mkdir()
        target = self.root / 'AGENTS.md'
        target.write_text('keep current content')
        state = self.root / INSTALLER.STATE
        INSTALLER.atomic_json(state / 'transaction.json', {
            'changes': {str(target): {'before': {'kind': 'dir', 'mode': 0o700, 'children': {'../escape': INSTALLER.file_value('bad')}}, 'after': INSTALLER.snapshot(target)}},
            'started': [str(target)], 'created_dirs': [],
            'old_state': {'manifest.json': {'kind': 'absent'}, 'backups.json': {'kind': 'absent'}},
        })
        before = self.original()
        for flags in ((), ('--apply',)):
            with self.assertRaises(INSTALLER.Conflict):
                self.invoke('recover', *flags)
            self.assertEqual(self.original(), before)
        self.assertFalse((self.base / 'escape').exists())

    def crash_directory_uninstall(self, stage):
        program = """
import importlib.util, os, sys
from pathlib import Path
module_path, repo, root, stage = sys.argv[1:]
spec = importlib.util.spec_from_file_location('crash_directory_installer', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_write = module.write_staged
original_replace = os.replace
def abrupt_write(path, value):
    result = original_write(path, value)
    if stage == 'during-payload' and path.name == 'a.txt':
        os._exit(91)
    return result
def abrupt_replace(source, destination):
    result = original_replace(source, destination)
    if stage == 'after-move' and str(source).endswith('/skills/example') and Path(destination).name == 'previous':
        os._exit(91)
    return result
module.write_staged = abrupt_write
os.replace = abrupt_replace
module.main(['uninstall', '--repo', repo, '--codex-home', root, '--apply'])
"""
        result = subprocess.run([sys.executable, '-c', program, str(SCRIPTS / 'manage-codex-config.py'), str(self.repo), str(self.root), stage], text=True, capture_output=True)
        self.assertEqual(result.returncode, 91, result.stdout + result.stderr)

    def prepare_original_skill_directory(self):
        skill = self.root / 'skills/example'
        skill.mkdir(parents=True)
        (skill / 'a.txt').write_text('first original file')
        (skill / 'b.txt').write_text('second original file')
        return skill

    def test_directory_restore_reenters_after_real_process_exit(self):
        self.prepare_original_skill_directory()
        original = self.original()
        self.invoke('install', '--apply')
        installed = self.original()
        for stage in ('during-payload', 'after-move'):
            with self.subTest(stage=stage):
                self.crash_directory_uninstall(stage)
                self.invoke('recover', '--apply')
                self.assertEqual(self.original(), installed)
                self.assertFalse(list(self.base.rglob('.codex-config-stage-*')))
        self.invoke('uninstall', '--apply')
        self.assertEqual(self.original(), original)

    def test_directory_recovery_does_not_overwrite_external_replacement(self):
        skill = self.prepare_original_skill_directory()
        self.invoke('install', '--apply')
        self.crash_directory_uninstall('during-payload')
        skill.unlink()
        skill.mkdir()
        (skill / 'foreign.txt').write_text('preserve external work')
        before = self.original()
        with self.assertRaises(INSTALLER.Conflict):
            self.invoke('recover', '--apply')
        self.assertEqual(self.original(), before)
        self.assertEqual((skill / 'foreign.txt').read_text(), 'preserve external work')

    def test_removed_source_restores_its_original_entry(self):
        self.root.mkdir()
        (self.root / 'agents').mkdir()
        (self.root / 'agents/explorer.toml').write_text('own agent')
        self.invoke('install', '--apply')
        (self.repo / 'agents/explorer.toml').unlink()
        self.invoke('install', '--apply')
        self.assertEqual((self.root / 'agents/explorer.toml').read_text(), 'own agent')


class GitHooksTests(unittest.TestCase):
    def test_linked_worktree_hook_settings_do_not_replace_main_worktree_settings(self):
        with tempfile.TemporaryDirectory(prefix='codex-worktree-hooks-test-') as directory:
            repo = Path(directory) / 'main'
            child = Path(directory) / 'child'
            subprocess.run(['git', 'init', str(repo)], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(repo), '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '--allow-empty', '-m', 'fixture'], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(repo), 'config', 'core.hooksPath', 'foreign-hooks'], check=True)
            subprocess.run(['git', '-C', str(repo), 'worktree', 'add', '-b', 'child', str(child)], check=True, capture_output=True)
            command = ['bash', str(SCRIPTS / 'install-git-hooks.sh'), '--repo', str(child), '--hooks-dir', str(SCRIPTS.parent / 'git-hooks'), '--apply']
            subprocess.run(command, check=True, capture_output=True)
            read = lambda target: subprocess.check_output(['git', '-C', str(target), 'config', '--get', 'core.hooksPath'], text=True).strip()
            self.assertEqual(read(repo), 'foreign-hooks')
            self.assertEqual(read(child), str(SCRIPTS.parent / 'git-hooks'))
            subprocess.run([*command, '--uninstall'], check=True, capture_output=True)
            self.assertEqual(read(repo), 'foreign-hooks')
            self.assertEqual(read(child), 'foreign-hooks')

    def test_process_exit_during_git_hook_install_is_recoverable(self):
        injected_program = """
import importlib.util, os, sys
module_path, repository, hooks, stage = sys.argv[1:]
spec = importlib.util.spec_from_file_location('git_installer', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_set = module.set_values
original_run = module.run
def abrupt_set(repo, scope, key, values):
    original_set(repo, scope, key, values)
    if key == 'core.hooksPath' and stage == 'after-set':
        os._exit(91)
def abrupt_run(repo, *arguments, **options):
    result = original_run(repo, *arguments, **options)
    if '--unset-all' in arguments and 'core.hooksPath' in arguments and stage == 'after-unset':
        os._exit(91)
    return result
module.set_values = abrupt_set
module.run = abrupt_run
sys.argv = [module_path, '--repo', repository, '--hooks-dir', hooks, '--apply']
module.main()
"""
        for stage in ('after-unset', 'after-set'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory(prefix='codex-git-crash-test-') as directory:
                repo = Path(directory)
                subprocess.run(['git', 'init', str(repo)], check=True, capture_output=True)
                subprocess.run(['git', '-C', str(repo), 'config', 'extensions.worktreeConfig', 'true'], check=True)
                subprocess.run(['git', '-C', str(repo), 'config', '--worktree', 'core.hooksPath', 'foreign-original'], check=True)
                result = subprocess.run([sys.executable, '-c', injected_program, str(SCRIPTS / 'manage-git-hooks.py'), str(repo), str(SCRIPTS.parent / 'git-hooks'), stage], capture_output=True)
                self.assertEqual(result.returncode, 91, result.stderr)
                self.assertTrue((repo / '.git/codex-config-hooks-pending.json').exists())
                recovery = subprocess.run(['bash', str(SCRIPTS / 'install-git-hooks.sh'), '--repo', str(repo), '--recover', '--apply'], text=True, capture_output=True)
                self.assertEqual(recovery.returncode, 0, recovery.stdout + recovery.stderr)
                restored = subprocess.check_output(['git', '-C', str(repo), 'config', '--worktree', '--get', 'core.hooksPath'], text=True).strip()
                self.assertEqual(restored, 'foreign-original')
                self.assertFalse((repo / '.git/codex-config-hooks-pending.json').exists())
                self.assertFalse((repo / '.git/codex-config-hooks-lock').exists())

    def test_original_hooks_path_preserves_spaces_and_newlines(self):
        with tempfile.TemporaryDirectory(prefix='codex-git-path-test-') as directory:
            repo = Path(directory)
            subprocess.run(['git', 'init', str(repo)], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(repo), 'config', 'extensions.worktreeConfig', 'true'], check=True)
            original = ' custom hooks\nwith newline '
            subprocess.run(['git', '-C', str(repo), 'config', '--worktree', 'core.hooksPath', original], check=True)
            command = ['bash', str(SCRIPTS / 'install-git-hooks.sh'), '--repo', str(repo), '--hooks-dir', str(SCRIPTS.parent / 'git-hooks'), '--apply']
            subprocess.run(command, check=True, capture_output=True)
            subprocess.run([*command, '--uninstall'], check=True, capture_output=True)
            actual = subprocess.check_output(['git', '-C', str(repo), 'config', '--null', '--worktree', '--get', 'core.hooksPath'])
            self.assertEqual(actual, original.encode() + b'\0')

    def test_preview_install_idempotence_and_uninstall_in_temporary_repository(self):
        with tempfile.TemporaryDirectory(prefix='codex-git-hooks-test-') as directory:
            repo = Path(directory)
            subprocess.run(['git', 'init', str(repo)], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(repo), 'config', 'core.hooksPath', 'foreign-hooks'], check=True)
            command = ['bash', str(SCRIPTS / 'install-git-hooks.sh'), '--repo', str(repo), '--hooks-dir', str(SCRIPTS.parent / 'git-hooks')]
            config = (repo / '.git/config').read_bytes()
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual((repo / '.git/config').read_bytes(), config)
            for _ in range(2):
                subprocess.run([*command, '--apply'], check=True, capture_output=True)
            active = subprocess.check_output(['git', '-C', str(repo), 'config', '--worktree', '--get', 'core.hooksPath'], text=True).strip()
            self.assertEqual(active, str(SCRIPTS.parent / 'git-hooks'))
            subprocess.run([*command, '--uninstall', '--apply'], check=True, capture_output=True)
            restored = subprocess.check_output(['git', '-C', str(repo), 'config', '--get', 'core.hooksPath'], text=True).strip()
            self.assertEqual(restored, 'foreign-hooks')
            self.assertFalse((repo / '.git/config.worktree').exists())
            self.assertFalse((repo / '.git/codex-config-hooks.json').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
