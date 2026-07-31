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

is_managed_symlink() {
  local path="$1"
  local target

  [ -L "$path" ] || return 1
  target="$(readlink "$path")"
  case "$target" in
    "$BASE_DIR"/*) return 0 ;;
    *) return 1 ;;
  esac
}

newest_matching_backup() {
  local path="$1"
  local candidate
  local newest=""

  for candidate in "${path}.codex-config-backup."*; do
    [ -e "$candidate" ] || [ -L "$candidate" ] || continue
    if [ -z "$newest" ] || [[ "$candidate" > "$newest" ]]; then
      newest="$candidate"
    fi
  done

  if [ -n "$newest" ]; then
    printf '%s\n' "$newest"
    return 0
  fi

  for candidate in "${path}.bak."*; do
    [ -e "$candidate" ] || [ -L "$candidate" ] || continue
    if [ -z "$newest" ] || [[ "$candidate" > "$newest" ]]; then
      newest="$candidate"
    fi
  done

  if [ -n "$newest" ]; then
    printf '%s\n' "$newest"
    return 0
  fi

  if [ -e "${path}.bak" ] || [ -L "${path}.bak" ]; then
    printf '%s\n' "${path}.bak"
  fi
}

restore_managed_path() {
  local path="$1"
  local backup=""

  if ! is_managed_symlink "$path"; then
    if [ -L "$path" ]; then
      log "跳过非本仓库软连接：$path"
    fi
    return 0
  fi

  backup="$(newest_matching_backup "$path")"
  if [ "$MODE" = "--dry-run" ]; then
    log "[dry-run] 删除本仓库软连接：$path"
    if [ -n "$backup" ]; then
      log "[dry-run] 恢复原入口：$backup -> $path"
    fi
    return 0
  fi

  rm -f "$path"
  log "已删除本仓库软连接：$path"
  if [ -n "$backup" ]; then
    mv "$backup" "$path"
    log "已恢复原入口：$backup -> $path"
  fi
}

main() {
  local mode_label
  local path

  if [ "$MODE" != "--apply" ] && [ "$MODE" != "--dry-run" ]; then
    log "用法：$0 [--apply|--dry-run]"
    exit 1
  fi

  for path in \
    "$CODEX_HOME/AGENTS.md" \
    "$CODEX_HOME/agents" \
    "$CODEX_HOME/prompts" \
    "$CODEX_HOME/docs" \
    "$CODEX_HOME/hooks.json" \
    "$CODEX_HOME/hooks" \
    "$CODEX_HOME/restore-global-setup.sh" \
    "$CODEX_HOME/restore-official-state.sh" \
    "$CODEX_HOME/skills/project-bootstrap" \
    "$CODEX_HOME/skills/autonomous-project-execution" \
    "$CODEX_HOME/skills/feature-thread-launch" \
    "$CODEX_HOME/skills/refero-design-system"
  do
    restore_managed_path "$path"
  done

  if [ "$MODE" = "--dry-run" ]; then
    mode_label="预览"
  else
    mode_label="执行"
  fi
  log "Codex 官方状态恢复${mode_label}完成。"
  log "Codex 目录：$CODEX_HOME"
  if [ "$MODE" = "--apply" ]; then
    log "请重新打开 Codex 或开启新任务，确保恢复后的状态生效。"
  fi
}

main
