#!/usr/bin/env bash
set -euo pipefail
SOURCE_PATH="${BASH_SOURCE[0]}"
ROOT_PATH=""
if [ -L "$SOURCE_PATH" ]; then
  case "$(basename "$SOURCE_PATH")" in
    restore-global-setup.sh|restore-official-state.sh)
      ROOT_PATH="$(cd -P "$(dirname "$SOURCE_PATH")" && pwd)" ;;
  esac
fi
while [ -L "$SOURCE_PATH" ]; do
  SOURCE_DIR="$(cd -P "$(dirname "$SOURCE_PATH")" && pwd)"
  SOURCE_PATH="$(readlink "$SOURCE_PATH")"
  case "$SOURCE_PATH" in /*) ;; *) SOURCE_PATH="$SOURCE_DIR/$SOURCE_PATH" ;; esac
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE_PATH")" && pwd)"
if [ -n "$ROOT_PATH" ]; then
  exec python3 "$SCRIPT_DIR/manage-codex-config.py" uninstall --codex-home "$ROOT_PATH" "$@"
fi
exec python3 "$SCRIPT_DIR/manage-codex-config.py" uninstall "$@"
