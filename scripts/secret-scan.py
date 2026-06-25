#!/usr/bin/env python3
"""用于仓库 guard hook 的高置信敏感内容扫描器。"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass


MAX_BYTES = int(os.environ.get("CODEX_SECRET_SCAN_MAX_BYTES", str(2 * 1024 * 1024)))


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    label: str


PATTERNS: tuple[tuple[bytes, str], ...] = (
    (rb"sk-[A-Za-z0-9_-]{20,}", "OpenAI-style API key"),
    (rb"ghp_[A-Za-z0-9_]{20,}", "GitHub personal token"),
    (rb"github_pat_[A-Za-z0-9_]{20,}", "GitHub fine-grained token"),
    (rb"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (rb"xox[baprs]-[A-Za-z0-9-]{20,}", "Slack token"),
    (rb"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "private key block"),
    (
        rb"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{32,}",
        "high-entropy inline secret",
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


def line_number(content: bytes, offset: int) -> int:
    return content.count(b"\n", 0, offset) + 1


def scan_content(path: str, content: bytes) -> list[Finding]:
    if b"\0" in content[:4096] or len(content) > MAX_BYTES:
        return []

    findings: list[Finding] = []
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


def main() -> int:
    try:
        git(["rev-parse", "--show-toplevel"])
    except subprocess.CalledProcessError:
        print("secret scan failed: not a git repository", file=sys.stderr)
        return 1

    findings = scan_staged()
    if not findings:
        findings = scan_tracked()

    if findings:
        print("secret scan failed: possible sensitive content found", file=sys.stderr)
        for finding in findings:
            print(f"- {finding.path}:{finding.line}: {finding.label}", file=sys.stderr)
        print("Remove the secret, rotate it if real, then commit again.", file=sys.stderr)
        return 1

    print("secret scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
