#!/usr/bin/env python3
"""检查本仓库维护的配置结构和引用；不对自然语言口号作断言。"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def agent_config(path):
    source = path.read_text(encoding="utf-8")
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            tomllib = None
    if tomllib:
        return tomllib.loads(source)
    # macOS Python 3.9 的无依赖路径只接受本仓库的顶层字符串格式。
    # 扩展到 table/array 等 TOML 时须使用 Python 3.11+ 或安装 tomli。
    values = {}
    pattern = re.compile(
        r'\s*([a-z_]+)\s*=\s*(?:"""(.*?)"""|("(?:[^"\\\n]|\\.)*"))\s*', re.S
    )
    offset = 0
    while source[offset:].strip():
        match = pattern.match(source, offset)
        if not match:
            raise ValueError("扩展/无效 TOML；请用 Python 3.11+ 或 tomli 校验")
        key, multiline, scalar = match.groups()
        if key in values:
            raise ValueError("重复配置键：" + key)
        if multiline is not None and "\\" in multiline:
            raise ValueError("多行 TOML 转义需完整 TOML 解析器")
        values[key] = multiline if multiline is not None else json.loads(scalar)
        offset = match.end()
    return values


def check(root=ROOT):
    errors = []
    names = set()
    allowed = {"name", "description", "developer_instructions", "model",
               "model_reasoning_effort", "sandbox_mode"}
    for path in sorted((root / "agents").glob("*.toml")):
        try:
            config = agent_config(path)
            if set(config) - allowed:
                raise ValueError("未知角色字段：" + str(set(config) - allowed))
            for key in ("name", "description", "developer_instructions"):
                if not isinstance(config.get(key), str) or not config[key].strip():
                    raise ValueError("缺少非空字符串 " + key)
            if config["name"] != path.stem or config["name"] in names:
                raise ValueError("角色名与文件名不符或重复")
            names.add(config["name"])
            if "model" in config and not config["model"].strip():
                raise ValueError("模型不能是空字符串")
            if config.get("model_reasoning_effort", "medium") not in {
                    "none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}:
                raise ValueError("未知推理档位")
            if config.get("sandbox_mode", "workspace-write") not in {
                    "read-only", "workspace-write", "danger-full-access"}:
                raise ValueError("未知沙箱模式")
        except (ValueError, TypeError) as error:
            errors.append(f"{path.relative_to(root)}: {error}")

    for path in sorted((root / "skills").glob("*/SKILL.md")):
        source = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", source, re.S)
        fields = dict(re.findall(r"^(name|description): (.+)$", match[1], re.M)) if match else {}
        if fields.get("name") != path.parent.name or not fields.get("description", "").strip():
            errors.append(f"{path.relative_to(root)}: 技能名称/描述缺失或不匹配")
        # 自维护 skill 使用简单 frontmatter；完整 YAML 另用 quick_validate 检查。

    maintained = [root / "AGENTS.md", root / "AGENTS.override.md", root / "README.md"]
    maintained += list((root / "docs").glob("*.md")) + list((root / "prompts").glob("*.md"))
    maintained += [p for p in (root / "skills").rglob("*.md") if "assets" not in p.parts]
    for path in maintained:
        source = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)\s]+)\)", source):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            if not (path.parent / target.split("#")[0]).exists():
                errors.append(f"{path.relative_to(root)}: 缺失链接 {target}")
        # 支持技能中的按需内联代码路径；示例占位路径不当成实际依赖。
        for target in re.findall(r"`((?:\.\./|references/)[^`\s]+\.md)`", source):
            if not (path.parent / target).exists():
                errors.append(f"{path.relative_to(root)}: 缺失引用 {target}")

    try:
        config = json.loads((root / "hooks/hooks.json").read_text())
        for event, groups in config["hooks"].items():
            if event not in {"PreToolUse"}:
                raise ValueError("本配置仅分发 PreToolUse；扩展事件须更新结构检查和行为测试")
            for group in groups:
                re.compile(group.get("matcher", ".*"))
                for handler in group["hooks"]:
                    if handler.get("type") != "command" or not handler.get("command"):
                        raise ValueError("hook handler 缺少 command")
                    if handler.get("timeout", 10) <= 0:
                        raise ValueError("hook timeout 必须为正数")
    except (KeyError, TypeError, ValueError, re.error) as error:
        errors.append(f"hooks/hooks.json: {error}")
    if errors:
        raise ValueError("\n".join(errors))
    print(f"配置结构与引用检查通过：{len(names)} 个角色，{len(maintained)} 个自维护文档。")


if __name__ == "__main__":
    try:
        check()
    except ValueError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
