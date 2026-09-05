#!/usr/bin/env bash
set -euo pipefail

SOURCE_PATH="${BASH_SOURCE[0]}"
INSTALLED_ROOT=""
if [ -L "$SOURCE_PATH" ] && [ "$(basename "$SOURCE_PATH")" = "codex-config.sh" ]; then
  INSTALLED_ROOT="$(cd -P "$(dirname "$SOURCE_PATH")" && pwd)"
fi
LINK_COUNT=0
while [ -L "$SOURCE_PATH" ]; do
  LINK_COUNT=$((LINK_COUNT + 1))
  if [ "$LINK_COUNT" -gt 40 ]; then
    printf '安装入口软链接链过长或存在循环。\n' >&2
    exit 1
  fi
  SOURCE_DIR="$(cd -P "$(dirname "$SOURCE_PATH")" && pwd)"
  SOURCE_PATH="$(readlink "$SOURCE_PATH")"
  case "$SOURCE_PATH" in /*) ;; *) SOURCE_PATH="$SOURCE_DIR/$SOURCE_PATH" ;; esac
done
REPO_DIR="$(cd -P "$(dirname "$SOURCE_PATH")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  printf '需要 Python 3.9+。请先安装 Python，再运行此命令；未修改配置。\n' >&2
  exit 1
fi
if ! python3 -B -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
  printf '需要 Python 3.9+；当前 python3 版本过低，未修改配置。\n' >&2
  exit 1
fi
export PYTHONDONTWRITEBYTECODE=1
if [ -n "$INSTALLED_ROOT" ]; then
  exec python3 -B "$REPO_DIR/scripts/setup-codex-config.py" --codex-home "$INSTALLED_ROOT" "$@"
fi
exec python3 -B "$REPO_DIR/scripts/setup-codex-config.py" "$@"
