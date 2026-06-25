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
  printf 'codex-config guard failed: %s\n' "$1" >&2
  exit 1
}

require_path() {
  local path="$1"
  [ -e "$ROOT_DIR/$path" ] || fail "missing $path"
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
  docs/project-expansion-workflow.md \
  docs/project-AGENTS-template.md \
  docs/hook-enforcement-policy.md \
  docs/git-workflow-policy.md \
  skills/project-bootstrap/references/project-expansion-workflow.md \
  skills/project-bootstrap/references/project-AGENTS-template.md
do
  require_path "$path"
done

bash -n scripts/restore-codex-global-links.sh
bash -n scripts/restore-codex-official-state.sh
bash -n scripts/codex-config-guard.sh
bash -n scripts/install-git-hooks.sh
bash -n git-hooks/pre-commit
bash -n git-hooks/pre-push

python3 -m json.tool hooks/hooks.json >/dev/null
python3 -m py_compile hooks/codex-policy-guard.py

diff -u docs/project-expansion-workflow.md \
  skills/project-bootstrap/references/project-expansion-workflow.md >/dev/null
diff -u docs/project-AGENTS-template.md \
  skills/project-bootstrap/references/project-AGENTS-template.md >/dev/null

if rg -n -F "$ROOT_DIR" scripts README.md docs >/dev/null; then
  fail "portable files contain hardcoded local global-config path"
fi

printf 'codex-config guard passed.\n'
