---
name: refero-design-system
description: Use Refero Styles as a frontend design taste library. Trigger when designing or redesigning product screens, landing pages, dashboards, mobile/H5 pages, high-fidelity prototypes, design systems, visual direction briefs, or when the user mentions styles.refero.design, Refero, DESIGN.md examples, design references, visual taste, UI polish, or asks to make an interface less generic.
---

# Refero Design System

Use Refero Styles as a reference library, not as a brand clone. Convert real website design systems into project-specific UI direction, tokens, components, and implementation checks.

## Core Workflow

1. Define the design job: screen type, user role, business goal, data/API constraints, device target, and existing project design system.
2. Select 1-3 visual references from Refero by matching density, tone, color, typography, and component weight. If live browsing is available, open `https://styles.refero.design`; otherwise use `references/style-directions.md`.
3. Extract the useful parts only: theme narrative, palette discipline, type hierarchy, spacing, radii, component shapes, motion, and do/don't constraints.
4. Translate into local tokens and UI decisions. Do not copy brand names, logos, proprietary assets, or unrelated features.
5. Produce an implementation-ready design brief: visual direction, token table, component rules, page structure, content rules, and QA checklist.
6. Before implementation, check product truth: every visible control, metric, form field, state, chart, and CTA must be supported by the user's requirements and current backend/frontend capability.

## References

- Read `references/refero-workflow.md` when using the live Refero site or a Refero style page.
- Read `references/style-directions.md` when choosing a visual direction without browsing, or when you need a quick style palette.
- Read `references/prompt-patterns.md` when writing a design task for Codex, ZCode, v0, Lovable, or another UI-building agent.

## Guardrails

- Prefer one strong visual concept over a generic mix of gradients, cards, and icons.
- Preserve the product's actual requirements and existing design system before adopting any Refero pattern.
- Use Refero as taste calibration: typography, spacing, density, restraint, and component grammar matter more than copying colors.
- For mobile/H5/product screens, adapt desktop references into compact navigation, touch targets, readable hierarchy, and real empty/error/loading states.
- Never show internal implementation terms in user-facing UI, such as mock, API, OpenAPI, audit, debug, token, schema, asset id, or task-priority labels.
