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
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
BASE_DIR="${BASE_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)}"
MODE="${1:---apply}"

log() {
  printf '%s\n' "$1"
}

run() {
  if [ "$MODE" = "--dry-run" ]; then
    log "[dry-run] $*"
  else
    eval "$@"
  fi
}

remove_if_symlink_to_global() {
  local path="$1"

  if [ -L "$path" ]; then
    local target
    target="$(readlink "$path")"
    case "$target" in
      "$BASE_DIR"/*)
        run "rm -f \"$path\""
        ;;
      *)
        log "skip: $path is a symlink, but not to $BASE_DIR"
        ;;
    esac
  fi
}

restore_agents_md() {
  local live="$CODEX_HOME/AGENTS.md"
  local backup="$CODEX_HOME/AGENTS.md.bak"
  local will_remove_live="false"

  if [ -L "$live" ]; then
    local target
    target="$(readlink "$live")"
    case "$target" in
      "$BASE_DIR"/AGENTS.md)
        will_remove_live="true"
        run "rm -f \"$live\""
        ;;
    esac
  fi

  if [ -f "$backup" ] && { [ ! -e "$live" ] || [ "$will_remove_live" = "true" ]; }; then
    run "mv \"$backup\" \"$live\""
  fi
}

restore_skills() {
  local skills_dir="$CODEX_HOME/skills"
  [ -d "$skills_dir" ] || return 0

  local skill
  for skill in project-bootstrap autonomous-project-execution feature-thread-launch; do
    remove_if_symlink_to_global "$skills_dir/$skill"
  done
}

restore_entrypoints() {
  remove_if_symlink_to_global "$CODEX_HOME/agents"
  remove_if_symlink_to_global "$CODEX_HOME/prompts"
  remove_if_symlink_to_global "$CODEX_HOME/docs"
  remove_if_symlink_to_global "$CODEX_HOME/hooks.json"
  remove_if_symlink_to_global "$CODEX_HOME/hooks"
  remove_if_symlink_to_global "$CODEX_HOME/restore-global-setup.sh"
  remove_if_symlink_to_global "$CODEX_HOME/restore-official-state.sh"
}

main() {
  if [ "$MODE" != "--apply" ] && [ "$MODE" != "--dry-run" ]; then
    log "Usage: $0 [--apply|--dry-run]"
    exit 1
  fi

  restore_agents_md
  restore_entrypoints
  restore_skills

  log "Codex official-state restore ${MODE#--} complete."
  log "CODEX_HOME=$CODEX_HOME"
  if [ "$MODE" = "--apply" ]; then
    log "Reopen Codex or start a new session to ensure the reverted state is reflected."
  fi
}

main
