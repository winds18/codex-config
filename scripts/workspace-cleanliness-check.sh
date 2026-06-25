#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf '工作区清洁检查失败：%s\n' "$1" >&2
  exit 1
}

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  fail "当前目录不是 git 仓库"
fi

staged_tmp="$(
  git diff --cached --name-only --diff-filter=ACMR |
    grep -E '(^|/)(\.tmp|\.artifacts|\.cache)/|(^|/).*\.(tmp|temp|bak|log)$' || true
)"

if [ -n "$staged_tmp" ]; then
  printf '%s\n' "$staged_tmp" >&2
  fail "提交前必须清理或移出已暂存的临时文件"
fi

root_noise="$(
  find . -maxdepth 1 \( \
    -name '.DS_Store' -o \
    -name '*.tmp' -o \
    -name '*.temp' -o \
    -name '*.bak' -o \
    -name '*.log' \
  \) -print | sed 's#^\./##' || true
)"

if [ -n "$root_noise" ]; then
  printf '%s\n' "$root_noise" >&2
  fail "提交前必须清理仓库根目录的临时噪音文件"
fi

printf '工作区清洁检查通过。\n'
