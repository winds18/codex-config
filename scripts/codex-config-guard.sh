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

require_text() {
  local path="$1"
  local text="$2"
  rg -n -F "$text" "$ROOT_DIR/$path" >/dev/null || fail "$path missing required text: $text"
}

cd "$ROOT_DIR"

for path in \
  AGENTS.md \
  AGENTS.override.md \
  README.md \
  hooks/hooks.json \
  hooks/codex-policy-guard.py \
  git-hooks/pre-commit \
  git-hooks/pre-push \
  prompts/agent-work-habits.md \
  prompts/subagent-work-habits.md \
  agents/orchestrator.toml \
  agents/planner.toml \
  agents/worker.toml \
  agents/explorer-lite.toml \
  agents/reviewer-lite.toml \
  agents/tester-lite.toml \
  agents/security-lite.toml \
  agents/security-reviewer.toml \
  agents/summarizer-lite.toml \
  agents/refiner.toml \
  agents/pr-preparer.toml \
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
  docs/git-workflow-policy.md \
  skills/refero-design-prompts/SKILL.md \
  skills/refero-design-prompts/references/style-taxonomy.md \
  skills/refero-design-prompts/references/substyle-recipes.md \
  skills/refero-design-prompts/references/output-templates.md
do
  require_path "$path"
done

agents_bytes="$(wc -c < AGENTS.md | tr -d '[:space:]')"
[ "$agents_bytes" -le 14000 ] || fail "AGENTS.md exceeds 14000 bytes; keep global guidance concise"

override_bytes="$(wc -c < AGENTS.override.md | tr -d '[:space:]')"
[ "$override_bytes" -le 6000 ] || fail "AGENTS.override.md exceeds 6000 bytes; keep project override concise"

for text in \
  "## 系统开发" \
  "Architecture Baseline" \
  "模块边界、接口契约、数据结构、依赖方向、并行工作包和验收方式" \
  "主编排者是技术负责人" \
  "自顶向下" \
  "统一领域模型" \
  "对应领域的默认工程规范" \
  "核心算法" \
  "理论依据" \
  "执行效率" \
  "成熟、现代、可靠的工程模式" \
  "不得为了新颖性引入复杂模式" \
  "可独立验证的工作包"
do
  require_text "prompts/agent-work-habits.md" "$text"
done

for text in \
  "## 边界" \
  "不改写核心抽象" \
  "Architecture Baseline" \
  "契约冲突" \
  "结论、关键证据、变更范围、验证结果、风险或未验证项"
do
  require_text "prompts/subagent-work-habits.md" "$text"
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

if rg -n "AGENTS\.override\.md" scripts/restore-codex-global-links.sh >/dev/null; then
  fail "restore script 不得把 AGENTS.override.md 链接到 CODEX_HOME"
fi

if rg -n "gpt-5\.3-codex-spark" agents >/dev/null; then
  fail "agent 配置仍引用 gpt-5.3-codex-spark；应使用当前 5.6 模型族"
fi

if find agents -maxdepth 1 -type f -name '*-spark.toml' | rg . >/dev/null; then
  fail "agent 配置仍使用旧 *-spark 文件名；应使用 *-lite 命名"
fi

printf 'codex-config guard 通过。\n'
