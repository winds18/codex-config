# Prompt Patterns

Use these when turning Refero inspiration into work for Codex, ZCode, v0, Lovable, or another UI-building agent.

## Design Brief Prompt

```md
Use $refero-design-system.

Task: Design <screen/page/flow> for <audience>.
Product goal: <what the user must accomplish>.
Functional constraints:
- <real API/data/actions available>
- <things that must not appear>

Visual reference:
- Primary direction: <Refero style URL or direction name>
- Preserve: <density/type/color/spacing/component grammar>
- Adapt: <brand colors/device/mobile constraints>

Deliver:
- Visual direction summary
- Tokens
- Components
- Page structure
- Empty/loading/error states
- Implementation checklist
- QA checklist
```

## Implementation Prompt

```md
Use $refero-design-system to implement the approved design direction.

Before editing:
- Read the existing design tokens and shared components.
- Preserve product scope and real API capability.
- Do not add visible mock/API/debug/internal wording.

Implement:
- Centralize tokens.
- Reuse or extend existing components.
- Apply the selected Refero-inspired grammar to typography, spacing, cards, navigation, buttons, and states.
- Keep mobile/H5 touch targets and safe areas correct.

Verify:
- Screenshot target pages.
- Compare against the brief.
- Run lint/type/build tests available for the project.
- Scan visible source strings for internal wording.
```

## High-Fidelity Prototype Prompt

```md
Use $refero-design-system to create one high-fidelity UI image for <single page>.

Reference direction: <style direction or URL>.
Page purpose: <user task>.
Data shown: <real fields only>.
Actions shown: <supported actions only>.
Do not include: <unsupported features/internal labels/mock copy>.

Output requirements:
- One page per image, no device frame unless requested.
- Use the selected typography, spacing, surface, and component grammar.
- Include realistic empty/error/loading states only if they are part of the page state.
```

## QA Checklist

- Visual direction is named and internally consistent.
- Palette has canvas, surface, text, muted text, border, and accent roles.
- Accent color is disciplined; it does not appear everywhere.
- Typography uses purposeful families and weights, not default stacks.
- Spacing and radii are intentional and repeated.
- Components share one grammar: card, button, chip, nav, metric, form, empty state.
- Mobile pages have touch-friendly spacing and readable hierarchy.
- Page content contains only product-facing language.
- No visible internal words: mock, API, OpenAPI, debug, audit, token, schema, asset id, priority labels, raw enum values.
- Every visible feature is backed by user requirements and implementation support.
