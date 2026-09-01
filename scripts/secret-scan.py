#!/usr/bin/env python3
"""用于仓库 guard hook 的高置信敏感内容扫描器。"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass


MAX_BYTES = int(os.environ.get("CODEX_SECRET_SCAN_MAX_BYTES", str(20 * 1024 * 1024)))
ZERO_SHA = "0" * 40


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    label: str


PATTERNS: tuple[tuple[bytes, str], ...] = (
    (rb"sk-[A-Za-z0-9_-]{20,}", "OpenAI 风格 API 密钥"),
    (rb"ghp_[A-Za-z0-9_]{20,}", "GitHub 个人令牌"),
    (rb"github_pat_[A-Za-z0-9_]{20,}", "GitHub 细粒度令牌"),
    (rb"AKIA[0-9A-Z]{16}", "AWS 访问密钥 ID"),
    (rb"xox[baprs]-[A-Za-z0-9-]{20,}", "Slack 令牌"),
    (rb"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "私钥内容"),
    (
        rb"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{32,}",
        "高熵内联敏感值",
    ),
)


ALLOWLIST_MARKERS = (
    b"secret-scan: allow",
    b"pragma: allowlist secret",
)


def git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def split_nul(raw: bytes) -> list[str]:
    return [item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item]


def staged_paths() -> list[str]:
    result = git(["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], check=True)
    return split_nul(result.stdout)


def tracked_paths() -> list[str]:
    result = git(["ls-files", "-z"], check=True)
    return split_nul(result.stdout)


def staged_blob(path: str) -> bytes | None:
    result = git(["show", f":{path}"], check=False)
    if result.returncode != 0:
        return None
    return result.stdout


def file_bytes(path: str) -> bytes | None:
    try:
        with open(path, "rb") as handle:
            return handle.read(MAX_BYTES + 1)
    except OSError:
        return None


def sensitive_path_label(path: str) -> str | None:
    name = os.path.basename(path).lower()
    allowed_env_suffixes = (".example", ".sample", ".template")

    if name == ".env" or (
        name.startswith(".env.") and not name.endswith(allowed_env_suffixes)
    ):
        return "环境变量文件"
    if name in {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "auth.json"}:
        return "高置信凭证文件"
    if name.endswith((".p12", ".pfx")):
        return "私钥容器文件"
    return None


def line_number(content: bytes, offset: int) -> int:
    return content.count(b"\n", 0, offset) + 1


def scan_content(path: str, content: bytes) -> list[Finding]:
    findings: list[Finding] = []
    path_label = sensitive_path_label(path)
    if path_label:
        findings.append(Finding(path=path, line=1, label=path_label))

    if len(content) > MAX_BYTES:
        findings.append(
            Finding(
                path=path,
                line=1,
                label=f"文件超过 {MAX_BYTES} 字节，无法完成敏感信息扫描",
            )
        )
        return findings

    lines = content.splitlines()
    for pattern, label in PATTERNS:
        for match in re.finditer(pattern, content):
            line = line_number(content, match.start())
            current_line = lines[line - 1] if line - 1 < len(lines) else b""
            if any(marker in current_line for marker in ALLOWLIST_MARKERS):
                continue
            findings.append(Finding(path=path, line=line, label=label))
    return findings


def scan_staged() -> list[Finding]:
    findings: list[Finding] = []
    for path in staged_paths():
        content = staged_blob(path)
        if content is not None:
            findings.extend(scan_content(path, content))
    return findings


def scan_tracked() -> list[Finding]:
    findings: list[Finding] = []
    for path in tracked_paths():
        content = file_bytes(path)
        if content is not None:
            findings.extend(scan_content(path, content))
    return findings


def outgoing_commits(lines: list[str]) -> list[str]:
    commits: set[str] = set()
    for line in lines:
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 4:
            raise ValueError(f"无法解析 pre-push 输入：{line}")

        _, local_sha, _, remote_sha = fields
        if local_sha == ZERO_SHA:
            continue
        if remote_sha == ZERO_SHA:
            result = git(["rev-list", local_sha, "--not", "--remotes"])
        else:
            result = git(["rev-list", f"{remote_sha}..{local_sha}"])
        commits.update(result.stdout.decode("ascii").splitlines())
    return sorted(commits)


def commit_paths(commit: str) -> list[str]:
    result = git(
        [
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-only",
            "--diff-filter=ACMR",
            "-r",
            "-z",
            commit,
        ]
    )
    return split_nul(result.stdout)


def commit_blob(commit: str, path: str) -> bytes | None:
    result = git(["show", f"{commit}:{path}"], check=False)
    if result.returncode != 0:
        return None
    return result.stdout


def scan_outgoing(lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for commit in outgoing_commits(lines):
        for path in commit_paths(commit):
            content = commit_blob(commit, path)
            if content is not None:
                display_path = f"{path}@{commit[:12]}"
                path_label = sensitive_path_label(path)
                if path_label:
                    findings.append(
                        Finding(path=display_path, line=1, label=path_label)
                    )
                findings.extend(scan_content(display_path, content))
    return findings


def report(findings: list[Finding], *, success_message: str) -> int:
    if findings:
        print("敏感信息扫描失败：发现疑似敏感内容", file=sys.stderr)
        for finding in findings:
            print(f"- {finding.path}:{finding.line}: {finding.label}", file=sys.stderr)
        print("请先移除敏感内容；如果是真实凭证，还必须先轮换凭证。", file=sys.stderr)
        return 1

    print(success_message)
    return 0


def main() -> int:
    try:
        git(["rev-parse", "--show-toplevel"])
    except subprocess.CalledProcessError:
        print("敏感信息扫描失败：当前目录不是 Git 仓库", file=sys.stderr)
        return 1

    if sys.argv[1:] == ["--pre-push"]:
        try:
            findings = scan_outgoing(sys.stdin.read().splitlines())
        except (subprocess.CalledProcessError, ValueError) as error:
            print(f"敏感信息扫描失败：无法解析待推送提交：{error}", file=sys.stderr)
            return 1
        return report(findings, success_message="待推送提交历史敏感信息扫描通过。")
    if sys.argv[1:]:
        print("用法：secret-scan.py [--pre-push]", file=sys.stderr)
        return 1

    findings = scan_staged()
    if not findings:
        findings = scan_tracked()
    return report(findings, success_message="敏感信息扫描通过。")


if __name__ == "__main__":
    raise SystemExit(main())
