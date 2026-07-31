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
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/codex-restore-test.XXXXXX")"
TEST_CODEX_HOME="$TEST_ROOT/.codex"
FOREIGN_SKILL="$TEST_ROOT/original-refero"

cleanup() {
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

fail() {
  printf '恢复回环测试失败：%s\n' "$1" >&2
  exit 1
}

mkdir -p "$TEST_CODEX_HOME/agents" "$TEST_CODEX_HOME/skills" "$FOREIGN_SKILL"
printf '原始 AGENTS\n' >"$TEST_CODEX_HOME/AGENTS.md"
printf '原始代理目录\n' >"$TEST_CODEX_HOME/agents/original.txt"
printf '{"source":"original"}\n' >"$TEST_CODEX_HOME/hooks.json"
printf '原始 Refero\n' >"$FOREIGN_SKILL/original.txt"
ln -s "$FOREIGN_SKILL" "$TEST_CODEX_HOME/skills/refero-design-system"

BASE_DIR="$ROOT_DIR" CODEX_HOME="$TEST_CODEX_HOME" \
  bash "$ROOT_DIR/scripts/restore-codex-global-links.sh" >/dev/null

[ -L "$TEST_CODEX_HOME/AGENTS.md" ] || fail "安装后 AGENTS.md 不是软连接"
[ -L "$TEST_CODEX_HOME/skills/refero-design-system" ] ||
  fail "安装后 refero-design-system 不是软连接"

BASE_DIR="$ROOT_DIR" CODEX_HOME="$TEST_CODEX_HOME" \
  bash "$ROOT_DIR/scripts/restore-codex-official-state.sh" --dry-run >/dev/null
[ -L "$TEST_CODEX_HOME/AGENTS.md" ] || fail "dry-run 修改了 AGENTS.md"

BASE_DIR="$ROOT_DIR" CODEX_HOME="$TEST_CODEX_HOME" \
  bash "$ROOT_DIR/scripts/restore-codex-official-state.sh" --apply >/dev/null

[ ! -L "$TEST_CODEX_HOME/AGENTS.md" ] || fail "AGENTS.md 仍是软连接"
[ "$(sed -n '1p' "$TEST_CODEX_HOME/AGENTS.md")" = "原始 AGENTS" ] ||
  fail "AGENTS.md 原内容未恢复"
[ "$(sed -n '1p' "$TEST_CODEX_HOME/agents/original.txt")" = "原始代理目录" ] ||
  fail "agents 原目录未恢复"
[ "$(sed -n '1p' "$TEST_CODEX_HOME/hooks.json")" = '{"source":"original"}' ] ||
  fail "hooks.json 原文件未恢复"
[ -L "$TEST_CODEX_HOME/skills/refero-design-system" ] ||
  fail "refero-design-system 原软连接未恢复"
[ "$(readlink "$TEST_CODEX_HOME/skills/refero-design-system")" = "$FOREIGN_SKILL" ] ||
  fail "refero-design-system 原软连接目标不一致"
[ ! -e "$TEST_CODEX_HOME/docs" ] && [ ! -L "$TEST_CODEX_HOME/docs" ] ||
  fail "原本不存在的 docs 入口未恢复为缺省状态"

if find "$TEST_CODEX_HOME" -name '*.codex-config-backup.*' -print -quit |
  grep -q .; then
  fail "恢复后残留本轮备份文件"
fi

printf '恢复回环测试通过。\n'
