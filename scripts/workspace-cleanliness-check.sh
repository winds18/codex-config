#!/usr/bin/env bash
set -euo pipefail

# Judge what would be committed. Unstaged/ignored local noise is advisory.
python3 - <<'PY'
from pathlib import Path
import subprocess
import sys

result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True)
if result.returncode:
    print('工作区清洁检查失败：当前目录不是 Git 仓库', file=sys.stderr)
    raise SystemExit(1)
root = Path(result.stdout.decode().strip())
result = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z'],
                        cwd=root, check=True, capture_output=True)
paths = [Path(raw.decode('utf-8', 'surrogateescape')) for raw in result.stdout.split(b'\0') if raw]


def noise(path):
    return path.name == '.DS_Store' or path.suffix.lower() in {'.tmp', '.temp', '.bak', '.log'}


staged = [path for path in paths if noise(path) or {'.tmp', '.artifacts', '.cache'} & set(path.parts[:-1])]
if staged:
    print('工作区清洁检查失败：已暂存临时文件，请检查并移出提交：', file=sys.stderr)
    for path in staged:
        print(f'- {str(path)!r}', file=sys.stderr)
    raise SystemExit(1)
local_noise = [path.name for path in root.iterdir() if path.is_file() and noise(path)]
if local_noise:
    print('工作区清洁提示：根目录有未纳入本次提交的临时文件（不阻断）：', file=sys.stderr)
    for name in sorted(local_noise):
        print(f'- {name!r}', file=sys.stderr)
print('工作区清洁检查通过。')
PY
