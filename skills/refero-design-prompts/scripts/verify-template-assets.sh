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
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_ROOT="$SKILL_DIR/assets/templates"
AWESOME_ROOT="$TEMPLATE_ROOT/awesome-design-md"
HOMEPAGE_ROOT="$TEMPLATE_ROOT/personal-homepage-skill"

fail() {
  printf '模板资产校验失败：%s\n' "$1" >&2
  exit 1
}

require_file() {
  local path="$1"
  [ -f "$path" ] || fail "缺少文件：${path#"$SKILL_DIR/"}"
}

count_files() {
  local root="$1"
  local name="$2"
  find "$root" -type f -name "$name" | wc -l | tr -d '[:space:]'
}

for path in \
  "$AWESOME_ROOT/LICENSE" \
  "$AWESOME_ROOT/README.md" \
  "$AWESOME_ROOT/SOURCE.md" \
  "$AWESOME_ROOT/UPSTREAM_COMMIT" \
  "$HOMEPAGE_ROOT/LICENSE" \
  "$HOMEPAGE_ROOT/README.md" \
  "$HOMEPAGE_ROOT/SOURCE.md" \
  "$HOMEPAGE_ROOT/UPSTREAM_COMMIT" \
  "$HOMEPAGE_ROOT/STYLE_PRESETS.md" \
  "$HOMEPAGE_ROOT/src/data/templates.ts" \
  "$HOMEPAGE_ROOT/demo/template-gallery.html" \
  "$HOMEPAGE_ROOT/templates/hero/portable/index.html" \
  "$HOMEPAGE_ROOT/templates/react-tailwind/App.tsx" \
  "$HOMEPAGE_ROOT/templates/single-html/personal-homepage.html" \
  "$HOMEPAGE_ROOT/templates/presentation-html/presentation.html"
do
  require_file "$path"
done

[ "$(tr -d '[:space:]' < "$AWESOME_ROOT/UPSTREAM_COMMIT")" = \
  "8147538b4226ae41e2487a9179e3bcc1f68e8554" ] ||
  fail "awesome-design-md 快照 commit 不一致"
[ "$(tr -d '[:space:]' < "$HOMEPAGE_ROOT/UPSTREAM_COMMIT")" = \
  "4055fabb1b67637364d375e18eb9ae13467a03db" ] ||
  fail "personal-homepage-skill 快照 commit 不一致"

awesome_dir_count="$(find "$AWESOME_ROOT/design-md" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d '[:space:]')"
[ "$awesome_dir_count" -eq 74 ] ||
  fail "awesome-design-md 期望 74 个模板目录，实际 $awesome_dir_count"

awesome_design_count="$(count_files "$AWESOME_ROOT/design-md" 'DESIGN.md')"
[ "$awesome_design_count" -eq 74 ] ||
  fail "awesome-design-md 期望 74 个 DESIGN.md，实际 $awesome_design_count"

while IFS= read -r template_dir; do
  require_file "$template_dir/DESIGN.md"
done < <(find "$AWESOME_ROOT/design-md" -mindepth 1 -maxdepth 1 -type d | sort)

homepage_template_count="$(rg -c "^[[:space:]]+id: '" "$HOMEPAGE_ROOT/src/data/templates.ts")"
[ "$homepage_template_count" -eq 19 ] ||
  fail "personal-homepage-skill 期望 19 个模板定义，实际 $homepage_template_count"

homepage_preview_count="$(count_files "$HOMEPAGE_ROOT/assets/template-previews" '*.svg')"
[ "$homepage_preview_count" -eq 18 ] ||
  fail "personal-homepage-skill 期望 18 个 SVG 模板预览，实际 $homepage_preview_count"

source_video_count="$(count_files "$HOMEPAGE_ROOT/templates/hero/assets/videos" '*.mp4')"
portable_video_count="$(count_files "$HOMEPAGE_ROOT/templates/hero/portable/assets/videos" '*.mp4')"
[ "$source_video_count" -eq 5 ] ||
  fail "Hero 源模板期望 5 个视频，实际 $source_video_count"
[ "$portable_video_count" -eq 5 ] ||
  fail "Hero 便携模板期望 5 个视频，实际 $portable_video_count"

if find "$TEMPLATE_ROOT" -type d \( \
  -name .git -o -name .github -o -name node_modules -o -name dist \
\) -print -quit | rg . >/dev/null; then
  fail "模板快照包含不应入库的仓库或构建目录"
fi

if find "$TEMPLATE_ROOT" -type f -size +100M -print -quit | rg . >/dev/null; then
  fail "模板快照包含超过 GitHub 单文件限制的资产"
fi

if find "$TEMPLATE_ROOT" -type f -empty -print -quit | rg . >/dev/null; then
  fail "模板快照包含空文件"
fi

# 只进行离线静态检查；不安装依赖、不执行上游代码。
python3 "$SCRIPT_DIR/verify-template-dependencies.py"
printf '前端模板资产校验通过。\n'
