# 前端技能逐文件复核与优化

日期：2026-09-05。范围：`skills/refero-design-prompts/` 全目录。本轮修改自维护规范和检查脚本，294 个上游快照文件保持原样。

## 结论与已实施优化

原入口 131 行和 references 1106 行将普通设计选择扩展成固定产物、重复 token schema、严格动效审批，容易增加上下文和串行等待。当前入口 45 行，references 739 行，整体从 1237 行降至 784 行（约减少 37%）。更重要的是普通修复无需加载，参考库仍按实际选择读取。

- 接受现有 Figma、CSS tokens、组件库和设计文档为权威来源；`DESIGN.md` 引用它们并记录差异/验收，删除强制 YAML 复制 token 数值和全量状态表。
- 先对齐最小共享 token / 接口 / 文件 owner，然后允许不同页面、组件及验证任务并行。共享基础文件集中修改，不把整个前端锁成单人串行。
- 用户要求实现时继续代码和验证；不再固定输出五个章节，也不为小改创建完整设计系统、Motion Contract 或审批工序。
- 删除 ease-in、纯 fade、超过 300ms、居中布局等绝对美学阻断。保留键盘/触控、reduced motion、中断、状态正确性、性能和真实渲染证据。
- 明确 vendor 内 SKILL/prompt 只是资料；既有方向和用户来源优先于默认模板。非商业许可、品牌/人物媒体和示例数据分别核实，不能从顶层代码 license 推定素材授权。
- 原资产 guard 仅覆盖计数和固定文件；新增离线静态依赖、package/lock、入口、来源标记和媒体摘要校验，并用故障注入测试验证漏检边界。

## 自维护文件覆盖

以下文件逐个完整阅读并检查调用关系；新文件按实现检查及测试验证。

| 文件（相对技能目录） | 本轮处理 |
| --- | --- |
| `SKILL.md` | 精简入口、精确触发、按需读取、现有事实源优先、并行边界、实现交付与许可边界 |
| `agents/openai.yaml` | 保留 display name，缩小默认 prompt 到实际需要的交付，保留隐式选择默认行为 |
| `references/design-md-contract.md` | 151 → 46 行；引用实现与 Figma，不制造 token 双真源；移除无消费者的强制 YAML/linter |
| `references/motion-craft-workflow.md` | 110 → 45 行；删除未安装术语 skill 依赖和机械美学阻断，保留关键动效风险验证 |
| `references/output-templates.md` | 255 → 54 行；删除重复 token schema 和固定五段输出；只保留按需骨架 |
| `references/style-taxonomy.md` | 全文复核，保留 6 类参考；增加偏好不覆盖项目/用户选择的边界 |
| `references/substyle-recipes.md` | 全文复核，保留 3 个细分方向；作为可选细化，不升级为全局风格规则 |
| `references/visual-archetypes.md` | 全文复核 14 个原型，保留按需资料；修正与入口不一致的素材复制边界及绝对视觉禁令 |
| `scripts/verify-template-assets.sh` | 保留原入口与固定快照结构验证，接入新静态依赖检查；不安装依赖或执行 vendor |
| `scripts/verify-template-dependencies.py` | 新增：全文件分类、UTF-8/JSON/SVG/媒体头、来源标记、字面量依赖、package scripts/lock、媒体 SHA-256 |
| `scripts/test-template-dependencies.py` | 新增 7 项测试，在临时副本注入缺模块、缺脚本、锁不一致、commit/媒体篡改及符号链接 |

## 上游快照与脚本入口

| 快照 | 文件数 | commit 标记 | 顶层许可 | 验证层次 |
| --- | ---: | --- | --- | --- |
| awesome-design-md | 153 | `8147538b4226ae41e2487a9179e3bcc1f68e8554` | MIT | SOURCE/commit/LICENSE 一致，74 个设计目录，逐文件存在、文本/链接静态检查 |
| personal-homepage-skill | 141 | `4055fabb1b67637364d375e18eb9ae13467a03db` | Personal Homepage Skill Non-Commercial License | SOURCE/commit/LICENSE 一致，19 个 registry 项，18 个 SVG，模块/资源/脚本/锁静态检查 |

