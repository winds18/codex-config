# Motion Craft Workflow

用于把模糊动效要求转为可实现、可审查、可复用的组件运动规范。

## 适用场景

- 用户要求动画、转场、微交互、动效优化、组件质感、丝滑感、高级感或交互反馈。
- 页面或组件已有动效，但需要判断是否过度、迟缓、掉帧、不自然或不可访问。
- 设计提示词需要明确 motion 语言，避免只写“更顺滑”“更高级”。

## Motion Brief

实现前必须先收敛术语和状态：

- `term`：准确动效术语，如 scale in、origin-aware animation、stagger、shared element transition、rubber-banding。
- `trigger`：触发方式，如 click、hover、focus、route change、drag、scroll、data update。
- `frequency`：用户看到频率。
- `purpose`：feedback、spatial consistency、state indication、preventing jarring change、explanation 或 rare delight。
- `states`：起始状态、结束状态、退出状态。
- `surface`：按钮、菜单、popover、drawer、toast、列表、图表、页面转场、Hero 或展示型媒体。
- `constraints`：性能预算、移动端、reduced motion、浏览器兼容和既有 design token。

术语不清时，先用 animation-vocabulary 的术语表归一化；不能命名目的时，不进入实现。

## Motion Gate

按顺序判断，前两项不通过就停止写动效代码：

1. Frequency Budget
   - 100+ 次/天、键盘快捷键、命令面板、核心导航：默认不做动画。
   - 数十次/天的 hover、列表导航、频繁 toggle：只允许近乎无感的短反馈。
   - 偶发的 modal、drawer、toast、popover：允许标准 UI 动效。
   - 首次引导、空状态、成功反馈和展示型解释：允许少量 delight。
2. Purpose Gate
   - 必须服务 feedback、spatial consistency、state indication、preventing jarring change 或 explanation。
   - “看起来更酷”不是高频 UI 动效理由。
3. Tool Gate
   - 复用既有 motion token、duration scale 和 easing token。
   - CSS transition / `@starting-style` 适合确定性进入退出。
   - WAAPI 适合需要 JS 控制但仍希望走浏览器动画管线的场景。
   - Spring 适合 gesture、drag、interruptible motion。
   - 不为 fade、hover 或简单 reveal 新增 motion library。
4. Property Gate
   - 默认只动画 `transform` 与 `opacity`。
   - reveal 可用 `clip-path` 或 mask，但要验证性能和浏览器表现。
   - accordion / collapse 可动画高度，但必须限制作用域、避免布局抖动并做渲染验证。
5. Timing Gate
   - Button press feedback：100-160ms。
   - Tooltip / small popover：125-200ms。
   - Dropdown / select：150-250ms。
   - Modal / drawer：200-500ms，超过 300ms 必须有理由。
   - Group stagger：30-80ms，不能阻塞交互。
6. Easing Gate
   - 进入、退出和用户反馈：ease-out 或既有强 ease-out token。
   - 屏幕内移动、morph、布局迁移：ease-in-out 或对应 token。
   - hover / color：ease。
   - marquee、spinner、进度循环：linear。
   - UI 交互禁用 `ease-in` 作为默认曲线。

## Component Motion Contract

新增或调整关键动效的组件必须能回答：

- 动效是否真的需要存在；若不需要，使用即时状态、静态 affordance 或更清晰的信息架构。
- 该动效属于进入退出、状态迁移、空间连续、反馈、手势、滚动、展示解释还是环境氛围。
- 触发源、目标元素、退出路径和 `transform-origin` 是否一致；trigger-anchored popover/dropdown/tooltip 不从中心点缩放。
- 是否避免 `transition: all`、`scale(0)`、无边界 keyframes、布局属性滥用和父级 CSS 变量驱动子级 transform。
- 快速重复触发时是否可 interruptible；toast、toggle、drag、list enter/exit 优先使用可重定向 transition 或 spring。
- hover 动效是否只在 `@media (hover: hover) and (pointer: fine)` 下启用。
- `prefers-reduced-motion` 是否提供温和替代：保留必要 opacity / color 反馈，移除位置和大幅 transform。
- 移动端是否降低 parallax、3D、粒子、视频 scrub 和持续背景动画。

## Review Animations

审查已有动效时，先列问题，再给结论。每个问题必须包含：

| Before | After | Why |
| --- | --- | --- |
| 当前实现或症状 | 建议改法 | 目的、性能、可访问性或一致性原因 |

默认阻断项：

- 无目的或高频 UI 动画。
- `transition: all`。
- `scale(0)`，或关键弹层、菜单、toast 使用缺少空间线索的纯 fade。
- UI 交互使用 `ease-in`。
- 无理由超过 300ms 的 UI 动效。
- trigger-anchored surface 使用错误 `transform-origin`。
- 高频触发元素使用会重启的 keyframes。
- 动画 `width`、`height`、`margin`、`padding`、`top`、`left` 等布局属性且无验证理由。
- 缺少 `prefers-reduced-motion` 或 hover gating。

审查结论只允许：

- `Block`：存在体感、性能、可访问性或高频噪音问题。
- `Approve`：目的明确，频率合适，时长和曲线受控，可中断、可降级，并通过渲染验证。

## Verification

- 用真实浏览器检查桌面和移动视口。
- 对关键动效检查 computed style：`transform`、`opacity`、`transition-*`、`animation-*`、`transform-origin`、`will-change`、`overflow`。
- 使用 DevTools animation inspector、慢放 2-5 倍或逐帧检查来判断节奏、同步和 origin。
- gesture、drag、swipe、drawer、mobile sheet 必须在真实触控路径或等效设备模拟中验证。
- 检查 reduced motion、hover gating、键盘操作、焦点状态和快速重复触发。
- 只在性能收益明确时使用 `will-change`，并避免长期滞留导致图层成本。

## 来源边界

- 高层流程参考 [emilkowalski/skills](https://github.com/emilkowalski/skills) 中 `animation-vocabulary`、`emil-design-eng`、`review-animations`、`animate` 和 `find-animation-opportunities` 的公开设计工程思想。
- 原仓库采用 MIT License。本文件是中文工程化抽象；若直接复用外部代码、文本、配置或示例，必须保留许可与署名要求。
