# Refero Substyle Recipes

Use this file when the top-level style family is correct, but the user wants a more specific feel.

Common triggers:

- "安静一点"
- "不要太营销"
- "像高频工作台"
- "技术味更重"
- "有 AI 发布感，但别太虚"

## Fast Mapping

| User cue | Primary family | Recommended substyle |
| --- | --- | --- |
| 安静、克制、SaaS、专业 | `clean-saas` | `quiet-saas` |
| 工作台、扫描、信息密度、实用 | `dashboard-workbench` or `devtool` | `technical-workbench` |
| 前沿、AI、新品发布、未来感 | `ai-startup` or `dark-mode` | `frontier-ai-launch` |

If a request already includes a strong family signal, keep that family and only swap in the substyle.

## quiet-saas

**Use when**

- the user wants SaaS clarity without template-like marketing noise
- the product is mature enough to signal trust, not hype
- the page should feel calm, literate, and polished

**Good fits**

- B2B SaaS landing pages
- feature pages
- docs-home hybrids
- founder-led software brands that still need conversion clarity

**Visual signals**

- warm-light or soft neutral surfaces
- restrained accent color, often blue, teal, or ink-like contrast
- calm typography with slightly more editorial rhythm than generic SaaS
- visible screenshots and proof, but not overloaded badge walls

**Avoid**

- loud gradient hero treatments
- oversized shouty headlines
- card spam without a clear narrative

**Prompt fragments**

- "Use a quiet SaaS direction: calm hierarchy, visible proof, restrained accents, and a more authored rhythm than a generic template."
- "The page should feel trustworthy and thoughtful, not hype-driven."

**DESIGN.md deltas**

- Typography: slightly more composed headline rhythm, body text tuned for long-form scanning
- Layout: generous but not airy section spacing, strong left alignment
- Components: crisp buttons, subtle cards, quiet borders

## technical-workbench

**Use when**

- the product is used repeatedly during work
- the user wants a workbench, cockpit, console, or analyst-tool feel
- density and scanability matter more than storytelling

**Good fits**

- internal tools
- dashboards
- devtools
- operations and analyst interfaces
- API or infrastructure products with real proof surfaces

**Visual signals**

- stable layout with strong panes, tables, filters, and status regions
- narrow radius, explicit dividers, predictable controls
- charts, logs, tables, or code blocks that look operational
- restrained palette with one accent channel

**Avoid**

- marketing hero composition
- fluffy decorative illustrations
- soft card-heavy layouts that hide actions and data

**Prompt fragments**

- "Design this as a technical workbench: dense, operational, predictable, and easy to scan all day."
- "Prioritize filters, tables, logs, screenshots, and workflow proof over decorative storytelling."

**DESIGN.md deltas**

- Layout: clear tool regions, stronger grids, compact spacing
- Components: high-utility tables, tabs, segmented controls, filter bars
- Motion: restrained, mostly feedback-oriented

## frontier-ai-launch

**Use when**

- the product needs clear AI-forward energy
- the page is a launch, announcement, or flagship surface
- novelty matters, but the workflow still has to be legible

**Good fits**

- AI startup launches
- research-to-product announcements
- agent products
- new product reveal pages

**Visual signals**

- one strong accent family over dark or controlled soft-light surfaces
- a visible product loop in the first viewport
- product UI, use-case bands, and capability framing that feel current
- faster visual energy than quiet SaaS, but still disciplined

**Avoid**

- generic space gradients with no product meaning
- pure vibe pages that hide the actual workflow
- too many accent colors competing at once

**Prompt fragments**

- "Use frontier AI launch energy, but make the product loop and use cases obvious in the first viewport."
- "Show novelty through interface detail and workflow framing, not just through atmospheric gradients."

**DESIGN.md deltas**

- Visual direction: fast, sharp, current
- Imagery: product UI, agent loops, use-case panels, selective diagrams
- Motion: slightly more energetic transitions, still restrained

## Quick Call Examples

```text
用 refero-design-prompts 给我一个 quiet-saas 风格的 B2B SaaS 首页，输出 prompt + DESIGN.md
```

```text
把这个 dashboard 走 technical-workbench 路线，别做成营销页
```

```text
给这个 AI 产品发布页走 frontier-ai-launch，保留产品流程清晰度
```