SOURCE 标记只证明本地记录一致，未重新拉取远程 commit 对整个快照做独立逐字节对照。Hero 6 个原始媒体及其 6 个 portable 副本逐个与上游 README 的 SHA-256 核对通过。媒体原始说明称其来自上游用户项目，不能据此证明当前使用者拥有第三方人物/品牌素材权利。

脚本入口逐个检查：

| vendor 脚本 | 作用与检查 |
| --- | --- |
| `scripts/check-spec.mjs` | 文档/目录静态检查；已执行通过 |
| `scripts/check-templates.mjs` | 19 个模板 registry 元数据；已执行通过 |
| `scripts/check-visual.mjs` | CSS/组件静态规则；已执行通过，不等于视觉截图验收 |
| `scripts/build-hero-portable.mjs` | Vite 构建并写 portable；入口/导入/语法检查，未执行以保持快照原样 |
| `scripts/capture-slides.mjs` | Playwright 截图及输出报告；入口/语法检查，未执行 |
| `scripts/verify-html-ppt-stage.mjs` | Playwright 布局/交互验收；入口/语法检查，未执行 |
| `scripts/test-export-html.mjs` | Playwright 导出检查；语法检查，非 package scripts 主入口，需显式输入 HTML |
| `tests/homepage-qa-rules.test.mjs` | 文档规范静态检查；已执行通过 |
| 其余 5 个 `tests/*.test.mjs` | Playwright/Vite 或子进程浏览器验收；各入口/语法检查，未执行浏览器 |

`package.json` 的 15 个 script 名称与 node 入口、npm run 内部引用均可定位；根 package 声明与 package-lock 的 name/version/dependencies/devDependencies/engines 一致。没有安装任何依赖；未评估所有传递依赖版本或安全公告。

## 验证结果与限制

- `bash skills/refero-design-prompts/scripts/verify-template-assets.sh`：通过；294 文件、152 个字面量本地引用、0 错误。
- `python3 -B skills/refero-design-prompts/scripts/test-template-dependencies.py`：7/7 通过。
- Node v24.19.0 对上面 4 个无外部依赖脚本执行通过，对 16 个 `.js/.mjs` 文件 `--check` 通过。
- 自维护 shell syntax、Python AST、技能 name/description 字段、Markdown 引用、UI metadata 字段与长度、`git diff --check` 通过。
- 初次运行缺少 PyYAML；集成阶段已将 PyYAML/tomli 安装到临时目录，四个技能均通过官方 `skill-creator/scripts/quick_validate.py`，角色 TOML 与 openai.yaml 也通过完整解析。系统 Python 与项目依赖未修改。
- 唯一缺失引用：`tests/fixtures/broken-image.html → ./does-not-exist.png`，是刻意损坏的负向测试，精确列入例外；生产模板中未发现此次静态提取可识别的缺失本地依赖。
- 未逐模板运行浏览器、未执行 TS 类型检查/完整 Vite 构建、未解析动态 URL/包传递引用/Markdown 锚点、未访问远程字体/CDN；SVG/XML 或媒体头通过不代表视觉/编码质量已通过。需要实际使用的模板，在目标项目运行相应构建和渲染验收。

## 全部 vendor 文件清单

路径相对 `assets/templates/`；“静态检查通过”仅表示本次离线可检查项通过，不代表逐行语义审计或全部运行验收。分类为机器生成清单，不是另一个手工模板发现索引。

