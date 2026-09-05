#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONDONTWRITEBYTECODE=1

# 结构、引用和真实行为；不锁定模型代际或自然语言原句。
python3 scripts/validate-config.py
for script in install.sh scripts/*.sh git-hooks/*; do
  bash -n "$script"
done
python3 - <<'CHECK_PYTHON'
import ast
from pathlib import Path
for folder in ('scripts', 'hooks'):
    for path in Path(folder).glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
print('Shell/Python 语法检查通过。')
CHECK_PYTHON

python3 scripts/secret-scan.py
python3 scripts/test-policy-guard.py
bash scripts/test-secret-scan.sh
bash scripts/test-restore-roundtrip.sh
python3 scripts/test-setup-entrypoint.py
bash skills/refero-design-prompts/scripts/verify-template-assets.sh
python3 skills/refero-design-prompts/scripts/test-template-dependencies.py
bash scripts/workspace-cleanliness-check.sh
printf 'codex-config guard 通过。\n'
