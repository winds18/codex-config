#!/usr/bin/env python3
"""Behavior regressions for the supplemental hook; dangerous text is never run."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
HOOK = ROOT_DIR / "hooks" / "codex-policy-guard.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_event(event: dict[str, object], root: Path, **environment: str) -> dict:
    env = {**os.environ, "CODEX_HOME": str(root), **environment}
    result = subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps(event), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, env=env,
    )
    return json.loads(result.stdout) if result.stdout.strip() else {}


def pre_tool(command: str, root: Path, **environment: str) -> dict:
    return run_event({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                      "tool_input": {"command": command}}, root, **environment)


def decision(output: dict) -> str | None:
    return output.get("hookSpecificOutput", {}).get("permissionDecision")


def main() -> int:
    count = 0
    with tempfile.TemporaryDirectory(prefix="codex-policy-test-") as temp:
        root = Path(temp) / "custom config"
        root.mkdir()
        (root / "AGENTS.md").symlink_to(ROOT_DIR / "AGENTS.md")
        (root / "agents").mkdir()
        (root / "skills").mkdir()
        (root / "skills" / "project-bootstrap").symlink_to(ROOT_DIR / "skills" / "project-bootstrap")
        # An unmanaged personal file in the same directory must remain editable.
        (root / "agents" / "personal.toml").write_text("# personal\n")
        for command in ("rm -rf .", "rm --recursive -- /", "rm -fr ..", "rm -r /./",
                        "echo safe && rm -rf /", "env CODEX_ALLOW_DESTRUCTIVE=1 rm -rf /",
                        "codex --yolo", "codex --dangerously-bypass-approvals-and-sandbox"):
            require(decision(pre_tool(command, root)) == "deny", f"missed: {command}")
            count += 1
        require(decision(pre_tool("rm -rf .", root, CODEX_ALLOW_DESTRUCTIVE="1")) == "deny",
                "environment variable became an approval credential")
        for command in ("printf '%s\\n' 'git reset --hard'", "echo 'rm -rf /'",
                        "printf '%s' 'codex --yolo'", "git clean -nd", "git clean -fn",
                        "git push --forceful-example", "cat <<'EOF'\nrm -rf /\nEOF",
                        "python3 -c 'print(\"git reset --hard\")'", "rm -rf ./build",
                        "rm -rf '*'", "rm -rf '$HOME'", "rm -rf '~'",
                        "'DEMO=example' rm -rf /", "'if' rm -rf /"):
            require(not pre_tool(command, root), f"false positive: {command}")
            count += 1
        for command in ("git checkout -- file.txt", "git reset --hard",
                        "git -C /tmp/project restore --worktree file.txt",
                        "git clean -fd", "git push -f origin main",
                        "git push origin +HEAD:main", "git push --force-with-lease=main:abc"):
            output = pre_tool(command, root)
            require(decision(output) is None and bool(output.get("hookSpecificOutput", {}).get("additionalContext")),
                    f"ordinary destructive Git operation must be advice, not permission: {command}")
            count += 1
        for command in (f'cp /tmp/source "{root}/AGENTS.md"',
                        f'printf x > "{root}/AGENTS.md"', f'rm -rf "{root}/skills"',
                        'tee "$CODEX_HOME/AGENTS.md"', f'mv "{root}/AGENTS.md" /tmp/moved'):
            require(decision(pre_tool(command, root)) == "deny", f"missed live target: {command}")
            count += 1
        for command in (f'cat "{root}/AGENTS.md"', f'cp "{root}/AGENTS.md" /tmp/copy',
                        f'printf "%s" "{root}/AGENTS.md"', f'printf "%s" ">" "{root}/AGENTS.md"', f'touch "{root}/agents/personal.toml"'):
            require(not pre_tool(command, root), f"blocked a read or personal file: {command}")
            count += 1
        for target in (str(root / "AGENTS.md"), "AGENTS.md"):
            for marker in ("Update File", "Move to"):
                patch = f"*** Begin Patch\n*** {marker}: {target}\n@@\n+x\n*** End Patch\n"
                output = run_event({"hook_event_name": "PreToolUse", "tool_name": "apply_patch",
                                    "tool_input": patch, "cwd": str(root)}, root)
                require(decision(output) == "deny", f"missed patch target: {target}")
                count += 1
        patch = ("*** Begin Patch\n*** Update File: /tmp/readme.md\n@@\n"
                 "+Do not run git reset --hard or rm -rf /.\n"
                 f"+Managed path: {root}/AGENTS.md\n*** End Patch\n")
        require(not run_event({"hook_event_name": "PreToolUse", "tool_name": "apply_patch",
                               "tool_input": {"input": patch}}, root), "patch body was parsed as code")
        for tool in ("Edit", "Write"):
            require(decision(run_event({"hook_event_name": "PreToolUse", "tool_name": tool,
                                       "tool_input": {"file_path": str(root / "AGENTS.md"), "content": "x"}}, root)) == "deny",
                    f"missed structured file target for {tool}")
            count += 1
        for event in ("Stop", "SubagentStop", "SessionStart", "SubagentStart", "PreCompact",
                      "PostCompact", "UserPromptSubmit", "PermissionRequest"):
            for message in ("尚未完成，需要你提供目标文件。", "已完成，测试以后再说。", "结论：未发现问题。"):
                require(not run_event({"hook_event_name": event, "last_assistant_message": message,
                                       "source": "compact"}, root), f"obsolete lifecycle intervention: {event}")
                count += 1
        require(decision(run_event({"hook_event_name": "PreToolUse", "tool_name": "exec_command",
                                    "tool_input": {"cmd": "rm -rf .", "workdir": str(root)}}, root)) == "deny",
                "exec_command alias was not inspected")
        require(not run_event({"hook_event_name": "PreToolUse", "tool_name": "Write",
                               "tool_input": {"file_path": "$CODEX_HOME/AGENTS.md"}, "cwd": str(root)}, root),
                "structured file path incorrectly received shell variable expansion")
        count += 2
        # Execute the configured entry in an isolated CODEX_HOME, including spaces.
        (root / "hooks").mkdir()
        (root / "hooks" / HOOK.name).symlink_to(HOOK)
        config = json.loads((ROOT_DIR / "hooks" / "hooks.json").read_text())
        require(set(config["hooks"]) == {"PreToolUse"}, "unexpected lifecycle hook installed")
        entry = config["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        output = subprocess.run(["/bin/sh", "-c", entry],
                                input=json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                                  "tool_input": {"command": "rm -rf ."}}),
                                text=True, capture_output=True, check=True,
                                env={**os.environ, "CODEX_HOME": str(root)})
        require(decision(json.loads(output.stdout)) == "deny", "custom CODEX_HOME hook entry failed")
    print(f"Codex hook 行为测试通过：{count + 3} 个用例。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
