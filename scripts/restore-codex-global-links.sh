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
BASE_DIR="${BASE_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

backup_if_needed() {
  local path="$1"

  if [ -L "$path" ]; then
    return 0
  fi

  if [ -e "$path" ]; then
    mv "$path" "${path}.bak.${TIMESTAMP}"
  fi
}

link_path() {
  local target="$1"
  local link_path="$2"
  local parent_dir
  parent_dir="$(dirname "$link_path")"

  mkdir -p "$parent_dir"
  backup_if_needed "$link_path"
  ln -sfn "$target" "$link_path"
}

mkdir -p "$CODEX_HOME"
mkdir -p "$CODEX_HOME/skills"

link_path "$BASE_DIR/AGENTS.md" "$CODEX_HOME/AGENTS.md"
link_path "$BASE_DIR/agents" "$CODEX_HOME/agents"
link_path "$BASE_DIR/prompts" "$CODEX_HOME/prompts"
link_path "$BASE_DIR/docs" "$CODEX_HOME/docs"
link_path "$BASE_DIR/hooks/hooks.json" "$CODEX_HOME/hooks.json"
link_path "$BASE_DIR/hooks" "$CODEX_HOME/hooks"
link_path "$BASE_DIR/scripts/restore-codex-global-links.sh" \
  "$CODEX_HOME/restore-global-setup.sh"
link_path "$BASE_DIR/scripts/restore-codex-official-state.sh" \
  "$CODEX_HOME/restore-official-state.sh"

link_path "$BASE_DIR/skills/project-bootstrap" \
  "$CODEX_HOME/skills/project-bootstrap"
link_path "$BASE_DIR/skills/autonomous-project-execution" \
  "$CODEX_HOME/skills/autonomous-project-execution"
link_path "$BASE_DIR/skills/feature-thread-launch" \
  "$CODEX_HOME/skills/feature-thread-launch"

echo "Codex global links restored."
echo "BASE_DIR=$BASE_DIR"
echo "CODEX_HOME=$CODEX_HOME"
echo "Reopen Codex or start a new session if new skills or prompts are not visible yet."
