#!/usr/bin/env python3
"""在临时副本验证漏文件、入口、来源和媒体损坏能被静态检查发现。"""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("verify-template-dependencies.py")
spec = importlib.util.spec_from_file_location("template_dependencies", SCRIPT)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class TemplateDependenciesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="template-dependency-test-")
        cls.root = Path(cls.tmp.name) / "templates"
        shutil.copytree(scanner.DEFAULT_ROOT, cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def mutate(self, relative, replacement, expected):
        path = self.root / relative
        before = path.read_bytes()
        try:
            path.write_bytes(replacement)
            errors = scanner.inspect(self.root)[1]
            self.assertTrue(any(expected in error for error in errors), errors)
        finally:
            path.write_bytes(before)

    def test_original_snapshot_and_expected_negative_fixture(self):
        rows, errors, notes, _ = scanner.inspect(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 294)
        self.assertTrue(any("broken-image.html" in note for note in notes))

    def test_missing_relative_module(self):
        rel = "personal-homepage-skill/src/main.tsx"
        data = (self.root / rel).read_bytes().replace(b"'./App'", b"'./missing-app'")
        self.mutate(rel, data, "missing-app")

    def test_missing_script_entry(self):
        rel = "personal-homepage-skill/package.json"
        data = json.loads((self.root / rel).read_text())
        data["scripts"]["dev"] = "node scripts/missing-entry.mjs"
        self.mutate(rel, json.dumps(data).encode(), "missing-entry.mjs")

    def test_lock_disagrees_with_manifest(self):
        rel = "personal-homepage-skill/package.json"
        data = json.loads((self.root / rel).read_text())
        data["dependencies"]["react"] = "0.0.0"
        self.mutate(rel, json.dumps(data).encode(), "根声明不一致")

    def test_source_commit_mismatch(self):
        self.mutate("awesome-design-md/UPSTREAM_COMMIT", b"0" * 40, "commit 标记不匹配")

    def test_media_changed_after_header(self):
        rel = "personal-homepage-skill/templates/hero/assets/images/portrait.jpg"
        data = (self.root / rel).read_bytes() + b"changed"
        self.mutate(rel, data, "SHA-256 不符")

    def test_symlink_is_rejected_without_reading_target(self):
        link = self.root / "awesome-design-md/unexpected-link"
        link.symlink_to(self.root / "not-present")
        try:
            self.assertTrue(any("符号链接" in error for error in scanner.inspect(self.root)[1]))
        finally:
            link.unlink()


if __name__ == "__main__":
    unittest.main()
