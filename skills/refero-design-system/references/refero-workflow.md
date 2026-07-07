# Refero Workflow

Source baseline checked on 2026-07-08:

- `https://styles.refero.design/`
- `https://styles.refero.design/ai-agents/design-resources`
- `https://styles.refero.design/ai-agents/design-prompts`

## What Refero Provides

Refero Styles is a library of AI-readable website style systems. The homepage describes 2,000+ design systems and says each style can expose colors, typography, spacing, components, and a DESIGN.md usable in coding agents. Individual style pages include tabs for Preview, DESIGN.md, Tailwind v4, CSS Variables, and Design Tokens.

Use it before first draft design, not after. The design resources guide frames the workflow as selecting the closest design job, opening a relevant resource, and comparing styles by density, tone, color, type, and component weight. The prompt guide emphasizes that good UI prompts combine product problem, concrete interface, and a real visual system reference.

## Live-Site Procedure

1. Open `https://styles.refero.design/`.
2. Search by brand, mood, screen type, color, or product category.
3. Open 3-6 candidate style pages.
4. For each page, capture:
   - Theme phrase and one-sentence design intent.
   - Primary canvas and surface colors.
   - Accent color discipline: where color is allowed and where it is forbidden.
   - Typography family, weights, scale, tracking, and role split.
   - Spacing base unit, card padding, section rhythm, max width.
   - Shape language: radii, borders, shadows, dividers.
   - Component grammar: buttons, cards, navigation, badges, tables, hero sections, empty states.
   - Do/don't rules that prevent generic UI.
5. Choose one dominant reference and optionally one secondary reference. Avoid mixing more than two visual systems.
6. Rewrite the style into project-native tokens and components.

## Extraction Template

```md
Reference: <Refero style URL>
Theme: <short mood phrase>
Use for: <screen/product fit>
Avoid for: <where it would be wrong>

Palette:
- Canvas:
- Surface:
- Text:
- Muted text:
- Accent:
- Border:

Typography:
- Display:
- Body:
- Labels/meta:
- Tracking/weight rule:

Layout:
- Base spacing:
- Card padding:
- Section gap:
- Radius:
- Border/elevation:

Components:
- Primary button:
- Secondary button:
- Card:
- Navigation:
- Empty/error states:

Do:
- ...

Don't:
- ...
```

## Translation Rules

- Replace reference brand colors with local token names.
- Preserve color discipline, not exact hue, unless the user explicitly wants exact visual mimicry.
- Convert desktop spacing to mobile density deliberately; do not shrink everything linearly.
- If the target repo already has tokens/components, extend them instead of creating a parallel design system.
- Treat the Refero DESIGN.md as a design brief. The product's real requirements still decide what appears on screen.

## Source Notes

- Homepage: 2,000+ AI-readable systems; style pages expose colors, type, spacing, components, DESIGN.md, Tailwind, CSS variables, and tokens.
- Resource guide: choose the design job, open the closest resource, compare by density/tone/color/type/component weight.
- Prompt guide: start with exact screen/audience, attach a real visual reference, and tell the agent what to preserve.
