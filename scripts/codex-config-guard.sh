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
export PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-${TMPDIR:-/tmp}/codex-config-pycache}"

fail() {
  printf 'codex-config guard 失败：%s\n' "$1" >&2
  exit 1
}

require_path() {
  local path="$1"
  [ -e "$ROOT_DIR/$path" ] || fail "缺少 $path"
}

cd "$ROOT_DIR"

for path in \
  AGENTS.md \
  README.md \
  hooks/hooks.json \
  hooks/codex-policy-guard.py \
  git-hooks/pre-commit \
  git-hooks/pre-push \
  scripts/restore-codex-global-links.sh \
  scripts/restore-codex-official-state.sh \
  scripts/codex-config-guard.sh \
  scripts/install-git-hooks.sh \
  scripts/secret-scan.py \
  scripts/test-policy-guard.py \
  scripts/test-restore-roundtrip.sh \
  scripts/test-secret-scan.sh \
  scripts/workspace-cleanliness-check.sh \
  docs/project-codex-config-template.md \
  docs/project-expansion-workflow.md \
  docs/project-AGENTS-template.md \
  docs/project-plan-template.md \
  docs/hook-enforcement-policy.md \
  docs/git-workflow-policy.md
do
  require_path "$path"
done

bash -n scripts/restore-codex-global-links.sh
bash -n scripts/restore-codex-official-state.sh
bash -n scripts/codex-config-guard.sh
bash -n scripts/install-git-hooks.sh
bash -n scripts/test-restore-roundtrip.sh
bash -n scripts/test-secret-scan.sh
bash -n scripts/workspace-cleanliness-check.sh
bash -n git-hooks/pre-commit
bash -n git-hooks/pre-push

python3 -m json.tool hooks/hooks.json >/dev/null
python3 -m py_compile hooks/codex-policy-guard.py
python3 -m py_compile scripts/secret-scan.py
python3 -m py_compile scripts/test-policy-guard.py
python3 scripts/secret-scan.py
python3 scripts/test-policy-guard.py
bash scripts/test-restore-roundtrip.sh
bash scripts/test-secret-scan.sh
bash scripts/workspace-cleanliness-check.sh

for spark_agent in agents/*-spark.toml; do
  rg -q '^model = "gpt-5\.3-codex-spark"$' "$spark_agent" ||
    fail "spark 角色模型未固定：$spark_agent"
  rg -q '^sandbox_mode = "read-only"$' "$spark_agent" ||
    fail "spark 角色未设置只读沙箱：$spark_agent"
done

for stale_copy in \
  skills/project-bootstrap/references/project-expansion-workflow.md \
  skills/project-bootstrap/references/project-AGENTS-template.md
do
  [ ! -e "$stale_copy" ] || fail "发现重复模板副本：$stale_copy"
done

rg -q -F '../../docs/project-expansion-workflow.md' \
  skills/project-bootstrap/SKILL.md ||
  fail "project-bootstrap 未引用项目展开真源文档"
rg -q -F '../../docs/project-AGENTS-template.md' \
  skills/project-bootstrap/SKILL.md ||
  fail "project-bootstrap 未引用项目 AGENTS 真源模板"
rg -q -F '../../docs/project-codex-config-template.md' \
  skills/project-bootstrap/SKILL.md ||
  fail "project-bootstrap 未引用项目 Codex 配置真源模板"

agents_bytes="$(wc -c <AGENTS.md | tr -d '[:space:]')"
[ "$agents_bytes" -le 24576 ] ||
  fail "AGENTS.md 超过 24 KiB 轻量上限：${agents_bytes} bytes"

if rg -n -F "$ROOT_DIR" scripts README.md docs >/dev/null; then
  fail "便携文件中包含本机 global-config 绝对路径"
fi

printf 'codex-config guard 通过。\n'
