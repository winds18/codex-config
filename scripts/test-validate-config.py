#!/usr/bin/env python3
"""Validate role fields in an isolated source fixture."""

import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "validate_config", Path(__file__).with_name("validate-config.py"))
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class AgentConfigTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="codex-role-validation-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / "agents").mkdir()
        (self.root / "hooks").mkdir()
        (self.root / "hooks/hooks.json").write_text('{"hooks": {}}', encoding="utf-8")
        for name in ("AGENTS.md", "AGENTS.override.md", "README.md"):
            (self.root / name).write_text("", encoding="utf-8")
        self.role = self.root / "agents/reviewer.toml"
        self.source = ('name = "reviewer"\ndescription = "Review changes"\n'
                       'developer_instructions = "Do not edit files"\n')

    def check_role(self, extra=""):
        self.role.write_text(self.source + extra, encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            VALIDATOR.check(self.root)

    def test_minimal_role_without_permission_overrides_is_valid(self):
        self.check_role()

    def test_supported_model_overrides_are_valid(self):
        self.check_role('model = "available-model"\nmodel_reasoning_effort = "medium"\n')

    def test_ineffective_parent_setting_overrides_are_rejected(self):
        for field, value in (("sandbox_mode", "read-only"),
                             ("approval_policy", "never"),
                             ("model_provider", "openai"),
                             ("mcp_servers", "external")):
            with self.subTest(field=field):
                with self.assertRaises(ValueError) as raised:
                    self.check_role(f'{field} = "{value}"\n')
                self.assertIn(field, str(raised.exception))

    def test_unknown_role_field_is_rejected(self):
        with self.assertRaises(ValueError):
            self.check_role('unknown_setting = "value"\n')


if __name__ == "__main__":
    unittest.main()
