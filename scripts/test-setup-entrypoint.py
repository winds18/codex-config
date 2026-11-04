#!/usr/bin/env python3
"""统一安装入口的离线集成测试；仅写 TemporaryDirectory。"""

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
import types
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SETUP = load('setup_entry', REPO / 'scripts/setup-codex-config.py')
CORE = load('setup_test_core', REPO / 'scripts/manage-codex-config.py')


class SetupEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(prefix='codex-setup-source-')
        cls.addClassCleanup(cls.fixture.cleanup)
        cls.source = Path(cls.fixture.name) / "source '目录 $literal"
        # 只复制自维护内容；上游只读资产复用，任何测试都不修改该链接目标。
        shutil.copytree(REPO, cls.source, ignore=shutil.ignore_patterns('.git', '__pycache__', 'assets'))
        (cls.source / 'skills/refero-design-prompts/assets').symlink_to(
            REPO / 'skills/refero-design-prompts/assets', target_is_directory=True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codex-setup-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "config '目录 $literal"
        self.environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')

    def invoke(self, *arguments, source=None, environment=None):
        repo = source or self.source
        return subprocess.run(['bash', str(repo / 'install.sh'), *arguments,
                               '--codex-home', str(self.root)], cwd=self.base,
                              env=environment or self.environment, text=True, capture_output=True)

    def success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def alternate_source(self):
        target = self.base / 'alternate-source'
        shutil.copytree(self.source, target, symlinks=True)
        return target

    def test_default_preview_and_check_are_read_only(self):
        for arguments in ((), ('--dry-run',), ('check',)):
            result = self.invoke(*arguments)
            self.success(result)
            self.assertFalse(self.root.exists())
        self.assertFalse(any(self.source.rglob('__pycache__')))

    def test_apply_is_idempotent_and_uninstall_restores_foreign_content(self):
        (self.root / 'agents').mkdir(parents=True)
        (self.root / 'agents/foreign.toml').write_text('foreign')
        (self.root / 'AGENTS.md').write_text('original guidance')
        (self.root / 'AGENTS.md').chmod(0o640)
        before = CORE.snapshot(self.root)
        first = self.invoke('--apply')
        self.success(first)
        self.assertIn('安装后检查', first.stdout)
        self.assertTrue((self.root / 'codex-config.sh').is_symlink())
        installed = CORE.snapshot(self.root)
        self.success(self.invoke('--apply'))
        self.assertEqual(CORE.snapshot(self.root), installed)
        self.success(self.invoke('uninstall'))
        self.assertEqual(CORE.snapshot(self.root), installed)
        self.success(self.invoke('uninstall', '--apply'))
        self.assertEqual(CORE.snapshot(self.root), before)

    def test_custom_skill_directory_and_installed_launcher_bind_the_correct_root(self):
        skills = self.base / 'selected skills'
        self.success(self.invoke('--skills-dir', str(skills), '--apply'))
        self.assertTrue((skills / 'autonomous-project-execution').is_symlink())
        decoy = self.base / 'other-config'
        environment = dict(self.environment, CODEX_HOME=str(decoy))
        launcher = self.root / 'codex-config.sh'
        result = subprocess.run(['bash', str(launcher), 'doctor'], cwd=self.base,
                                env=environment, text=True, capture_output=True)
        self.success(result)
        self.assertIn(str(self.root), result.stdout)
        self.assertIn(str(skills), result.stdout)
        result = subprocess.run(['bash', str(launcher), 'uninstall', '--apply'], cwd=self.base,
                                env=environment, text=True, capture_output=True)
        self.success(result)
        self.assertFalse(self.root.exists())
        self.assertFalse(skills.exists())
        self.assertFalse(decoy.exists())

    def test_codex_home_environment_is_respected(self):
        result = subprocess.run(['bash', str(self.source / 'install.sh'), '--apply'], cwd=self.base,
                                env=dict(self.environment, CODEX_HOME=str(self.root)), text=True, capture_output=True)
        self.success(result)
        self.assertTrue((self.root / 'AGENTS.md').is_symlink())
        self.success(self.invoke('uninstall', '--apply'))

    def test_invalid_source_stops_before_writing(self):
        source = self.alternate_source()
        failures = (
            ('agents/worker.toml', 'name = [broken'),
            ('hooks/codex-policy-guard.py', 'def invalid(:\n'),
            ('scripts/restore-codex-global-links.sh', 'if\n'),
            ('docs/client-compatibility.md', '[missing](missing-file.md)\n'),
        )
        for name, invalid in failures:
            with self.subTest(name=name):
                path = source / name
                original = path.read_text()
                try:
                    path.write_text(invalid)
                    result = self.invoke('--apply', source=source)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(self.root.exists())
                finally:
                    path.write_text(original)

    def test_missing_runtime_dependency_is_rejected(self):
        source = self.alternate_source()
        for name in ('scripts/validate-config.py',
                     'scripts/update-codex-config.py',
                     'skills/refero-design-prompts/scripts/verify-template-dependencies.py'):
            with self.subTest(name=name):
                path = source / name
                original = path.read_bytes()
                try:
                    path.unlink()
                    # 使用完整入口检查另一个来源，避免依赖恰好由入口仓库补齐。
                    result = self.invoke('--repo', str(source), '--apply')
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('安装来源不完整', result.stderr)
                    self.assertFalse(self.root.exists())
                finally:
                    path.write_bytes(original)

    def test_installed_daily_update_uses_own_root_and_uninstalls_cleanly(self):
        writer = self.base / 'update-writer'
        shutil.copytree(self.source, writer, symlinks=True)
        origin = self.base / 'update-origin.git'
        checkout = self.base / 'update-source'
        environment = {key: value for key, value in self.environment.items()
                       if not key.startswith('GIT_')}
        environment.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                           GIT_ALLOW_PROTOCOL='file', GIT_TERMINAL_PROMPT='0',
                           GIT_AUTHOR_NAME='Update Test', GIT_COMMITTER_NAME='Update Test',
                           GIT_AUTHOR_EMAIL='update@example.invalid',
                           GIT_COMMITTER_EMAIL='update@example.invalid')

        def git(directory, *arguments):
            result = subprocess.run(['git', '-C', str(directory), *arguments],
                                    text=True, capture_output=True, env=environment, timeout=20)
            self.success(result)
            return result.stdout.strip()

        git(self.base, 'init', '--bare', '--initial-branch=main', str(origin))
        git(writer, 'init', '--initial-branch=main')
        git(writer, 'add', '--all')
        git(writer, '-c', 'commit.gpgsign=false', 'commit', '-m', 'Initial configuration')
        git(writer, 'remote', 'add', 'origin', str(origin))
        git(writer, 'push', '-u', 'origin', 'main')
        git(self.base, 'clone', str(origin), str(checkout))
        skills = self.base / 'update-skills'
        self.success(self.invoke('--skills-dir', str(skills), '--apply', source=checkout,
                                 environment=dict(environment, GIT_DIR=str(writer / '.git'),
                                                  GIT_WORK_TREE=str(writer))))
        initial_receipt = json.loads((self.root / '.codex-config-state/manifest.json').read_text())
        self.assertEqual(initial_receipt['source_revision'], git(checkout, 'rev-parse', 'HEAD'))
        second = self.base / 'second-update-config'
        second_skills = self.base / 'second-update-skills'
        result = subprocess.run(['bash', str(checkout / 'install.sh'), '--apply',
                                 '--codex-home', str(second), '--skills-dir', str(second_skills)],
                                env=environment, text=True, capture_output=True, timeout=90)
        self.success(result)
        (writer / 'docs/update-proof.md').write_text('# Updated configuration\n', encoding='utf-8')
        git(writer, 'add', '--all')
        git(writer, '-c', 'commit.gpgsign=false', 'commit', '-m', 'New configuration entry')
        git(writer, 'push', 'origin', 'main')
        decoy = self.base / 'unrelated-config'
        backups_path = self.root / '.codex-config-state/backups.json'
        before_backups = backups_path.read_bytes()
        damaged = json.loads(before_backups)
        damaged[next(iter(damaged))] = {'kind': 'file', 'data': '', 'mode': 0o600}
        backups_path.write_text(json.dumps(damaged))
        rejected = subprocess.run(['bash', str(self.root / 'codex-config.sh'), 'update', '--apply'],
                                  env=environment, text=True, capture_output=True, timeout=90)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('备份摘要不匹配', rejected.stderr)
        self.assertEqual(git(checkout, 'rev-parse', 'HEAD'), initial_receipt['source_revision'])
        self.assertFalse((self.root / '.codex-config-state/daily-update.json').exists())
        backups_path.write_bytes(before_backups)
        result = subprocess.run(['bash', str(self.root / 'codex-config.sh'), 'update', '--apply'],
                                text=True, capture_output=True, cwd=self.base,
                                env=dict(environment, CODEX_HOME=str(decoy)), timeout=90)
        self.success(result)
        self.assertEqual(git(checkout, 'rev-parse', 'HEAD'), git(writer, 'rev-parse', 'HEAD'))
        self.assertTrue((self.root / 'docs/update-proof.md').is_symlink())
        self.assertTrue((skills / 'autonomous-project-execution').is_symlink())
        self.assertFalse(decoy.exists())
        state = json.loads((self.root / '.codex-config-state/daily-update.json').read_text())
        self.assertEqual(state['status'], 'updated')
        self.assertFalse((second / 'docs/update-proof.md').exists())
        result = subprocess.run(['bash', str(second / 'codex-config.sh'), 'update', '--apply'],
                                env=environment, text=True, capture_output=True, timeout=90)
        self.success(result)
        self.assertTrue((second / 'docs/update-proof.md').is_symlink())
        receipt = json.loads((second / '.codex-config-state/manifest.json').read_text())
        self.assertEqual(receipt['source_revision'], git(writer, 'rev-parse', 'HEAD'))
        self.success(self.invoke('uninstall', '--apply', source=checkout, environment=environment))
        self.assertFalse(self.root.exists())

    def test_uninstall_retains_pending_candidate_record(self):
        self.success(self.invoke('--apply'))
        candidate = self.base / 'retained candidate'
        candidate.mkdir()
        (candidate / 'evidence').write_text('interrupted validation\n')
        record = self.root / '.codex-config-state/daily-update.json'
        record.write_text(json.dumps({'candidate_path': str(candidate), 'status': 'failed'}))
        self.success(self.invoke('uninstall', '--apply'))
        self.assertTrue(candidate.exists())
        self.assertEqual(json.loads(record.read_text())['candidate_path'], str(candidate))
        self.success(self.invoke('--apply'))
        self.assertEqual(json.loads(record.read_text())['candidate_path'], str(candidate))

    def test_source_and_destination_overlap_is_rejected(self):
        before = (self.source / 'AGENTS.md').read_bytes()
        result = self.invoke('--skills-dir', str(self.source / 'skills'), '--apply')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.source / 'AGENTS.md').read_bytes(), before)
        self.assertFalse(self.root.exists())

    def test_uninstall_remains_available_when_guidance_source_is_broken(self):
        source = self.alternate_source()
        self.success(self.invoke('--apply', source=source))
        (source / 'AGENTS.md').unlink()
        self.success(self.invoke('uninstall', '--apply', source=source))
        self.assertFalse(self.root.exists())

    def test_recover_does_not_require_source_guidance_validation(self):
        source = self.alternate_source()
        (source / 'AGENTS.md').unlink()
        self.root.mkdir()
        path = self.root / 'AGENTS.md'
        before = CORE.file_value('original')
        after = CORE.file_value('interrupted')
        CORE.put(path, after)
        state = self.root / CORE.STATE
        CORE.atomic_json(state / 'transaction.json', {
            'changes': {str(path): {'before': before, 'after': after}},
            'started': [str(path)], 'created_dirs': [],
            'old_state': {'manifest.json': {'kind': 'absent'}, 'backups.json': {'kind': 'absent'}},
        })
        self.success(self.invoke('recover', source=source))
        self.assertEqual(path.read_text(), 'interrupted')
        self.success(self.invoke('recover', '--apply', source=source))
        self.assertEqual(path.read_text(), 'original')

    def test_post_install_failure_is_not_reported_as_success(self):
        real_load = SETUP.load
        def core_call(arguments):
            result = CORE.main(arguments)
            if arguments[0] == 'install':
                (self.root / 'AGENTS.md').unlink()
                (self.root / 'AGENTS.md').write_text('concurrent external change')
            return result
        def loader(name, path):
            if name == 'setup_installer':
                return types.SimpleNamespace(absolute=CORE.absolute, main=core_call, Conflict=CORE.Conflict)
            return real_load(name, path)
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(SETUP, 'load', side_effect=loader), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = SETUP.main(['--repo', str(self.source), '--codex-home', str(self.root), '--apply'])
        self.assertEqual(code, 1)
        self.assertIn('安装后检查失败', errors.getvalue())
        self.assertNotIn('文件安装及自检完成', output.getvalue())
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'concurrent external change')

    def test_apply_is_rejected_for_read_only_actions(self):
        for action in ('check', 'doctor'):
            self.assertEqual(self.invoke(action, '--apply').returncode, 2)
            self.assertFalse(self.root.exists())

    def test_archive_install_does_not_require_git_rg_or_codex(self):
        binaries = self.base / 'bin'
        binaries.mkdir()
        for name in ('bash', 'python3', 'dirname', 'basename', 'readlink'):
            (binaries / name).symlink_to(shutil.which(name))
        environment = dict(self.environment, PATH=str(binaries))
        result = self.invoke('--apply', environment=environment)
        self.success(result)
        self.assertIn('警告', result.stdout)
        self.success(self.invoke('uninstall', '--apply', environment=environment))
        self.assertFalse(self.root.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
