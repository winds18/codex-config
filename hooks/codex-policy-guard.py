#!/usr/bin/env python3
"""用于全局工作流安全守门的 Codex hook。"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any


DESTRUCTIVE_PATTERNS = [
    (r"\brm\s+-[^\n;&|]*[rf][^\n;&|]*\s+(/|~|\$HOME)(\s|$)", "refuse broad rm against home/root"),
    (r"\bsudo\s+rm\b", "refuse sudo rm"),
    (r"\bgit\s+reset\s+--hard\b", "refuse git reset --hard"),
    (r"\bgit\s+clean\s+-[^\n;&|]*[fdx]", "refuse git clean destructive flags"),
    (r"\bgit\s+checkout\s+--\b", "refuse git checkout -- destructive restore"),
    (r"\bgit\s+restore\s+(\.|\*)\b", "refuse broad git restore"),
    (r"\bgit\s+push\b[^\n;&|]*(--force|-f)\b", "refuse force push"),
    (r"\bchmod\s+-R\s+777\b", "refuse recursive chmod 777"),
    (r"--dangerously-bypass|danger-full-access|--yolo\b", "refuse bypassing sandbox/approvals"),
]

SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9_-]{20,}", "OpenAI-style API key"),
    (r"ghp_[A-Za-z0-9_]{20,}", "GitHub personal token"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "GitHub fine-grained token"),
    (r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "private key block"),
    (r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{24,}", "inline secret"),
]

COMPLETION_WORDS = re.compile(
    r"(已完成|完成了|修复了|处理好了|done\b|fixed\b|complete\b|completed\b)",
    re.IGNORECASE,
)
VERIFICATION_WORDS = re.compile(
    r"(验证|校验|测试|test|lint|build|typecheck|dry-run|bash -n|exit code 0|通过|passed|pass\b|0 failures)",
    re.IGNORECASE,
)


def read_event() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def block_pre_tool(reason: str) -> None:
    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )


def block_permission(reason: str) -> None:
    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "behavior": "deny",
                    "message": reason,
                },
            }
        }
    )


def block_prompt(reason: str) -> None:
    emit({"decision": "block", "reason": reason})


def continue_turn(reason: str) -> None:
    emit({"decision": "block", "reason": reason})


def command_from_tool_input(tool_input: Any) -> str:
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command
    if isinstance(tool_input, str):
        return tool_input
    return ""


def has_override(text: str) -> bool:
    return "CODEX_ALLOW_DESTRUCTIVE=1" in text or os.environ.get("CODEX_ALLOW_DESTRUCTIVE") == "1"


def high_confidence_secret(text: str) -> str | None:
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, text):
            return label
    return None


def destructive_reason(command: str) -> str | None:
    if has_override(command):
        return None
    for pattern, label in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, command):
            return f"Blocked by global Codex policy: {label}. If this is intentional, stop and get explicit human approval before using CODEX_ALLOW_DESTRUCTIVE=1."
    return None


def writes_live_codex_entry(command: str) -> bool:
    if "restore-codex-global-links.sh" in command or "restore-global-setup.sh" in command:
        return False

    live_entry = re.search(
        r"(\$HOME|~|/Users/[^/\s]+)?/\.codex/(AGENTS\.md|agents|docs|prompts|skills|hooks|hooks\.json)",
        command,
    )
    if not live_entry:
        return False

    write_intent = re.search(
        r"(\b(rm|mv|cp|ln|touch|mkdir|chmod|chown)\b|\bsed\s+-i\b|\bperl\s+-pi\b|\btee\b|>>|>)",
        command,
    )
    return bool(write_intent or command.lstrip().startswith("*** Begin Patch"))


def handle_user_prompt(event: dict[str, Any]) -> None:
    prompt = str(event.get("prompt") or "")
    label = high_confidence_secret(prompt)
    if label:
        block_prompt(f"Blocked by global Codex policy: prompt appears to contain a {label}. Use a local env file or credential store instead of pasting secrets into the thread.")


def handle_pre_tool(event: dict[str, Any]) -> None:
    tool_name = str(event.get("tool_name") or "")
    command = command_from_tool_input(event.get("tool_input"))
    if not command:
        return

    reason = destructive_reason(command)
    if reason:
        block_pre_tool(reason)
        return

    if tool_name in {"Bash", "apply_patch"} and writes_live_codex_entry(command):
        block_pre_tool(
            "Blocked by global Codex policy: edit the codex-config source repo and run restore-codex-global-links.sh instead of directly modifying live ~/.codex entrypoints."
        )
        return

    if re.search(r"\bgit\s+push\b", command):
        emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": "Before pushing, run the repository guard script and report its result.",
                }
            }
        )


def handle_permission_request(event: dict[str, Any]) -> None:
    command = command_from_tool_input(event.get("tool_input"))
    if not command:
        return
    reason = destructive_reason(command)
    if reason:
        block_permission(reason)


def handle_stop(event: dict[str, Any]) -> None:
    if event.get("stop_hook_active"):
        return
    last = str(event.get("last_assistant_message") or "")
    if COMPLETION_WORDS.search(last) and not VERIFICATION_WORDS.search(last):
        continue_turn(
            "Before claiming completion, run or cite the closest practical verification. If verification is impossible, state exactly what was not verified and why."
        )


def main() -> int:
    event = read_event()
    name = str(event.get("hook_event_name") or "")

    if name == "UserPromptSubmit":
        handle_user_prompt(event)
    elif name == "PreToolUse":
        handle_pre_tool(event)
    elif name == "PermissionRequest":
        handle_permission_request(event)
    elif name == "Stop":
        handle_stop(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
