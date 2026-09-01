# DESIGN.md Contract

`DESIGN.md` 是项目级视觉契约；`AGENTS.md` 定义开发方式，`DESIGN.md` 定义界面应该如何呈现。

## 适用边界

需要建立或更新 `DESIGN.md`：

- 新建有持续维护价值的前端项目、网站、产品界面、dashboard 或品牌页面。
- 大幅视觉重构、设计系统收敛、模板参考迁移或多人/多代理并行实现。
- 用户要求“像某个品牌/模板/参考站”，或需要长期保持 UI 一致性。

不强制建立完整 `DESIGN.md`：

- 一次性小修、小组件补丁、无视觉系统变化的功能实现。
- 已有项目设计系统清晰且本次不改变视觉规则。

## 统一模板接管

- 模板来源由用户统一模板体系接管；本规范只定义读取、抽取、落地和验收规则。
- 从统一模板入口选择一个主参考，最多一个辅助参考；不要在本 skill 内维护平行模板索引。
- 先读取统一模板返回的 `DESIGN.md`、preview、源码说明或 license，再抽取 token、组件状态、布局节奏和反模式。
- 若统一模板入口不可发现，先用当前可用工具或 skill 搜索模板能力；仍不可发现时，只问一个精准问题索取模板 ID、路径或链接，不自建索引、不猜测来源。
- 模板是输入参考；完成适配后，项目 `DESIGN.md` 是唯一视觉真源，上游模板变化不得自动覆盖本地决策。
- 只能借用设计语言，不得复制品牌文案、logo、素材、商标、专有字体文件或完整页面结构。
- 参考品牌只作为设计坐标；交付必须回到用户自己的业务、内容、组件和资产。
- 每次使用统一模板或外部参考，必须记录 source、license、borrowed patterns 和 excluded assets。

## 机器可读契约

完整 `DESIGN.md` 必须使用 YAML frontmatter 保存来源、版本、语义 token 和组件状态。示例：

```yaml
---
design_system: project-design
version: 1
source_templates:
  - name: vercel
    source: unified-template:vercel
    upstream: https://getdesign.md/vercel/design-md
    license: template license recorded; brand assets excluded
borrowed_patterns:
  - monochrome precision
  - tight technical typography
excluded_assets:
  - logos
  - proprietary copy
  - product screenshots
tokens:
  color:
    canvas: "#0a0a0a"
    surface: "#141414"
    text-primary: "#fafafa"
    text-muted: "#a1a1aa"
    accent: "#5eead4"
    border: "#2a2a2a"
    focus: "#67e8f9"
  typography:
    display: "Inter, system-ui, sans-serif"
    body: "Inter, system-ui, sans-serif"
    label: "Inter, system-ui, sans-serif"
    code-data: "ui-monospace, monospace"
  spacing:
    unit: "4px"
    component-gap: "12px"
    section-gap: "80px"
  radius:
    control: "6px"
    panel: "8px"
  motion:
    fast: "120ms"
    standard: "180ms"
    easing-standard: "cubic-bezier(0.2, 0, 0, 1)"
component_states:
  button: [default, hover, pressed, disabled, focus-visible]
  input: [default, hover, focus, error, disabled]
  panel: [default, hover, selected, featured]
  navigation: [default, active, hover, mobile-collapsed]
---
```

- `version` 是项目视觉契约版本；已接受的 token 或组件状态发生变化时递增。
- 最终文件不得保留 `<value>`、`TODO` 或未解析字段；不适用的可选列表可以为空。
- 业务说明可以写在正文；实现依赖的 token 与状态必须留在 frontmatter 中，保持可解析。

## 必备章节

```md
# DESIGN.md

## Visual Direction
## Source References
## Color Tokens
## Typography
## Spacing And Layout
## Components
## Motion
## Imagery And Assets
## Responsive Rules
## Do / Avoid
## Verification
```

## Token 要求

- Token 必须语义化：`canvas`、`surface`、`text-primary`、`text-muted`、`accent`、`border`、`focus`。
- 同一组件必须引用 token，不在实现里散落未命名 hex、字号、圆角和阴影。
- Typography 至少定义 display、body、label、code / data；中文项目必须定义 CJK 字体栈。
- Spacing 至少定义基础步进、section 间距、组件 padding、grid gap 和移动端折叠规则。
- Radius、border、shadow、elevation 必须有使用边界；不要把一种圆角或阴影套满全站。

## 组件状态

组件规则必须写到状态，而不是只写静态样式：

- button：default、hover、pressed、disabled、focus。
- input / select：default、hover、focus、error、disabled。
- card / panel：default、hover、selected、featured。
- navigation：default、active、hover、mobile collapsed。
- table / chart / code：density、border、highlight、empty、loading。
- modal / popover / toast：surface、backdrop、motion、focus trap、dismiss。

## 设计到实现

- 实现前先产出 token plan：哪些 token 会映射到 CSS variables、Tailwind theme、component variants 或 design-system constants。
- 多代理并行时，先冻结 `DESIGN.md` 的 token 和组件状态，再拆分页面或组件实现。
- 新组件优先接入既有 token 和组件语法；不得为局部方便创建相近但不兼容的视觉规则。
- 修改视觉系统时，先更新并递增 `DESIGN.md` 版本，再同步实现 token、组件状态和必要的视觉测试；不得只改其中一侧。

## 验收

- 与参考模板比对：保留了哪些设计语言，舍弃了哪些品牌资产。
- 契约检查：frontmatter 可解析、无占位符，token 和组件状态均能映射到实现。
- 渲染检查：桌面、移动、横向溢出、文本重叠、资源加载、交互状态。
- 移动端检查：触控目标、safe area、软键盘遮挡以及 hover 的触控替代路径。
- 可访问性检查：语义结构、文本对比度、focus-visible、键盘路径、label / alt 和 reduced-motion。
- 性能检查：媒体尺寸与格式、字体加载、布局偏移，以及动效是否引发高频 layout / paint。
- Token 检查：实现是否使用命名 token，组件状态是否覆盖。
- 动效检查：关键动效是否有 Motion Contract、reduced-motion 和 hover/touch 分支。
- 必要时运行 `npx @google/design.md lint DESIGN.md`；该工具是可选验证，不作为全局依赖。

## 来源边界

- 高层工作流参考 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) 与 Google Stitch `DESIGN.md` 思路。
- `awesome-design-md` 采用 MIT License，但品牌名称、商标、logo、素材和视觉身份仍属于对应权利方。
- 本规范不维护独立模板索引；模板入口由统一模板体系接管。
