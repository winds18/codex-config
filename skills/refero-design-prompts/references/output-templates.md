# Output Templates

Use these templates to keep responses consistent across design requests.

## Preferred Response Shape

```md
结论
- 主风格：
- 备选风格：
- 适配原因：

风格判断
- 目标受众：
- 主要信号：
- 信息密度：
- 必须出现的产品证据：
- 要避免的误区：

Build Prompt
```text
[tool-specific prompt]
```

DESIGN.md
```md
# DESIGN.md
## Visual Direction
## Color System
## Typography
## Layout
## Components
## Imagery
## Motion
## Avoid
```

验证清单
- [ ] ...
- [ ] ...
```

## Prompt Skeleton

Fill the blanks, then trim any section that does not help the task.

```text
Design a [surface] for [product / company].

User-facing outcome:
- Help the user [primary task or impression].

Primary style direction:
- [style family]

Backup style direction:
- [backup style family]

Audience and trust signal:
- [who it is for]
- [what should make it feel credible]

Visual system:
- Color: [palette direction]
- Contrast: [high / medium / calm]
- Typography: [tone and hierarchy]
- Spacing: [dense / balanced / airy]
- Radius and borders: [tight / soft / crisp]
- Imagery: [screenshots / diagrams / product photos / none]
- Motion: [quiet / guided / energetic]

Motion Contract, only when motion matters:
- Term: [exact motion term when motion matters]
- Trigger / frequency / purpose: [event, how often, why it moves]
- States: [start, end, exit]
- Properties / timing: [animated properties, duration, easing or spring]
- Accessibility: [reduced-motion and hover/touch behavior]

Must show:
- [product screenshot]
- [workflow proof]
- [benchmarks / docs / integrations / customer proof]

Avoid:
- [anti-pattern 1]
- [anti-pattern 2]
- [anti-pattern 3]

Implementation bar:
- Keep the layout coherent on desktop and mobile.
- Make the hierarchy obvious in the first viewport.
- Use real product evidence instead of decorative filler.
```

## Tool Adapters

### Codex / Claude Code

Add:

- exact page or screen type
- product evidence requirements
- component expectations
- post-build verification request

Adapter line:

```text
After building, run the relevant checks and review the page for hierarchy, spacing, contrast, and whether the visual direction matches the requested style.
```

### Cursor

Keep it shorter and implementation-oriented.

Adapter line:

```text
Implement the visual direction with concrete layout, component, spacing, and typography choices. Keep the result aligned with the selected style family.
```

### v0 / Lovable

Bias toward sections, layout rhythm, and visual polish.

Adapter line:

```text
Focus on section composition, hierarchy, responsive layout, and polished components. Keep the style consistent across hero, proof sections, and repeated UI patterns.
```

## Compact DESIGN.md Template

```md
# DESIGN.md

## Visual Direction
- Overall style:
- Emotional tone:
- Density:
- Trust signal:

## Color System
- Background:
- Primary text:
- Secondary text:
- Accent:
- Border / divider:
- States:

## Typography
- Headline tone:
- Body tone:
- Scale behavior:
- Code / data text:

## Layout
- Preferred page rhythm:
- Content width:
- Section spacing:
- Grid behavior:

## Components
- Buttons:
- Cards / panels:
- Navigation:
- Tables / charts / code blocks:
- Forms / filters:

## Imagery
- Use:
- Do not use:

## Motion
- Hover / focus behavior:
- Transition character:
- Motion terms:
- Trigger / purpose:
- Duration / easing:
- Reduced motion:
- Review risks:

## Avoid
-
-
-
```

## Verification Checklist

Use 4-8 checks only. Favor observable outcomes.

```md
- [ ] The chosen style matches the audience and page type.
- [ ] The first viewport makes the product or workflow obvious.
- [ ] The interface shows real product proof, not placeholder atmosphere.
- [ ] Contrast, spacing, and hierarchy are consistent.
- [ ] Repeated UI patterns share the same visual rules.
- [ ] Motion has a named purpose, bounded timing, reduced-motion handling, and no high-frequency noise.
- [ ] The page avoids the listed anti-patterns.
```
