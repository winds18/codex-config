"""只读审计目标代码，在临时 Git 仓库复现边界；不执行危险字符串或推送。"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASELINE = "9618e008c3cbb387d8894e27dca52ab55dc58a60"


def load(name, relative):
    # 固定审计前代码，避免旧缺陷复现误调用优化后的实现。
    source = subprocess.run(
        ["git", "show", f"{BASELINE}:{relative}"], cwd=ROOT, check=True,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    sys.modules[name] = module
    exec(compile(source, f"{BASELINE}:{relative}", "exec"), module.__dict__)
    return module


def main():
    guard = load("audit_policy", "hooks/codex-policy-guard.py")
    scanner = load("audit_scan", "scripts/secret-scan.py")
    results = {}
    cases = [
        ("negated_completion", guard.handle_stop,
         {"last_assistant_message": "尚未完成，需要你提供目标文件。"}),
        ("unverified_claim", guard.handle_stop,
         {"last_assistant_message": "已完成，测试以后再说。"}),
        ("valid_short_summary", guard.handle_subagent_stop,
         {"last_assistant_message": "结论：未发现问题。证据：目标测试通过。"}),
        ("quoted_documentation", guard.handle_pre_tool,
         {"tool_name": "Bash", "tool_input": {
             "command": "printf '%s' 'git reset --hard'"}}),
        ("checkout_discard", guard.handle_pre_tool,
         {"tool_name": "Bash", "tool_input": {
             "command": "git checkout -- file.txt"}}),
        ("safe_documentation_patch", guard.handle_pre_tool,
         {"tool_name": "apply_patch", "tool_input": {"command":
             "*** Begin Patch\n*** Add File: /tmp/example.md\n"
             "+不要使用 git reset --hard\n*** End Patch"}}),
    ]
    previous_override = os.environ.pop("CODEX_ALLOW_DESTRUCTIVE", None)
    try:
        for name, handler, event in cases:
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                handler(event)
            payload = json.loads(capture.getvalue()) if capture.getvalue() else {}
            results[name] = "block" if payload else "allow"
    finally:
        if previous_override is not None:
            os.environ["CODEX_ALLOW_DESTRUCTIVE"] = previous_override

    with tempfile.TemporaryDirectory(prefix="codex-audit-") as directory:
        folder = Path(directory)

        def git(*args):
            return subprocess.run(
                ["git", "-c", "core.hooksPath=/dev/null", "-c",
                 "commit.gpgsign=false", *args], cwd=folder, check=True,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            ).stdout.strip()

        def commit(message):
            git("add", ".")
            git("commit", "-m", message)

        git("init", "-b", "main")
        git("config", "user.name", "Audit Fixture")
        git("config", "user.email", "audit@example.invalid")
        (folder / "base.txt").write_text("base")
        commit("base")
        base = git("rev-parse", "HEAD")
        git("checkout", "-b", "side")
        (folder / "side.txt").write_text("side")
        commit("side")
        git("checkout", "main")
        (folder / "main.txt").write_text("main")
        commit("main")
        git("merge", "--no-ff", "--no-commit", "side")
        # 合成格式匹配值，不是真实凭证，也不会输出其内容。
        (folder / "fixture.txt").write_text("ghp_" + "A" * 36)
        commit("merge introduces synthetic fixture")
        merge = git("rev-parse", "HEAD")
        (folder / "fixture.txt").unlink()
        commit("remove synthetic fixture")
        head = git("rev-parse", "HEAD")
        previous_cwd = Path.cwd()
        os.chdir(folder)
        try:
            results["merge_paths"] = scanner.commit_paths(merge)
            results["direct_merge_blob_findings"] = len(scanner.scan_content(
                "fixture.txt", scanner.commit_blob(merge, "fixture.txt")))
            results["merge_outgoing_findings"] = len(scanner.scan_outgoing([
                f"refs/heads/main {head} refs/heads/main {base}"]))

            # 独立验证普通提交也会因无关的远程 tracking ref 被排除。
            (folder / "private-fixture.txt").write_text("ghp_" + "B" * 36)
            commit("ordinary private synthetic fixture")
            private_commit = git("rev-parse", "HEAD")
            git("update-ref", "refs/remotes/private/main", private_commit)
            (folder / "private-fixture.txt").unlink()
            commit("remove private fixture")
            new_head = git("rev-parse", "HEAD")
            push_input = [f"refs/heads/main {new_head} refs/heads/main "
                          + scanner.ZERO_SHA]
            results["unrelated_remote_excludes_ordinary_commit"] = (
                private_commit not in scanner.outgoing_commits(push_input))
            results["new_remote_outgoing_findings"] = len(
                scanner.scan_outgoing(push_input))
        finally:
            os.chdir(previous_cwd)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
