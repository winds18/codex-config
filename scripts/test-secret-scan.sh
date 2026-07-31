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
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/codex-secret-test.XXXXXX")"
TEST_REPO="$TEST_ROOT/repo"

cleanup() {
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

fail() {
  printf '敏感信息扫描测试失败：%s\n' "$1" >&2
  exit 1
}

mkdir -p "$TEST_REPO"
git -C "$TEST_REPO" init -q
git -C "$TEST_REPO" config user.name "Codex Guard Test"
git -C "$TEST_REPO" config user.email "codex-guard@example.invalid"

printf 'safe\n' >"$TEST_REPO/README.md"
git -C "$TEST_REPO" add README.md
git -C "$TEST_REPO" commit -q -m "test: 初始提交"

secret_prefix="sk"
printf 'token=%s\n' "${secret_prefix}-AAAAAAAAAAAAAAAAAAAAAAAA" \
  >"$TEST_REPO/temporary-secret.txt"
git -C "$TEST_REPO" add temporary-secret.txt
git -C "$TEST_REPO" commit -q -m "test: 加入模拟敏感值"
rm "$TEST_REPO/temporary-secret.txt"
git -C "$TEST_REPO" add -u
git -C "$TEST_REPO" commit -q -m "test: 删除模拟敏感值"

local_sha="$(git -C "$TEST_REPO" rev-parse HEAD)"
if printf 'refs/heads/main %s refs/heads/main %040d\n' "$local_sha" 0 |
  (
    cd "$TEST_REPO"
    python3 "$ROOT_DIR/scripts/secret-scan.py" --pre-push >/dev/null 2>&1
  ); then
  fail "未发现待推送历史中已被后续删除的敏感值"
fi

printf 'SAFE=true\n' >"$TEST_REPO/.env"
git -C "$TEST_REPO" add -f .env
if (
  cd "$TEST_REPO"
  python3 "$ROOT_DIR/scripts/secret-scan.py" >/dev/null 2>&1
); then
  fail "未阻断已暂存的 .env 文件"
fi

git -C "$TEST_REPO" reset -q HEAD .env
rm "$TEST_REPO/.env"
printf 'SAFE_PLACEHOLDER=true\n' >"$TEST_REPO/.env.example"
git -C "$TEST_REPO" add .env.example
(
  cd "$TEST_REPO"
  python3 "$ROOT_DIR/scripts/secret-scan.py" >/dev/null
) || fail "错误阻断 .env.example"

printf '敏感信息扫描测试通过。\n'
