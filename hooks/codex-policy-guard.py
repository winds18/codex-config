#!/usr/bin/env python3
"""用于全局工作流安全守门的 Codex hook。"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any


DESTRUCTIVE_PATTERNS = [
    (
        r"\brm\s+-[^\n;&|]*[rR][^\n;&|]*\s+"
        r"(/|~|\$HOME|\$\{HOME\}|\.{1,2}(?:/|\s|$)|\*)(?:\s|$)",
        "禁止对根目录、home、当前目录、上级目录或通配目标执行递归删除",
    ),
    (r"\bsudo\s+rm\b", "禁止使用 sudo rm"),
    (r"\bgit\s+reset\s+--hard\b", "禁止 git reset --hard"),
    (r"\bgit\s+clean\s+-[^\n;&|]*[fdx]", "禁止破坏性 git clean"),
    (r"\bgit\s+checkout\s+--\b", "禁止使用 git checkout -- 丢弃改动"),
    (
        r"\bgit\s+restore\s+(?:\.|\*|:\(top\))(?=\s|$)",
        "禁止大范围 git restore 丢弃改动",
    ),
    (r"\bgit\s+push\b[^\n;&|]*(--force|-f)\b", "禁止强制推送"),
    (r"\bchmod\s+-R\s+777\b", "禁止递归 chmod 777"),
    (
        r"--dangerously-bypass|danger-full-access|--yolo\b",
        "禁止绕过沙箱或审批机制",
    ),
]

SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9_-]{20,}", "OpenAI 风格 API 密钥"),
    (r"ghp_[A-Za-z0-9_]{20,}", "GitHub 个人令牌"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "GitHub 细粒度令牌"),
    (r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "私钥内容"),
    (
        r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{24,}",
        "高熵内联敏感值",
    ),
]

COMPLETION_WORDS = re.compile(
    r"(已完成|已经完成|完成了|完成|修复了|处理好了|done\b|fixed\b|complete\b|completed\b)",
    re.IGNORECASE,
)
VERIFICATION_WORDS = re.compile(
    r"(验证|校验|测试|test|lint|build|typecheck|dry-run|bash -n|exit code 0|通过|passed|pass\b|0 failures)",
    re.IGNORECASE,
)
SUBAGENT_SUMMARY_WORDS = re.compile(
    r"(结论|摘要|发现|证据|验证|风险|限制|阻塞|文件|路径|未验证|下一步)",
    re.IGNORECASE,
)

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"
WORK_HABITS_PROMPT = PROMPT_DIR / "agent-work-habits.md"
SUBAGENT_WORK_HABITS_PROMPT = PROMPT_DIR / "subagent-work-habits.md"


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


def add_context(event_name: str, context: str) -> None:
    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": context,
            }
        }
    )


def system_message(message: str) -> None:
    emit({"systemMessage": message})


def read_prompt_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def command_from_tool_input(tool_input: Any) -> str:
    if isinstance(tool_input, dict):
        for key in ("command", "cmd"):
            command = tool_input.get(key)
            if isinstance(command, str):
                return command
    if isinstance(tool_input, str):
        return tool_input
    return ""


def has_override(text: str) -> bool:
    del text
    return os.environ.get("CODEX_ALLOW_DESTRUCTIVE") == "1"


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
            return (
                f"已被全局 Codex 策略阻断：{label}。如果确实需要执行，"
                "请先停止并获得明确人工批准；不要在命令中自行添加绕过变量。"
            )
    return None


def writes_live_codex_entry(
    command: str, *, tool_name: str, cwd: str = ""
) -> bool:
    if tool_name == "apply_patch":
        live_root = Path(
            os.path.abspath(Path.home() / (".co" + "dex"))
        )
        base_dir = Path(os.path.abspath(cwd or Path.cwd()))
        headers = re.findall(
            r"^\*\*\* (?:Add|Update|Delete) File: (.+)$",
            command,
            re.MULTILINE,
        )
        for raw_path in headers:
            expanded = raw_path.strip()
            expanded = expanded.replace("${HOME}", str(Path.home()))
            expanded = expanded.replace("$HOME", str(Path.home()))
            candidate = Path(expanded).expanduser()
            if not candidate.is_absolute():
                candidate = base_dir / candidate
            candidate = Path(os.path.abspath(candidate))
            if candidate == live_root or live_root in candidate.parents:
                return True
        return False

    home = os.path.expanduser("~").rstrip("/")
    home_prefixes = (
        f"{home}/.codex/",
        "$HOME/.codex/",
        "${HOME}/.codex/",
        "~/.codex/",
    )
    managed_names = (
        "AGENTS.md",
        "agents",
        "docs",
        "prompts",
        "skills",
        "hooks",
        "hooks.json",
        "restore-global-setup.sh",
        "restore-official-state.sh",
    )
    live_entry = any(
        f"{prefix}{name}" in command
        for prefix in home_prefixes
        for name in managed_names
    )
    if not live_entry:
        return False

    write_intent = re.search(
        r"(\b(rm|mv|cp|ln|touch|mkdir|chmod|chown|install|truncate)\b|"
        r"\bsed\s+-i\b|\bperl\s+-pi\b|\btee\b|>>|>)",
        command,
    )
    interpreter_write = re.search(
        r"\b(python[0-9.]*|node|ruby|php)\b.*"
        r"(write|unlink|remove|rename|replace|mkdir|chmod|chown)",
        command,
        re.IGNORECASE,
    )
    return bool(
        write_intent
        or interpreter_write
        or command.lstrip().startswith("*** Begin Patch")
    )


def handle_user_prompt(event: dict[str, Any]) -> None:
    prompt = str(event.get("prompt") or "")
    label = high_confidence_secret(prompt)
    if label:
        block_prompt(
            f"已被全局 Codex 策略阻断：提示词疑似包含{label}。"
            "请改用本地环境文件或凭证存储，不要把真实敏感信息粘贴进任务。"
        )


def handle_pre_tool(event: dict[str, Any]) -> None:
    tool_name = str(event.get("tool_name") or "")
    command = command_from_tool_input(event.get("tool_input"))
    if not command:
        return

    reason = destructive_reason(command)
    if reason:
        block_pre_tool(reason)
        return

    if tool_name in {"Bash", "apply_patch"} and writes_live_codex_entry(
        command,
        tool_name=tool_name,
        cwd=str(event.get("cwd") or ""),
    ):
        block_pre_tool(
            "已被全局 Codex 策略阻断：请修改 codex-config 真源仓库，"
            "再运行 restore-codex-global-links.sh；不要直接修改 live ~/.codex 入口。"
        )
        return

    if re.search(r"\bgit\s+push\b", command):
        emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": "推送前必须运行仓库 guard，并报告验证结果。",
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


def handle_session_start(event: dict[str, Any]) -> None:
    contexts: list[str] = []

    if event.get("source") == "compact":
        contexts.append(
            "上下文刚完成压缩。继续前先重新读取当前范围内的 AGENTS.md、"
            "docs/spec.md 与 docs/plan.md，恢复 Mission、Constraints、"
            "Working Goal、Stage Objective 和当前验收状态；不要仅依赖压缩摘要。"
        )

    prompt = read_prompt_file(WORK_HABITS_PROMPT)
    if prompt:
        contexts.append(prompt)

    if contexts:
        add_context("SessionStart", "\n\n".join(contexts))


def handle_subagent_start(event: dict[str, Any]) -> None:
    prompt = read_prompt_file(SUBAGENT_WORK_HABITS_PROMPT)
    if prompt:
        add_context("SubagentStart", prompt)
        return

    add_context(
        "SubagentStart",
        "子代理必须保持边界清晰：优先读多写少；不要倾倒原始日志；返回结论、关键证据、风险或未验证项；未经明确要求不要改写核心代码。",
    )


def handle_subagent_stop(event: dict[str, Any]) -> None:
    if event.get("stop_hook_active"):
        return

    last = str(event.get("last_assistant_message") or "").strip()
    if not last:
        continue_turn("Subagent must return a concise summary before stopping.")
        return

    if len(last) < 30 or not SUBAGENT_SUMMARY_WORDS.search(last):
        continue_turn(
            "Before stopping, return a concise subagent summary with conclusion, evidence, risks or unverified items."
        )


def handle_pre_compact(event: dict[str, Any]) -> None:
    system_message(
        "Compaction guard: preserve Mission, Constraints, Working Goal, current stage, verification evidence, user decisions, blockers, and remaining risks."
    )


def handle_post_compact(event: dict[str, Any]) -> None:
    system_message(
        "After compaction, re-check the active goal, latest user instruction, verification state, and unresolved risks before continuing."
    )


def handle_stop(event: dict[str, Any]) -> None:
    if event.get("stop_hook_active"):
        return
    last = str(event.get("last_assistant_message") or "")
    if COMPLETION_WORDS.search(last) and not VERIFICATION_WORDS.search(last):
        continue_turn(
            "在宣称完成前，运行或引用最接近改动的可行验证。"
            "如果无法验证，必须明确说明未验证项及原因。"
        )


def main() -> int:
    event = read_event()
    name = str(event.get("hook_event_name") or "")

    if name == "SessionStart":
        handle_session_start(event)
    elif name == "UserPromptSubmit":
        handle_user_prompt(event)
    elif name == "PreToolUse":
        handle_pre_tool(event)
    elif name == "PermissionRequest":
        handle_permission_request(event)
    elif name == "SubagentStart":
        handle_subagent_start(event)
    elif name == "SubagentStop":
        handle_subagent_stop(event)
    elif name == "PreCompact":
        handle_pre_compact(event)
    elif name == "PostCompact":
        handle_post_compact(event)
    elif name == "Stop":
        handle_stop(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
