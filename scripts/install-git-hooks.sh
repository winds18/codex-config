#!/usr/bin/env bash
set -euo pipefail

resolve_script_dir() {
  local source_path="${BASH_SOURCE[0]}"

  while [ -L "$source_path" ]; do
    local dir
    dir="$(cd -P "$(dirname "$source_path")" && pwd)"
    source_path="$(readlink "$source_path")"
    case "$source_path" in
      /*) ;;
      *) source_path="$dir/$source_path" ;;
    esac
  done

  cd -P "$(dirname "$source_path")" && pwd
}

SCRIPT_DIR="$(resolve_script_dir)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  printf '当前目录不是 Git 仓库，请先 git init 或 clone 仓库。\n' >&2
  exit 1
fi

git config extensions.worktreeConfig true
git config --worktree core.hooksPath "$ROOT_DIR/git-hooks"

printf '已通过 worktree-local core.hooksPath 安装 codex-config Git hooks。\n'
printf 'core.hooksPath=%s\n' "$ROOT_DIR/git-hooks"
