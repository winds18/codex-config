#!/usr/bin/env python3
"""Offline integration tests for daily source updates using real Git repositories."""

import contextlib
import fcntl
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

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('config_update', REPO / 'scripts/update-codex-config.py')
UPDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UPDATE)
DAY = 24 * 60 * 60
NOW = 1_800_000_000


class ConfigUpdateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='codex-update-test-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.origin = self.base / 'origin.git'
        self.repo = self.base / 'installed source'
        self.writer = self.base / 'writer'
        self.root = self.base / 'config root'
        self.home = self.base / 'home'
        self.home.mkdir()
        environment = {
            'HOME': str(self.home), 'XDG_CONFIG_HOME': str(self.home),
            'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
            'GIT_ALLOW_PROTOCOL': 'file', 'GIT_TERMINAL_PROMPT': '0',
            'GIT_AUTHOR_NAME': 'Update Test', 'GIT_AUTHOR_EMAIL': 'update@example.invalid',
            'GIT_COMMITTER_NAME': 'Update Test', 'GIT_COMMITTER_EMAIL': 'update@example.invalid',
            'GIT_CONFIG_COUNT': '0', 'GIT_ATTR_NOSYSTEM': '1',
        }
        # Git routing inherited from a caller must not escape the temporary fixture.
        isolated = {key: value for key, value in os.environ.items()
                    if not key.startswith('GIT_')}
        isolated.update(environment)
        environment_patch = patch.dict(os.environ, isolated, clear=True)
        environment_patch.start()
        self.addCleanup(environment_patch.stop)
        self.git(self.base, 'init', '--bare', '--initial-branch=main', str(self.origin))
        self.git(self.base, 'clone', str(self.origin), str(self.writer))
        (self.writer / 'AGENTS.md').write_text('original guidance\n', encoding='utf-8')
        self.commit(self.writer, 'Initial source')
        self.git(self.writer, 'push', '-u', 'origin', 'main')
        self.git(self.base, 'clone', str(self.origin), str(self.repo))
        self.old = self.head()
        self.state_dir = self.root / '.codex-config-state'
        self.state_dir.mkdir(parents=True)
        (self.state_dir / 'manifest.json').write_text(
            json.dumps({'source_revision': self.old}), encoding='utf-8')
        (self.root / 'AGENTS.md').symlink_to(self.repo / 'AGENTS.md')
        self.checks = []
        self.installs = []

    def git(self, directory, *arguments):
        result = subprocess.run(['git', '-C', str(directory), *arguments],
                                text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def commit(self, repo, message):
        self.git(repo, 'add', '--all')
        self.git(repo, '-c', 'commit.gpgsign=false', 'commit', '-m', message)
        return self.git(repo, 'rev-parse', 'HEAD')

    def head(self):
        return self.git(self.repo, 'rev-parse', 'HEAD')

    def publish(self):
        (self.writer / 'new-config.txt').write_text('new configuration\n', encoding='utf-8')
        (self.writer / 'AGENTS.md').write_text('updated guidance\n', encoding='utf-8')
        target = self.commit(self.writer, 'Update source')
        self.git(self.writer, 'push', 'origin', 'main')
        return target

    def check(self, candidate):
        candidate = Path(candidate)
        self.checks.append(candidate)
        self.assertNotEqual(candidate.resolve(), self.repo.resolve())
        self.assertEqual(self.head(), self.old)
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'original guidance\n')
        self.assertEqual((candidate / 'new-config.txt').read_text(), 'new configuration\n')

    def install(self, repo, root):
        self.installs.append((Path(repo), Path(root)))
        self.assertEqual((Path(repo), Path(root)), (self.repo, self.root))
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'updated guidance\n')
        self.assertEqual((Path(repo) / 'new-config.txt').read_text(), 'new configuration\n')
        return 0

    def invoke(self, *, apply=True, now=NOW, check=None, install=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = UPDATE.update(self.repo, self.root, apply=apply,
                                 check_source=check or self.check,
                                 install_source=install or self.install, now=now)
        self.assertTrue(output.getvalue().strip())
        return code

    def state(self):
        return json.loads((self.state_dir / 'daily-update.json').read_text())

    def assert_reclaimed(self):
        self.assertTrue(all(not candidate.exists() for candidate in self.checks))
        self.assertTrue(all(not candidate.parent.exists() for candidate in self.checks))
        worktrees = self.git(self.repo, 'worktree', 'list', '--porcelain')
        self.assertEqual(sum(line.startswith('worktree ') for line in worktrees.splitlines()), 1)
        self.assertEqual(self.git(self.repo, 'status', '--porcelain'), '')

    def snapshot(self):
        return {str(path.relative_to(self.base)):
                ('link', os.readlink(path)) if path.is_symlink() else ('file', path.read_bytes())
                for path in self.base.rglob('*') if path.is_symlink() or path.is_file()}

    def test_preview_is_read_only_without_git_or_callbacks(self):
        self.publish()
        before = self.snapshot()
        with patch.object(subprocess, 'run', side_effect=AssertionError('preview ran a command')) as run:
            self.assertEqual(self.invoke(apply=False), 0)
        run.assert_not_called()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])
        self.assertFalse((self.state_dir / 'daily-update.json').exists())

    def test_up_to_date_fetch_is_bounded_noninteractive_and_local(self):
        real_run = subprocess.run
        fetches = []

        def observe(command, **kwargs):
            if 'fetch' in command:
                fetches.append(command)
                self.assertGreater(kwargs.get('timeout', 0), 0)
                self.assertLessEqual(kwargs['timeout'], 120)
                environment = kwargs.get('env', os.environ)
                self.assertEqual(environment.get('GIT_TERMINAL_PROMPT'), '0')
                self.assertEqual(environment.get('GIT_ALLOW_PROTOCOL'), 'file')
                self.assertIn('origin', command)
                self.assertIn('refs/heads/main', command)
            return real_run(command, **kwargs)

        with patch.object(subprocess, 'run', side_effect=observe):
            self.assertEqual(self.invoke(), 0)
        self.assertEqual(len(fetches), 1)
        self.assertEqual(self.head(), self.old)
        self.assertEqual(self.state()['status'], 'up_to_date')
        self.assertEqual(self.state()['last_attempt'], NOW)
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])
        self.assert_reclaimed()

    def test_unknown_receipt_does_not_reuse_old_success_record(self):
        (self.state_dir / 'manifest.json').write_text(json.dumps({'source_revision': None}))
        (self.state_dir / 'daily-update.json').write_text(json.dumps({
            'last_attempt': NOW - DAY, 'installed_head': self.old,
            'validated_head': self.old, 'status': 'updated'}))
        applied = []
        self.assertEqual(self.invoke(install=lambda repo, root: applied.append(root) or 0), 0)
        self.assertEqual(applied, [self.root])
        self.assertEqual(self.state()['status'], 'updated')
        self.assert_reclaimed()

    def test_fast_forward_validates_then_installs_and_reclaims_candidate(self):
        target = self.publish()
        self.assertEqual(self.invoke(), 0)
        self.assertEqual(self.head(), target)
        self.assertEqual(len(self.checks), 1)
        self.assertEqual(len(self.installs), 1)
        self.assertEqual(self.state()['status'], 'updated')
        self.assertEqual(self.state()['old_head'], self.old)
        self.assertEqual(self.state()['new_head'], target)
        self.assertFalse(self.state()['pending_install'])
        self.assertEqual(self.git(self.repo, 'rev-parse', 'refs/codex-config/previous'), self.old)
        self.assert_reclaimed()

    def test_success_throttles_until_full_day_then_retries(self):
        self.assertEqual(self.invoke(), 0)
        target = self.publish()
        saved = self.state()
        with patch.object(subprocess, 'run', wraps=subprocess.run) as run:
            self.assertEqual(self.invoke(now=NOW + DAY - 1), 0)
        self.assertFalse(any('fetch' in call.args[0] for call in run.call_args_list))
        self.assertEqual(self.state(), saved)
        self.assertEqual(self.head(), self.old)
        self.assertEqual(self.invoke(now=NOW + DAY), 0)
        self.assertEqual(self.head(), target)
        self.assertEqual(self.state()['last_attempt'], NOW + DAY)
        self.assert_reclaimed()

    def test_validation_failure_is_throttled_and_retry_can_succeed(self):
        target = self.publish()

        def reject(candidate):
            self.check(candidate)
            raise ValueError('candidate rejected')

        self.assertEqual(self.invoke(check=reject), 1)
        self.assertEqual(self.head(), self.old)
        self.assertEqual(self.state()['status'], 'failed')
        self.assertEqual(self.installs, [])
        self.assert_reclaimed()
        saved = self.state()
        with patch.object(subprocess, 'run', wraps=subprocess.run) as run:
            self.assertEqual(self.invoke(now=NOW + DAY - 1), 0)
        self.assertFalse(any('fetch' in call.args[0] for call in run.call_args_list))
        self.assertEqual(self.state(), saved)
        self.assertEqual(len(self.checks), 1)
        self.assertEqual(self.invoke(now=NOW + DAY), 0)
        self.assertEqual(self.head(), target)
        self.assert_reclaimed()

    def test_dirty_source_blocks_without_fetch_or_overwrite(self):
        self.publish()
        (self.repo / 'AGENTS.md').write_text('local edits\n')
        (self.repo / 'untracked.txt').write_text('keep me\n')
        with patch.object(subprocess, 'run', wraps=subprocess.run) as run:
            self.assertEqual(self.invoke(), 1)
        self.assertFalse(any('fetch' in call.args[0] for call in run.call_args_list))
        self.assertEqual(self.head(), self.old)
        self.assertEqual((self.repo / 'AGENTS.md').read_text(), 'local edits\n')
        self.assertEqual((self.repo / 'untracked.txt').read_text(), 'keep me\n')
        self.assertEqual(self.state()['status'], 'failed')
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])

    def test_caller_git_routing_cannot_redirect_update_to_another_checkout(self):
        target = self.publish()
        writer_before = self.git(self.writer, 'status', '--porcelain')
        with patch.dict(os.environ, GIT_DIR=str(self.writer / '.git'),
                        GIT_WORK_TREE=str(self.writer),
                        GIT_INDEX_FILE=str(self.writer / '.git/index')):
            self.assertEqual(self.invoke(check=lambda path: None,
                                         install=lambda repo, root: 0), 0)
        self.assertEqual(self.head(), target)
        self.assertEqual(self.state()['status'], 'updated')
        self.assertEqual(self.git(self.writer, 'status', '--porcelain'), writer_before)
        self.assert_reclaimed()

    def test_source_subdirectory_cannot_update_its_parent_repository(self):
        nested = self.repo / 'embedded'
        nested.mkdir()
        (nested / 'AGENTS.md').write_text('nested guidance\n')
        original = self.commit(self.repo, 'Embedded configuration')
        (self.root / 'AGENTS.md').unlink()
        (self.root / 'AGENTS.md').symlink_to(nested / 'AGENTS.md')
        (self.state_dir / 'manifest.json').write_text(json.dumps({'source_revision': original}))
        with contextlib.redirect_stdout(io.StringIO()):
            with patch.object(subprocess, 'run', wraps=subprocess.run) as run:
                result = UPDATE.update(nested, self.root, apply=True, now=NOW,
                                       check_source=lambda path: None,
                                       install_source=lambda repo, root: 0)
        self.assertEqual(result, 1)
        self.assertFalse(any('fetch' in call.args[0] for call in run.call_args_list))
        self.assertEqual(self.head(), original)

    def test_divergence_preserves_local_commit(self):
        self.publish()
        (self.repo / 'local.txt').write_text('local commit\n')
        local = self.commit(self.repo, 'Local change')
        self.assertEqual(self.invoke(), 1)
        self.assertEqual(self.head(), local)
        self.assertEqual(self.state()['status'], 'failed')
        self.assertEqual(self.state()['old_head'], local)
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])
        self.assert_reclaimed()

    def test_local_ahead_reconciles_installation_without_losing_commit(self):
        (self.repo / 'local.txt').write_text('local commit\n')
        local = self.commit(self.repo, 'Local change')

        def check_current(source):
            self.assertEqual(source, self.repo)
            self.assertEqual((source / 'local.txt').read_text(), 'local commit\n')

        def install_current(source, root):
            self.assertEqual((source, root), (self.repo, self.root))
            return 0

        self.assertEqual(self.invoke(check=check_current, install=install_current), 0)
        self.assertEqual(self.head(), local)
        self.assertEqual(self.state()['status'], 'updated')
        self.assertEqual(self.state()['installed_head'], local)
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])
        self.assert_reclaimed()

    def test_install_failure_keeps_fast_forward_and_recovery_heads(self):
        target = self.publish()

        def fail_install(repo, root):
            self.install(repo, root)
            self.assertTrue(self.state()['pending_install'])
            return 1

        self.assertEqual(self.invoke(install=fail_install), 1)
        self.assertEqual(self.head(), target)
        self.assertEqual(self.state()['status'], 'failed')
        self.assertEqual(self.state()['old_head'], self.old)
        self.assertEqual(self.state()['new_head'], target)
        self.assertTrue(self.state()['pending_install'])
        self.assertEqual(self.git(self.repo, 'rev-parse', 'refs/codex-config/previous'), self.old)
        self.assertEqual(len(self.installs), 1)
        self.assert_reclaimed()
        saved = self.state()
        self.assertEqual(self.invoke(now=NOW + DAY - 1), 0)
        self.assertEqual(self.state(), saved)
        self.assertEqual(len(self.installs), 1)
        self.assertEqual(self.invoke(now=NOW + DAY), 0)
        self.assertEqual(self.head(), target)
        self.assertEqual(len(self.checks), 1)
        self.assertEqual(len(self.installs), 2)
        self.assertEqual(self.state()['status'], 'updated')
        self.assertFalse(self.state()['pending_install'])
        self.assertEqual(self.git(self.repo, 'rev-parse', 'refs/codex-config/previous'), self.old)
        self.assert_reclaimed()

    def test_detached_head_is_rejected_without_fetch(self):
        self.git(self.repo, 'checkout', '--detach')
        with patch.object(subprocess, 'run', wraps=subprocess.run) as run:
            self.assertEqual(self.invoke(), 1)
        self.assertFalse(any('fetch' in call.args[0] for call in run.call_args_list))
        self.assertEqual(self.head(), self.old)
        self.assertEqual(self.state()['status'], 'failed')
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])
        self.assert_reclaimed()

    def test_missing_upstream_is_rejected_without_fetch(self):
        self.git(self.repo, 'branch', '--unset-upstream')
        with patch.object(subprocess, 'run', wraps=subprocess.run) as run:
            self.assertEqual(self.invoke(), 1)
        self.assertFalse(any('fetch' in call.args[0] for call in run.call_args_list))
        self.assertEqual(self.head(), self.old)
        self.assertEqual(self.state()['status'], 'failed')
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])
        self.assert_reclaimed()

    def test_missing_manifest_and_foreign_source_are_rejected(self):
        manifest = self.state_dir / 'manifest.json'
        entry = self.root / 'AGENTS.md'
        for failure in ('missing_manifest', 'foreign_source', 'regular_entry'):
            with self.subTest(failure=failure):
                manifest.write_text('{}\n')
                entry.unlink()
                entry.symlink_to(self.repo / 'AGENTS.md')
                if failure == 'missing_manifest':
                    manifest.unlink()
                elif failure == 'foreign_source':
                    entry.unlink()
                    entry.symlink_to(self.writer / 'AGENTS.md')
                else:
                    entry.unlink()
                    entry.write_text('not managed\n')
                before = self.snapshot()
                with patch.object(subprocess, 'run', wraps=subprocess.run) as run:
                    self.assertEqual(self.invoke(), 1)
                self.assertFalse(any('fetch' in call.args[0] for call in run.call_args_list))
                self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])

    def test_same_source_lock_skips_without_attempt(self):
        self.publish()
        common = Path(self.git(self.repo, 'rev-parse', '--git-common-dir'))
        if not common.is_absolute():
            common = self.repo / common
        with (common / 'codex-config-update.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(self.invoke(), 0)
        self.assertEqual(self.head(), self.old)
        self.assertFalse((self.state_dir / 'daily-update.json').exists())
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])
        self.assertEqual(self.invoke(), 0)
        self.assert_reclaimed()

    def test_candidate_time_source_change_blocks_activation(self):
        self.publish()

        def concurrent_edit(candidate):
            self.check(candidate)
            (self.repo / 'concurrent.txt').write_text('external change\n')

        self.assertEqual(self.invoke(check=concurrent_edit), 1)
        self.assertEqual(self.head(), self.old)
        self.assertEqual(self.state()['status'], 'failed')
        self.assertEqual(self.installs, [])
        self.assertTrue(all(not candidate.exists() for candidate in self.checks))
        self.assertEqual((self.repo / 'concurrent.txt').read_text(), 'external change\n')
        self.assertEqual(self.git(self.repo, 'worktree', 'list', '--porcelain').count('worktree '), 1)

    def test_killed_preflight_leaves_record_and_blocks_new_candidates(self):
        target = self.publish()
        script = (
            'import importlib.util, os; from pathlib import Path; '
            f's = importlib.util.spec_from_file_location("updater", {str(REPO / "scripts/update-codex-config.py")!r}); '
            'm = importlib.util.module_from_spec(s); s.loader.exec_module(m); '
            f'm.update(Path({str(self.repo)!r}), Path({str(self.root)!r}), apply=True, now={NOW}, '
            'check_source=lambda p: os._exit(9), install_source=lambda r, c: 0)'
        )
        result = subprocess.run([sys.executable, '-B', '-c', script],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 9)
        candidate = Path(self.state()['candidate_path'])

        def cleanup():
            if UPDATE.registered(self.repo, candidate):
                self.git(self.repo, 'worktree', 'remove', str(candidate))
            if candidate.parent.exists():
                shutil.rmtree(candidate.parent)

        self.addCleanup(cleanup)
        self.assertTrue(candidate.exists())
        self.assertEqual(self.head(), self.old)
        self.assertEqual(self.invoke(now=NOW + DAY), 1)
        self.assertEqual(self.state()['candidate_path'], str(candidate))
        self.assertEqual(self.git(self.repo, 'worktree', 'list', '--porcelain').count('worktree '), 2)
        # Missing directory does not erase the Git registration or permit another candidate.
        shutil.rmtree(candidate.parent)
        self.assertTrue(UPDATE.registered(self.repo, candidate))
        self.assertEqual(self.invoke(now=NOW + DAY), 1)
        cleanup()
        self.assertEqual(self.invoke(now=NOW + DAY), 0)
        self.assertEqual(self.head(), target)
        self.assertNotIn('candidate_path', self.state())
        self.assert_reclaimed()

    def test_worktree_add_timeout_cleans_registered_candidate(self):
        self.publish()
        original = UPDATE.git

        def timeout_after_add(repo, *arguments):
            output = original(repo, *arguments)
            if arguments[:2] == ('worktree', 'add'):
                raise subprocess.TimeoutExpired(['git', *arguments], 120)
            return output

        with patch.object(UPDATE, 'git', side_effect=timeout_after_add):
            self.assertEqual(self.invoke(), 1)
        self.assertEqual(self.head(), self.old)
        self.assertNotIn('candidate_path', self.state())
        self.assert_reclaimed()

    def test_fetch_timeout_is_caught_and_throttled(self):
        real_run = subprocess.run

        def timeout(command, **kwargs):
            if 'fetch' in command:
                raise subprocess.TimeoutExpired(command, kwargs['timeout'])
            return real_run(command, **kwargs)

        with patch.object(subprocess, 'run', side_effect=timeout):
            self.assertEqual(self.invoke(), 1)
        self.assertEqual(self.head(), self.old)
        self.assertEqual(self.state()['status'], 'failed')
        saved = self.state()
        with patch.object(subprocess, 'run', wraps=subprocess.run) as run:
            self.assertEqual(self.invoke(now=NOW + 1), 0)
        self.assertFalse(any('fetch' in call.args[0] for call in run.call_args_list))
        self.assertEqual(self.state(), saved)
        self.assertEqual(self.checks, [])
        self.assertEqual(self.installs, [])


if __name__ == '__main__':
    unittest.main()