| 快照内路径 | 分类 | 字节 | 本地引用 | 结果/边界 |
| --- | --- | ---: | ---: | --- |
| `awesome-design-md/.gitignore` | 说明/设计参考 | 10 | 0 | 静态检查通过 |
| `awesome-design-md/CONTRIBUTING.md` | 说明/设计参考 | 912 | 0 | 静态检查通过 |
| `awesome-design-md/LICENSE` | 来源/许可 | 1066 | 0 | 静态检查通过 |
| `awesome-design-md/README.md` | 说明/设计参考 | 16023 | 2 | 静态检查通过 |
| `awesome-design-md/SOURCE.md` | 来源/许可 | 445 | 0 | 静态检查通过 |
| `awesome-design-md/UPSTREAM_COMMIT` | 来源/许可 | 41 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/airbnb/DESIGN.md` | 说明/设计参考 | 30517 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/airbnb/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/airtable/DESIGN.md` | 说明/设计参考 | 35266 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/airtable/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/apple/DESIGN.md` | 说明/设计参考 | 37096 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/apple/README.md` | 说明/设计参考 | 207 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/binance/DESIGN.md` | 说明/设计参考 | 39918 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/binance/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/bmw/DESIGN.md` | 说明/设计参考 | 27907 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/bmw/README.md` | 说明/设计参考 | 203 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/bmw-m/DESIGN.md` | 说明/设计参考 | 30697 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/bmw-m/README.md` | 说明/设计参考 | 207 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/bugatti/DESIGN.md` | 说明/设计参考 | 28535 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/bugatti/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/cal/DESIGN.md` | 说明/设计参考 | 31176 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/cal/README.md` | 说明/设计参考 | 203 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/claude/DESIGN.md` | 说明/设计参考 | 33586 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/claude/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/clay/DESIGN.md` | 说明/设计参考 | 25705 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/clay/README.md` | 说明/设计参考 | 205 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/clickhouse/DESIGN.md` | 说明/设计参考 | 25986 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/clickhouse/README.md` | 说明/设计参考 | 217 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/cohere/DESIGN.md` | 说明/设计参考 | 20020 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/cohere/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/coinbase/DESIGN.md` | 说明/设计参考 | 25853 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/coinbase/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/composio/DESIGN.md` | 说明/设计参考 | 20606 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/composio/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/cursor/DESIGN.md` | 说明/设计参考 | 21771 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/cursor/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/dell-1996/DESIGN.md` | 说明/设计参考 | 34592 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/dell-1996/README.md` | 说明/设计参考 | 217 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/elevenlabs/DESIGN.md` | 说明/设计参考 | 20943 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/elevenlabs/README.md` | 说明/设计参考 | 217 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/expo/DESIGN.md` | 说明/设计参考 | 21660 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/expo/README.md` | 说明/设计参考 | 205 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/ferrari/DESIGN.md` | 说明/设计参考 | 24365 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/ferrari/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/figma/DESIGN.md` | 说明/设计参考 | 32316 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/figma/README.md` | 说明/设计参考 | 207 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/framer/DESIGN.md` | 说明/设计参考 | 29119 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/framer/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/hashicorp/DESIGN.md` | 说明/设计参考 | 28023 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/hashicorp/README.md` | 说明/设计参考 | 215 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/hp/DESIGN.md` | 说明/设计参考 | 36335 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/hp/README.md` | 说明/设计参考 | 201 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/ibm/DESIGN.md` | 说明/设计参考 | 26481 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/ibm/README.md` | 说明/设计参考 | 203 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/intercom/DESIGN.md` | 说明/设计参考 | 23278 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/intercom/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/kraken/DESIGN.md` | 说明/设计参考 | 4350 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/kraken/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/lamborghini/DESIGN.md` | 说明/设计参考 | 21119 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/lamborghini/README.md` | 说明/设计参考 | 219 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/linear.app/DESIGN.md` | 说明/设计参考 | 24354 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/linear.app/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/lovable/DESIGN.md` | 说明/设计参考 | 17384 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/lovable/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/mastercard/DESIGN.md` | 说明/设计参考 | 26995 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/mastercard/README.md` | 说明/设计参考 | 217 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/meta/DESIGN.md` | 说明/设计参考 | 37986 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/meta/README.md` | 说明/设计参考 | 205 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/minimax/DESIGN.md` | 说明/设计参考 | 37920 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/minimax/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/mintlify/DESIGN.md` | 说明/设计参考 | 44083 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/mintlify/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/miro/DESIGN.md` | 说明/设计参考 | 36542 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/miro/README.md` | 说明/设计参考 | 205 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/mistral.ai/DESIGN.md` | 说明/设计参考 | 35508 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/mistral.ai/README.md` | 说明/设计参考 | 217 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/mongodb/DESIGN.md` | 说明/设计参考 | 32077 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/mongodb/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/nike/DESIGN.md` | 说明/设计参考 | 36697 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/nike/README.md` | 说明/设计参考 | 205 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/nintendo-2001/DESIGN.md` | 说明/设计参考 | 38977 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/nintendo-2001/README.md` | 说明/设计参考 | 229 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/notion/DESIGN.md` | 说明/设计参考 | 35176 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/notion/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/nvidia/DESIGN.md` | 说明/设计参考 | 35591 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/nvidia/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/ollama/DESIGN.md` | 说明/设计参考 | 32747 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/ollama/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/opencode.ai/DESIGN.md` | 说明/设计参考 | 32647 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/opencode.ai/README.md` | 说明/设计参考 | 219 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/pinterest/DESIGN.md` | 说明/设计参考 | 36392 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/pinterest/README.md` | 说明/设计参考 | 215 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/playstation/DESIGN.md` | 说明/设计参考 | 39766 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/playstation/README.md` | 说明/设计参考 | 219 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/posthog/DESIGN.md` | 说明/设计参考 | 40498 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/posthog/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/raycast/DESIGN.md` | 说明/设计参考 | 41275 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/raycast/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/renault/DESIGN.md` | 说明/设计参考 | 30076 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/renault/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/replicate/DESIGN.md` | 说明/设计参考 | 31495 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/replicate/README.md` | 说明/设计参考 | 215 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/resend/DESIGN.md` | 说明/设计参考 | 31461 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/resend/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/revolut/DESIGN.md` | 说明/设计参考 | 32034 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/revolut/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/runwayml/DESIGN.md` | 说明/设计参考 | 14353 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/runwayml/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/sanity/DESIGN.md` | 说明/设计参考 | 21231 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/sanity/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/sentry/DESIGN.md` | 说明/设计参考 | 35444 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/sentry/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/shopify/DESIGN.md` | 说明/设计参考 | 27067 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/shopify/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/slack/DESIGN.md` | 说明/设计参考 | 24529 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/spacex/DESIGN.md` | 说明/设计参考 | 19679 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/spacex/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/spotify/DESIGN.md` | 说明/设计参考 | 12955 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/spotify/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/starbucks/DESIGN.md` | 说明/设计参考 | 37329 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/starbucks/README.md` | 说明/设计参考 | 215 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/stripe/DESIGN.md` | 说明/设计参考 | 24606 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/stripe/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/supabase/DESIGN.md` | 说明/设计参考 | 21315 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/supabase/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/superhuman/DESIGN.md` | 说明/设计参考 | 21877 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/superhuman/README.md` | 说明/设计参考 | 217 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/tesla/DESIGN.md` | 说明/设计参考 | 22212 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/tesla/README.md` | 说明/设计参考 | 207 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/theverge/DESIGN.md` | 说明/设计参考 | 28368 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/theverge/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/together.ai/DESIGN.md` | 说明/设计参考 | 38343 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/together.ai/README.md` | 说明/设计参考 | 219 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/uber/DESIGN.md` | 说明/设计参考 | 34760 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/uber/README.md` | 说明/设计参考 | 205 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/vercel/DESIGN.md` | 说明/设计参考 | 41405 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/vercel/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/vodafone/DESIGN.md` | 说明/设计参考 | 28106 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/vodafone/README.md` | 说明/设计参考 | 213 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/voltagent/DESIGN.md` | 说明/设计参考 | 25915 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/voltagent/README.md` | 说明/设计参考 | 215 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/warp/DESIGN.md` | 说明/设计参考 | 24438 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/warp/README.md` | 说明/设计参考 | 205 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/webflow/DESIGN.md` | 说明/设计参考 | 28179 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/webflow/README.md` | 说明/设计参考 | 211 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/wired/DESIGN.md` | 说明/设计参考 | 23661 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/wired/README.md` | 说明/设计参考 | 207 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/wise/DESIGN.md` | 说明/设计参考 | 24586 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/wise/README.md` | 说明/设计参考 | 205 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/x.ai/DESIGN.md` | 说明/设计参考 | 21781 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/x.ai/README.md` | 说明/设计参考 | 204 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/zapier/DESIGN.md` | 说明/设计参考 | 22995 | 0 | 静态检查通过 |
| `awesome-design-md/design-md/zapier/README.md` | 说明/设计参考 | 209 | 0 | 静态检查通过 |
| `personal-homepage-skill/.gitignore` | 说明/设计参考 | 76 | 0 | 静态检查通过 |
| `personal-homepage-skill/CINEMATIC_SCROLL_TEMPLATE.md` | 说明/设计参考 | 5265 | 0 | 静态检查通过 |
| `personal-homepage-skill/COMPONENT_PATTERNS.md` | 说明/设计参考 | 8027 | 2 | 静态检查通过 |
| `personal-homepage-skill/CONTRIBUTING.md` | 说明/设计参考 | 3704 | 0 | 静态检查通过 |
| `personal-homepage-skill/DATA_SCHEMA.md` | 说明/设计参考 | 4297 | 0 | 静态检查通过 |
| `personal-homepage-skill/DEMO_SCRIPT.md` | 说明/设计参考 | 3405 | 0 | 静态检查通过 |
| `personal-homepage-skill/DESIGN_REVIEW.md` | 说明/设计参考 | 13097 | 0 | 静态检查通过 |
| `personal-homepage-skill/HOMEPAGE_GENERATION_WORKFLOW.md` | 说明/设计参考 | 4687 | 0 | 静态检查通过 |
| `personal-homepage-skill/HOMEPAGE_SECTIONS.md` | 说明/设计参考 | 4755 | 0 | 静态检查通过 |
| `personal-homepage-skill/IMAGE_WORKFLOW.md` | 说明/设计参考 | 1801 | 0 | 静态检查通过 |
| `personal-homepage-skill/LICENSE` | 来源/许可 | 3011 | 0 | 静态检查通过 |
| `personal-homepage-skill/MOTION_PATTERNS.md` | 说明/设计参考 | 6528 | 0 | 静态检查通过 |
| `personal-homepage-skill/OPEN_SOURCE_CHECKLIST.md` | 说明/设计参考 | 4342 | 0 | 静态检查通过 |
| `personal-homepage-skill/OPEN_SOURCE_PRD.md` | 说明/设计参考 | 8385 | 0 | 静态检查通过 |
| `personal-homepage-skill/PPT_VISUAL_QA.md` | 说明/设计参考 | 4662 | 0 | 静态检查通过 |
| `personal-homepage-skill/PRD.md` | 说明/设计参考 | 8350 | 0 | 静态检查通过 |
| `personal-homepage-skill/PRESENTATION_WORKFLOW.md` | 说明/设计参考 | 15248 | 1 | 静态检查通过 |
| `personal-homepage-skill/README.md` | 说明/设计参考 | 12023 | 52 | 静态检查通过 |
| `personal-homepage-skill/REFERENCE_PRODUCTS.md` | 说明/设计参考 | 12041 | 5 | 静态检查通过 |
| `personal-homepage-skill/SKILL.md` | 说明/设计参考 | 20260 | 14 | 静态检查通过 |
| `personal-homepage-skill/SOURCE.md` | 来源/许可 | 602 | 0 | 静态检查通过 |
| `personal-homepage-skill/STYLE_PRESETS.md` | 说明/设计参考 | 18134 | 1 | 静态检查通过 |
| `personal-homepage-skill/TASK_BREAKDOWN.md` | 说明/设计参考 | 4920 | 2 | 静态检查通过 |
| `personal-homepage-skill/TECHNICAL_ROUTE.md` | 说明/设计参考 | 7343 | 3 | 静态检查通过 |
| `personal-homepage-skill/TEST_SCENARIOS.md` | 说明/设计参考 | 7856 | 0 | 静态检查通过 |
| `personal-homepage-skill/UPSTREAM_COMMIT` | 来源/许可 | 41 | 0 | 静态检查通过 |
| `personal-homepage-skill/USER_STORIES.md` | 说明/设计参考 | 6714 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/demo-cinematic-scroll-personal-brand.gif` | 媒体/预览 | 1598427 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/demo-hero-neural-homepage.png` | 媒体/预览 | 185832 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/demo-orbis-nft-space-landing.gif` | 媒体/预览 | 4121874 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/demo-toonhub-figurine-carousel.gif` | 媒体/预览 | 4177140 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/3d-tech-portfolio.svg` | 媒体/预览 | 1644 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/ai-system-dashboard.svg` | 媒体/预览 | 1675 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/art-museum-portfolio.svg` | 媒体/预览 | 1624 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/business-personal-brand.svg` | 媒体/预览 | 1533 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/case-study-portfolio.svg` | 媒体/预览 | 1563 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/cinematic-scroll-personal-brand.svg` | 媒体/预览 | 1609 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/clean-developer-homepage.svg` | 媒体/预览 | 1654 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/creator-bento-homepage.svg` | 媒体/预览 | 1519 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/cute-pixel-creator.svg` | 媒体/预览 | 1650 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/dark-editorial-portfolio.svg` | 媒体/预览 | 1628 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/magazine-portfolio.svg` | 媒体/预览 | 1539 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/minimal-premium-resume.svg` | 媒体/预览 | 1605 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/motion-gradient-brand.svg` | 媒体/预览 | 1555 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/orbis-nft-space-landing.svg` | 媒体/预览 | 5308 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/soft-product-video-hero.svg` | 媒体/预览 | 1658 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/spatial-project-gallery.svg` | 媒体/预览 | 1566 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/terminal-hacker-homepage.svg` | 媒体/预览 | 1645 | 0 | 静态检查通过 |
| `personal-homepage-skill/assets/template-previews/toonhub-figurine-carousel.svg` | 媒体/预览 | 1584 | 0 | 静态检查通过 |
| `personal-homepage-skill/demo/personal-homepage-skill-overview.html` | 模板源码/页面 | 36457 | 0 | 静态检查通过 |
| `personal-homepage-skill/demo/template-gallery.html` | 模板源码/页面 | 51115 | 0 | 静态检查通过 |
| `personal-homepage-skill/examples/PROMPTS.md` | 说明/设计参考 | 7281 | 0 | 静态检查通过 |
| `personal-homepage-skill/index.html` | 模板源码/页面 | 321 | 1 | 静态检查通过 |
| `personal-homepage-skill/package-lock.json` | 配置/依赖锁 | 94590 | 0 | 静态检查通过 |
| `personal-homepage-skill/package.json` | 配置/依赖锁 | 1780 | 0 | 静态检查通过 |
| `personal-homepage-skill/postcss.config.js` | 模板源码/页面 | 81 | 0 | 静态检查通过 |
| `personal-homepage-skill/scripts/build-hero-portable.mjs` | 脚本/测试入口 | 4768 | 0 | 静态检查通过 |
| `personal-homepage-skill/scripts/capture-slides.mjs` | 脚本/测试入口 | 10221 | 0 | 静态检查通过 |
| `personal-homepage-skill/scripts/check-spec.mjs` | 脚本/测试入口 | 6094 | 0 | 静态检查通过 |
| `personal-homepage-skill/scripts/check-templates.mjs` | 脚本/测试入口 | 2466 | 0 | 静态检查通过 |
| `personal-homepage-skill/scripts/check-visual.mjs` | 脚本/测试入口 | 2127 | 0 | 静态检查通过 |
| `personal-homepage-skill/scripts/test-export-html.mjs` | 脚本/测试入口 | 2879 | 0 | 静态检查通过 |
| `personal-homepage-skill/scripts/verify-html-ppt-stage.mjs` | 脚本/测试入口 | 24279 | 0 | 静态检查通过 |
| `personal-homepage-skill/src/App.tsx` | 模板源码/页面 | 1069 | 4 | 静态检查通过 |
| `personal-homepage-skill/src/components/GalleryHeader.tsx` | 模板源码/页面 | 2086 | 1 | 静态检查通过 |
| `personal-homepage-skill/src/components/PreviewCanvas.tsx` | 模板源码/页面 | 549 | 5 | 静态检查通过 |
| `personal-homepage-skill/src/components/TemplateCard.tsx` | 模板源码/页面 | 2319 | 2 | 静态检查通过 |
| `personal-homepage-skill/src/components/TemplateFilters.tsx` | 模板源码/页面 | 1108 | 1 | 静态检查通过 |
| `personal-homepage-skill/src/components/TemplateGrid.tsx` | 模板源码/页面 | 705 | 2 | 静态检查通过 |
| `personal-homepage-skill/src/data/profile-schema.ts` | 模板源码/页面 | 1607 | 0 | 静态检查通过 |
| `personal-homepage-skill/src/data/templates.ts` | 模板源码/页面 | 26610 | 0 | 静态检查通过 |
| `personal-homepage-skill/src/index.css` | 模板源码/页面 | 4694 | 0 | 静态检查通过 |
| `personal-homepage-skill/src/main.tsx` | 模板源码/页面 | 237 | 2 | 静态检查通过 |
| `personal-homepage-skill/src/previews/art.tsx` | 模板源码/页面 | 3275 | 2 | 静态检查通过 |
| `personal-homepage-skill/src/previews/business.tsx` | 模板源码/页面 | 2815 | 2 | 静态检查通过 |
| `personal-homepage-skill/src/previews/creator.tsx` | 模板源码/页面 | 7481 | 2 | 静态检查通过 |
| `personal-homepage-skill/src/previews/previewData.ts` | 模板源码/页面 | 279 | 0 | 静态检查通过 |
| `personal-homepage-skill/src/previews/tech.tsx` | 模板源码/页面 | 7249 | 3 | 静态检查通过 |
| `personal-homepage-skill/tailwind.config.js` | 模板源码/页面 | 515 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/App.tsx` | 模板源码/页面 | 1641 | 8 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/Architecture.tsx` | 模板源码/页面 | 2074 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/BackgroundMedia.tsx` | 模板源码/页面 | 2698 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/CinematicText.tsx` | 模板源码/页面 | 1896 | 2 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/Footer.tsx` | 模板源码/页面 | 2527 | 5 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/Hero.tsx` | 模板源码/页面 | 5931 | 4 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/InlineEditor.tsx` | 模板源码/页面 | 3798 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/Metrics.tsx` | 模板源码/页面 | 1843 | 2 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/Navbar.tsx` | 模板源码/页面 | 6391 | 4 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/README.md` | 说明/设计参考 | 11333 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/ScrambleIn.tsx` | 模板源码/页面 | 1815 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/ScrambleText.tsx` | 模板源码/页面 | 1538 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/SocialLinks.tsx` | 模板源码/页面 | 5516 | 1 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/SquashHamburger.tsx` | 模板源码/页面 | 1146 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/SynapseXLogo.tsx` | 模板源码/页面 | 824 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/Technology.tsx` | 模板源码/页面 | 2820 | 2 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/assets/README.md` | 说明/设计参考 | 1218 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/assets/images/portrait.jpg` | 媒体/预览 | 338578 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/assets/videos/cinematic-text.mp4` | 媒体/预览 | 5121950 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/assets/videos/footer.mp4` | 媒体/预览 | 1077148 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/assets/videos/hero.mp4` | 媒体/预览 | 3363487 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/assets/videos/metrics.mp4` | 媒体/预览 | 2853260 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/assets/videos/technology.mp4` | 媒体/预览 | 16856749 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/content.ts` | 模板源码/页面 | 345 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/index.css` | 模板源码/页面 | 4083 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/assets/hero.css` | 便携产物/资源 | 39844 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/assets/hero.js` | 便携产物/资源 | 332686 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/assets/images/portrait.jpg` | 便携产物/资源 | 338578 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/assets/videos/cinematic-text.mp4` | 便携产物/资源 | 5121950 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/assets/videos/footer.mp4` | 便携产物/资源 | 1077148 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/assets/videos/hero.mp4` | 便携产物/资源 | 3363487 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/assets/videos/metrics.mp4` | 便携产物/资源 | 2853260 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/assets/videos/technology.mp4` | 便携产物/资源 | 16856749 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/index.html` | 便携产物/资源 | 769 | 2 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/portable/使用说明.txt` | 便携产物/资源 | 536 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/preview.html` | 模板源码/页面 | 727 | 1 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/preview.tsx` | 模板源码/页面 | 232 | 2 | 静态检查通过 |
| `personal-homepage-skill/templates/hero/videos.ts` | 模板源码/页面 | 1292 | 6 | 静态检查通过 |
| `personal-homepage-skill/templates/orbis-nft/README.md` | 说明/设计参考 | 7705 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/presentation-html/README.md` | 说明/设计参考 | 1256 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/presentation-html/presentation.html` | 模板源码/页面 | 10473 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/react-tailwind/App.tsx` | 模板源码/页面 | 2739 | 1 | 静态检查通过 |
| `personal-homepage-skill/templates/react-tailwind/README.md` | 说明/设计参考 | 389 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/react-tailwind/index.css` | 模板源码/页面 | 866 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/react-tailwind/profile.ts` | 模板源码/页面 | 630 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/single-html/README.md` | 说明/设计参考 | 375 | 0 | 静态检查通过 |
| `personal-homepage-skill/templates/single-html/personal-homepage.html` | 模板源码/页面 | 9163 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/capture-slides.test.mjs` | 脚本/测试入口 | 4992 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/fixtures/broken-image.html` | 测试夹具 | 1082 | 1 | 负向夹具：./does-not-exist.png |
| `personal-homepage-skill/tests/fixtures/capture-edge-cases.html` | 测试夹具 | 3063 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/fixtures/duplicate-slide-id.html` | 测试夹具 | 1546 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/fixtures/missing-shortcuts.html` | 测试夹具 | 1413 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/fixtures/transform-conflict.html` | 测试夹具 | 1268 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/fixtures/valid-deck.html` | 测试夹具 | 3925 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/fixtures/verifier-edge-cases.html` | 测试夹具 | 6222 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/hero-portable.test.mjs` | 脚本/测试入口 | 5955 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/hero-template.test.mjs` | 脚本/测试入口 | 6004 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/homepage-qa-rules.test.mjs` | 脚本/测试入口 | 1998 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/homepage-regression.test.mjs` | 脚本/测试入口 | 2263 | 0 | 静态检查通过 |
| `personal-homepage-skill/tests/verify-html-ppt-stage.test.mjs` | 脚本/测试入口 | 5308 | 0 | 静态检查通过 |
| `personal-homepage-skill/tsconfig.json` | 配置/依赖锁 | 565 | 0 | 静态检查通过 |
| `personal-homepage-skill/vite.config.ts` | 模板源码/页面 | 353 | 2 | 静态检查通过 |
