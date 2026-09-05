#!/usr/bin/env python3
"""离线检查模板静态依赖；不执行模板代码，不请求外部 URL。"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "assets/templates"
SOURCE = {
    "awesome-design-md": ("8147538b4226ae41e2487a9179e3bcc1f68e8554", "https://github.com/VoltAgent/awesome-design-md", "MIT License"),
    "personal-homepage-skill": ("4055fabb1b67637364d375e18eb9ae13467a03db", "https://github.com/shengjidaguai-china/personal-homepage-skill", "Personal Homepage Skill Non-Commercial License"),
}
SOURCE_EXTENSIONS = {".js", ".mjs", ".ts", ".tsx"}
MEDIA_EXTENSIONS = {".mp4", ".jpg", ".png", ".gif"}
# 上游故意破坏的负向 fixture，不代表模板生产资源缺失。
EXPECTED_MISSING = {("personal-homepage-skill/tests/fixtures/broken-image.html", "./does-not-exist.png")}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"src", "href", "poster"} and value:
                self.links.append(value)


def classification(path: Path, relative: Path) -> str:
    if "portable" in relative.parts:
        return "便携产物/资源"
    if "fixtures" in relative.parts:
        return "测试夹具"
    if path.suffix in MEDIA_EXTENSIONS or path.suffix == ".svg":
        return "媒体/预览"
    if "tests" in relative.parts or "scripts" in relative.parts:
        return "脚本/测试入口"
    if path.suffix in SOURCE_EXTENSIONS | {".css", ".html"}:
        return "模板源码/页面"
    if path.suffix == ".json":
        return "配置/依赖锁"
    if path.name in {"LICENSE", "SOURCE.md", "UPSTREAM_COMMIT"}:
        return "来源/许可"
    return "说明/设计参考"


def references(path: Path, data: str):
    """仅解析字面量；动态 URL、模板表达式和 Markdown 示例代码不作真实依赖。"""
    found = []
    if path.suffix == ".md":
        data = re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", data, flags=re.M | re.S)
        found.extend((m, "文档链接") for m in re.findall(r"\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)", data))
    if path.suffix in {".html", ".svg"}:
        parser = Links()
        parser.feed(data)
        found.extend((m, "页面资源") for m in parser.links)
    if path.suffix in SOURCE_EXTENSIONS:
        found.extend((m, "模块引用") for m in re.findall(r"(?:\bfrom\s+|\bimport\s*\(\s*|\bimport\s+)[\"']([^\"']+)[\"']", data))
        found.extend((m, "模块资源") for m in re.findall(r"new URL\(\s*[\"']([^\"']+)[\"']\s*,\s*import\.meta\.url", data))
        if path.suffix == ".tsx":
            found.extend((m, "页面资源") for m in re.findall(r"\b(?:src|href|poster)=[\"']([^\"']+)[\"']", data))
    if path.suffix in {".css", ".html", ".svg"}:
        found.extend((m.strip("'\" "), "样式资源") for m in re.findall(r"url\(([^)]+)\)", data))
    return set(found)


def inspect(root: Path):
    root = root.resolve()
    errors, notes, rows, counters = [], [], [], Counter()
    for name, (commit, repository, license_title) in SOURCE.items():
        base = root / name
        try:
            if (base / "UPSTREAM_COMMIT").read_text().strip() != commit:
                errors.append(f"{name}: commit 标记不匹配")
            source = (base / "SOURCE.md").read_text()
            if commit not in source or repository not in source:
                errors.append(f"{name}: SOURCE 与 commit/repository 不一致")
            if license_title not in (base / "LICENSE").read_text():
                errors.append(f"{name}: LICENSE 标题不匹配")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{name}: 来源文件不可读：{exc}")

    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if path.is_symlink():
            errors.append(f"{rel}: 快照不允许符号链接")
            continue
        if not path.is_file():
            continue
        raw = path.read_bytes()
        row = {"path": str(rel), "category": classification(path, rel), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "local_links": 0, "notes": []}
        rows.append(row)
        counters[row["category"]] += 1
        if path.suffix in MEDIA_EXTENSIONS:
            signatures = {".jpg": raw.startswith(b"\xff\xd8\xff"), ".png": raw.startswith(b"\x89PNG\r\n\x1a\n"), ".gif": raw[:6] in {b"GIF87a", b"GIF89a"}, ".mp4": raw[4:8] == b"ftyp"}
            if not signatures[path.suffix]:
                errors.append(f"{rel}: 媒体签名与扩展名不匹配")
            continue
        try:
            data = raw.decode("utf-8")
            if path.suffix == ".json":
                json.loads(data)
            if path.suffix == ".svg":
                ET.fromstring(data)
        except (UnicodeError, ValueError, ET.ParseError) as exc:
            errors.append(f"{rel}: 文本/结构无效：{exc}")
            continue
        for value, kind in sorted(references(path, data)):
            if any(marker in value for marker in ("${", "{", "<", ">")):
                continue
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc:
                counters["外部/特殊引用"] += 1
                continue
            target = unquote(parsed.path)
            if not target:
                continue
            if kind == "模块引用" and not target.startswith("."):
                continue  # 包引用由 package/lock 和实际构建负责。
            base = root / rel.parts[0]
            resolved = (base / target.lstrip("/") if target.startswith("/") else path.parent / target).resolve()
            row["local_links"] += 1
            candidates = [resolved]
            if kind == "模块引用":
                candidates += [Path(str(resolved) + extension) for extension in (".ts", ".tsx", ".js", ".mjs", ".css")]
                candidates += [resolved / ("index" + extension) for extension in (".ts", ".tsx", ".js")]
            if any(p.exists() for p in candidates) and resolved.is_relative_to(root):
                continue
            message = f"{rel}: {kind}缺失或越界 {value}"
            if (str(rel), value) in EXPECTED_MISSING or kind == "文档链接":
                notes.append(message)
                row["notes"].append(value)
            else:
                errors.append(message)

    for name, expected_count in {"awesome-design-md": 153, "personal-homepage-skill": 141}.items():
        actual_count = sum(row["path"].startswith(name + "/") for row in rows)
        if actual_count != expected_count:
            errors.append(f"{name}: 快照期望 {expected_count} 文件，实际 {actual_count}")
    home = root / "personal-homepage-skill"
    try:
        package = json.loads((home / "package.json").read_text())
        lock = json.loads((home / "package-lock.json").read_text())
        locked = lock["packages"][""]
        for key in ("name", "version", "dependencies", "devDependencies", "engines"):
            if package.get(key) != locked.get(key):
                errors.append(f"package/lock 根声明不一致：{key}")
        for name, command in package["scripts"].items():
            for entry in re.findall(r"\bnode\s+([^\s&;|]+)", command):
                if not (home / entry).is_file():
                    errors.append(f"package script {name}: 缺少入口 {entry}")
            for script in re.findall(r"\bnpm run\s+([^\s&;|]+)", command):
                if script not in package["scripts"]:
                    errors.append(f"package script {name}: 未定义 {script}")
        media_root = home / "templates/hero/assets"
        readme = (media_root / "README.md").read_text()
        hashes = re.findall(r"\| `([^`]+)` \|[^\n]+?\| `([0-9a-f]{64})` \|", readme)
        if len(hashes) != 6:
            errors.append("Hero 媒体 SHA-256 清单应有 6 项")
        for name, digest in hashes:
            for media in (media_root / name, home / "templates/hero/portable/assets" / name):
                if not media.is_file() or hashlib.sha256(media.read_bytes()).hexdigest() != digest:
                    errors.append(f"{media.relative_to(root)}: 与上游媒体 SHA-256 不符")
    except (OSError, ValueError, KeyError) as exc:
        errors.append(f"package/lock/media 校验失败：{exc}")
    return rows, errors, notes, counters


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--inventory", action="store_true", help="输出逐文件 Markdown 清单")
    args = parser.parse_args()
    rows, errors, notes, counters = inspect(args.root)
    if args.inventory:
        print("| 快照内路径 | 分类 | 字节 | 本地引用 | 备注 |\n| --- | --- | ---: | ---: | --- |")
        for row in rows:
            print(f"| `{row['path']}` | {row['category']} | {row['bytes']} | {row['local_links']} | {'、'.join(row['notes']) or '静态检查通过'} |")
    for note in notes:
        print("参考注记：", note)
    for error in errors:
        print("错误：", error)
    print(f"模板静态依赖校验：{len(rows)} 文件，{sum(row['local_links'] for row in rows)} 本地引用，{len(errors)} 错误，{len(notes)} 注记。")
    print("边界：来源标记不等于独立上游签名验证；未解析动态引用、包传递依赖、Markdown 锚点，未请求外部资源或运行浏览器。")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
