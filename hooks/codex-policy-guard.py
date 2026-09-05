#!/usr/bin/env python3
"""Small, supplemental PreToolUse checks; never an approval mechanism.

Only direct shell commands and structured file targets are inspected. Shell
interpreters, heredocs, variable evaluation, substitutions and arbitrary code
are outside this parser's guarantees. Native permissions remain authoritative.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(__file__).resolve().parent.parent
SHELL_TOOLS = {"Bash", "exec_command"}
PATCH_TOOLS = {"apply_patch"}
FILE_TOOLS = {"Edit", "Write"}


def read_event() -> dict[str, Any]:
    try:
        event = json.load(sys.stdin)
        return event if isinstance(event, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def block_pre_tool(reason: str) -> None:
    emit({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }})


def command_from_tool_input(tool_input: Any) -> str:
    if isinstance(tool_input, dict):
        for key in ("command", "cmd", "patch", "input"):
            value = tool_input.get(key)
            if isinstance(value, str):
                return value
    return tool_input if isinstance(tool_input, str) else ""


class ShellWord(str):
    """Decoded value plus source spelling, so quoted operators stay data."""

    def __new__(cls, value: str, raw: str, operator: bool = False):
        item = str.__new__(cls, value)
        item.raw = raw
        item.operator = operator
        return item


def shell_tokens(command: str) -> list[ShellWord]:
    tokens: list[ShellWord] = []
    index = 0
    punctuation = ";&|()<>\n"
    while index < len(command):
        char = command[index]
        if char in " \t\r":
            index += 1
            continue
        if char == "#":
            newline = command.find("\n", index)
            index = len(command) if newline < 0 else newline
            continue
        start = index
        if char in punctuation:
            index += 1
            while index < len(command) and command[index] in punctuation:
                index += 1
            raw = command[start:index]
            if "<<" in raw:
                return []
            tokens.append(ShellWord(raw, raw, True))
            continue
        quote = ""
        while index < len(command):
            char = command[index]
            if not quote and (char in " \t\r" or char in punctuation):
                break
            if char == "\\" and quote != "'":
                index += 2
                continue
            if char in "\"'" and (not quote or quote == char):
                quote = char if not quote else ""
            elif quote != "'" and (char == "`" or command[index:index + 2] == "$("):
                return []
            index += 1
        raw = command[start:index]
        try:
            decoded = shlex.split(raw, comments=False, posix=True)
        except ValueError:
            return []
        if len(decoded) != 1 or quote:
            return []
        tokens.append(ShellWord(decoded[0], raw))
    return tokens


def shell_commands(command: str) -> list[list[str]]:
    """Tokenize direct commands without executing or evaluating shell code."""
    commands: list[list[str]] = []
    current: list[str] = []
    for token in shell_tokens(command):
        if token.operator and all(char in ";&|()\n" for char in token):
            if current:
                commands.append(current)
                current = []
        else:
            current.append(token)
    if current:
        commands.append(current)
    return commands


def shell_path(word: str) -> str:
    """Expand only simple path spellings we can recognize without evaluation."""
    raw = getattr(word, "raw", word)
    if raw.startswith("'") and raw.endswith("'"):
        return str(word)
    if "\\" in raw or "'" in raw:
        return str(word)
    value = os.path.expandvars(str(word))
    return os.path.expanduser(value) if not raw.startswith('"') else value


def unwrap(words: list[str]) -> list[str]:
    words = words[:]
    while words and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", getattr(words[0], "raw", words[0]))
                     or getattr(words[0], "raw", words[0]) in {"!", "then", "do", "if", "elif"}):
        words.pop(0)
    # Limited wrappers with no option parsing ambiguity.
    if words and words[0] in {"command", "exec", "env", "sudo"}:
        words.pop(0)
        while words and (words[0] == "--" or re.match(
            r"^[A-Za-z_][A-Za-z0-9_]*=", getattr(words[0], "raw", words[0])
        )):
            words.pop(0)
    return words


def recursive_rm_targets(words: list[str]) -> list[str]:
    recursive = False
    targets: list[str] = []
    options = True
    for word in words:
        if word == "--" and options:
            options = False
        elif options and word.startswith("-"):
            recursive |= word == "--recursive" or (
                not word.startswith("--") and bool(set(word[1:]) & {"r", "R"})
            )
        else:
            targets.append(word)
    return targets if recursive else []


def destructive_reason(command: str) -> str | None:
    """Only catastrophic direct forms are denied; ordinary Git risk is advice."""
    for segment in shell_commands(command):
        words = unwrap(segment)
        if not words:
            continue
        executable, args = os.path.basename(words[0]), words[1:]
        if executable == "rm":
            for target in recursive_rm_targets(args):
                normalized = os.path.normpath(shell_path(target))
                raw = getattr(target, "raw", target)
                if normalized in {"*", "/*"} and ("\"" in raw or "\'" in raw or "\\" in raw):
                    continue
                if normalized in {"/", ".", "..", str(Path.home()), "*", "/*"}:
                    return "检测到递归删除根目录、home、当前目录、上级目录或全部条目的直接命令。"
        if executable == "codex" and any(
            arg in {"--yolo", "--dangerously-bypass-approvals-and-sandbox"}
            or arg.startswith("--dangerously-bypass") for arg in args
        ):
            return "检测到 Codex 绕过审批与沙箱的启动选项。"
    return None


def git_advice(words: list[str]) -> str | None:
    words = unwrap(words)
    if not words or os.path.basename(words[0]) != "git":
        return None
    args = words[1:]
    while args and args[0].startswith("-"):
        option = args.pop(0)
        if option in {"-C", "-c", "--git-dir", "--work-tree"} and args:
            args.pop(0)
    if not args:
        return None
    verb, args = args[0], args[1:]
    if verb == "reset" and "--hard" in args:
        return "git reset --hard 会丢弃工作区与索引改动"
    if verb == "clean" and not any(arg in {"--dry-run", "-n"} for arg in args):
        if any(arg.startswith("-") and not arg.startswith("--") and "n" in arg
               for arg in args):
            return None
        return "git clean 可能删除未跟踪文件"
    if verb == "checkout" and "--" in args:
        return "git checkout 路径操作会覆盖对应工作区改动"
    if verb == "restore":
        return "git restore 会替换所选路径的工作区或索引内容"
    if verb == "push" and any(
        arg in {"-f", "--force", "--force-with-lease", "--force-if-includes"}
        or arg.startswith("--force-with-lease=") or arg.startswith("+")
        or (arg.startswith("-") and not arg.startswith("--") and "f" in arg[1:])
        for arg in args
    ):
        return "git push 的强制更新选项可能重写远端历史"
    return None


def live_root() -> Path:
    return Path(os.path.abspath(os.path.expanduser(
        os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    )))


def owned_live_target(raw_path: str, cwd: str = "") -> bool:
    # Resolve paths lexically first: resolving a managed symlink too early
    # loses the fact that an operation targets the live entry itself.
    root = live_root()
    candidate = Path(shell_path(raw_path) if isinstance(raw_path, ShellWord) else raw_path)
    if not candidate.is_absolute():
        candidate = Path(cwd or os.getcwd()) / candidate
    candidate = Path(os.path.abspath(candidate))
    if candidate != root and root not in candidate.parents:
        return False
    try:
        resolved = candidate.resolve()
        if resolved == SOURCE_ROOT or SOURCE_ROOT in resolved.parents:
            return True
        # Directory operations must also protect owned links inside that dir.
        # Inspect known source paths only, never traverse runtime state/logs.
        if candidate.is_dir():
            for directory in ("agents", "docs", "prompts", "hooks", "skills"):
                source = SOURCE_ROOT / directory
                if not source.exists():
                    continue
                for source_file in source.rglob("*"):
                    if not source_file.is_file():
                        continue
                    installed = root / source_file.relative_to(SOURCE_ROOT)
                    if candidate == installed or candidate in installed.parents:
                        if installed.resolve() == source_file.resolve():
                            return True
            for name in ("AGENTS.md", "hooks.json", "restore-global-setup.sh",
                         "restore-official-state.sh"):
                installed = root / name
                if installed.is_symlink() and (candidate == installed or candidate in installed.parents):
                    target = installed.resolve()
                    if target == SOURCE_ROOT or SOURCE_ROOT in target.parents:
                        return True
    except (OSError, RuntimeError):
        return False
    return False


def shell_write_targets(words: list[str]) -> list[str]:
    words = unwrap(words)
    if not words:
        return []
    targets = [words[index + 1] for index, word in enumerate(words[:-1])
               if getattr(word, "operator", False) and word in {">", ">>", ">|", "&>"}]
    executable, args = os.path.basename(words[0]), words[1:]
    # A source path being read is not a destination being changed.
    operands = [word for word in args if not word.startswith("-")]
    if executable in {"cp", "ln", "install"}:
        if operands:
            targets.append(operands[-1])
        for index, arg in enumerate(args):
            if arg in {"-t", "--target-directory"} and index + 1 < len(args):
                targets.append(args[index + 1])
            elif arg.startswith("--target-directory="):
                targets.append(arg.split("=", 1)[1])
    elif executable in {"rm", "mv", "touch", "mkdir", "chmod", "chown", "truncate", "tee"}:
        targets.extend(operands)
    elif executable == "sed" and any(arg == "--in-place" or arg.startswith("-i") for arg in args):
        targets.extend(operands[-1:])
    return targets


def writes_live_codex_entry(command: str, *, tool_name: str, cwd: str = "") -> bool:
    if tool_name in PATCH_TOOLS:
        targets = re.findall(
            r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+)$",
            command, re.MULTILINE,
        )
    elif tool_name in SHELL_TOOLS:
        targets = [target for words in shell_commands(command)
                   for target in shell_write_targets(words)]
    else:
        targets = [command]
    return any(owned_live_target(target, cwd) for target in targets)


def handle_pre_tool(event: dict[str, Any]) -> None:
    tool_name = str(event.get("tool_name") or "")
    tool_input = event.get("tool_input")
    cwd = str(event.get("cwd") or "")
    if isinstance(tool_input, dict):
        cwd = str(tool_input.get("workdir") or cwd)
    if tool_name in FILE_TOOLS:
        if not isinstance(tool_input, dict):
            return
        command = str(tool_input.get("file_path") or tool_input.get("path") or "")
    elif tool_name in SHELL_TOOLS | PATCH_TOOLS:
        command = command_from_tool_input(tool_input)
    else:
        return
    if not command:
        return
    if tool_name in SHELL_TOOLS and (reason := destructive_reason(command)):
        block_pre_tool(reason + "此自定义 hook 不接受环境变量授权；如需例外，由用户审查并调整 hook 配置，客户端权限仍然生效。")
        return
    if writes_live_codex_entry(command, tool_name=tool_name, cwd=cwd):
        block_pre_tool("目标是 codex-config 管理的 live 链接；请修改真源文件，并通过安装/恢复脚本维护链接。")
        return
    if tool_name in SHELL_TOOLS:
        advice = list(dict.fromkeys(item for words in shell_commands(command)
                                   if (item := git_advice(words))))
        if advice:
            emit({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "；".join(advice) + "。依据本次已给授权及客户端权限执行；该提示不授予权限，也不要求重复审批。",
            }})


def main() -> int:
    event = read_event()
    if event.get("hook_event_name") == "PreToolUse":
        handle_pre_tool(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
