#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHONDONTWRITEBYTECODE=1 exec python3 "$SCRIPT_DIR/test-restore-roundtrip.py"
