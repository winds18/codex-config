#!/usr/bin/env bash
set -euo pipefail
SOURCE_PATH="${BASH_SOURCE[0]}"
while [ -L "$SOURCE_PATH" ]; do
  SOURCE_DIR="$(cd -P "$(dirname "$SOURCE_PATH")" && pwd)"
  SOURCE_PATH="$(readlink "$SOURCE_PATH")"
  case "$SOURCE_PATH" in /*) ;; *) SOURCE_PATH="$SOURCE_DIR/$SOURCE_PATH" ;; esac
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE_PATH")" && pwd)"
exec python3 "$SCRIPT_DIR/manage-git-hooks.py" "$@"
