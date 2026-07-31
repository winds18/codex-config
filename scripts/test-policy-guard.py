#!/usr/bin/env python3
"""验证全局 Codex lifecycle hook 的关键守门行为。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
HOOK = ROOT_DIR / "hooks" / "codex-policy-guard.py"


def run_event(event: dict[str, object]) -> dict[str, object]:
    env = os.environ.copy()
    env.pop("CODEX_ALLOW_DESTRUCTIVE", None)
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(event, ensure_ascii=False),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        env=env,
    )
    if not result.stdout.strip():
        return {}
    return json.loads(result.stdout)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pre_tool(command: str) -> dict[str, object]:
    return run_event(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }
    )


def pre_patch(command: str, *, cwd: str = "") -> dict[str, object]:
    return run_event(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"command": command},
            "cwd": cwd,
        }
    )


def main() -> int:
    blocked_rm = pre_tool("rm -rf .")
    require(
        blocked_rm.get("hookSpecificOutput", {}).get("permissionDecision") == "deny",
        "未阻断 rm -rf .",
    )

    blocked_override = pre_tool("CODEX_ALLOW_DESTRUCTIVE=1 git reset --hard")
    require(
        blocked_override.get("hookSpecificOutput", {}).get("permissionDecision")
        == "deny",
        "命令内绕过变量不应放行破坏性命令",
    )

    live_path = str(Path.home() / ".codex" / "AGENTS.md")
    blocked_live_write = pre_tool(
        f"python3 -c 'from pathlib import Path; Path(\"{live_path}\").write_text(\"x\")'"
    )
    require(
        blocked_live_write.get("hookSpecificOutput", {}).get("permissionDecision")
        == "deny",
        "未阻断解释器直接写 live ~/.codex 入口",
    )

    safe_patch = pre_patch(
        "*** Begin Patch\n"
        "*** Update File: /tmp/codex-config-doc.md\n"
        "@@\n"
        "+文档示例：~/.codex/AGENTS.md\n"
        "*** End Patch\n"
    )
    require(not safe_patch, "误把文档内容中的 live 路径当成补丁目标")

    blocked_patch = pre_patch(
        "*** Begin Patch\n"
        f"*** Update File: {live_path}\n"
        "@@\n"
        "+x\n"
        "*** End Patch\n"
    )
    require(
        blocked_patch.get("hookSpecificOutput", {}).get("permissionDecision")
        == "deny",
        "未阻断直接修改 live 入口的补丁目标",
    )

    blocked_relative_patch = pre_patch(
        "*** Begin Patch\n"
        "*** Update File: .codex/AGENTS.md\n"
        "@@\n"
        "+x\n"
        "*** End Patch\n",
        cwd=str(Path.home()),
    )
    require(
        blocked_relative_patch.get("hookSpecificOutput", {}).get(
            "permissionDecision"
        )
        == "deny",
        "未阻断相对路径形式的 live 补丁目标",
    )

    blocked_restore_entry = pre_tool(
        f"cp /tmp/fake {Path.home() / '.codex' / 'restore-global-setup.sh'}"
    )
    require(
        blocked_restore_entry.get("hookSpecificOutput", {}).get(
            "permissionDecision"
        )
        == "deny",
        "未保护 live 恢复入口脚本",
    )

    push_context = pre_tool("git push origin main")
    require(
        "guard"
        in push_context.get("hookSpecificOutput", {}).get("additionalContext", ""),
        "git push 前未注入 guard 要求",
    )

    compact_context = run_event(
        {"hook_event_name": "SessionStart", "source": "compact"}
    )
    require(
        "Mission"
        in compact_context.get("hookSpecificOutput", {}).get("additionalContext", ""),
        "压缩后未注入目标恢复要求",
    )

    subagent_context = run_event(
        {"hook_event_name": "SubagentStart", "agent_type": "explorer-spark"}
    )
    require(
        "关键证据"
        in subagent_context.get("hookSpecificOutput", {}).get(
            "additionalContext", ""
        ),
        "子代理启动时未注入摘要交付要求",
    )

    stop_without_verification = run_event(
        {
            "hook_event_name": "Stop",
            "stop_hook_active": False,
            "last_assistant_message": "修复已完成。",
        }
    )
    require(
        stop_without_verification.get("decision") == "block",
        "完成但无验证时未要求继续",
    )

    stop_with_verification = run_event(
        {
            "hook_event_name": "Stop",
            "stop_hook_active": False,
            "last_assistant_message": "修复已完成，测试通过。",
        }
    )
    require(not stop_with_verification, "已有验证证据时不应继续阻断")

    print("Codex lifecycle hook 策略测试通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
