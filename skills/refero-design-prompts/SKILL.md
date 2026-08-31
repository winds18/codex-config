---
name: refero-design-prompts
description: Use when a user wants a website, product UI, dashboard, landing page, or frontend visual direction translated into a structured design prompt, a compact DESIGN.md brief, or both, especially when choosing among clean SaaS, dark mode, devtool, editorial, AI-startup, or other Refero-style aesthetics.
---

# Refero Design Prompts

## Overview

Turn a loose product or page brief into three linked artifacts:

1. a recommended visual direction
2. a build-ready prompt
3. a compact `DESIGN.md` block

Use this skill when the visual bar is unclear, the user wants better frontend prompting, or an agent needs fewer aesthetic guesses.

## Workflow

1. Identify the surface and outcome.
   - Surface examples: landing page, marketing site, docs site, dashboard, product UI, onboarding, settings, pricing.
   - Outcome examples: earn trust, explain workflow, show product proof, improve scanability, feel premium, feel technical.
2. Choose one primary style family and one backup style.
   - Read `references/style-taxonomy.md` when the fit is unclear or the user asks for alternatives.
   - Read `references/substyle-recipes.md` when the user wants a more specific temperament such as quieter SaaS, denser workbench, or frontier AI launch.
   - Read `references/visual-archetypes.md` when the user asks for a polished homepage, portfolio, creator page, personal brand, strong hero, motion-heavy visual direction, single HTML showcase, or HTML presentation feel.
   - Read `references/motion-craft-workflow.md` when the request mentions animation, transition, motion, microinteraction, component polish, gesture, smoothness, review of existing motion, or exact animation terminology.
3. Lock the output mode.
   - `prompt`
   - `DESIGN.md`
   - `prompt + DESIGN.md + verification`
4. Produce the response in this order:
   - `结论`
   - `风格判断`
   - `Build Prompt`
   - `DESIGN.md`
   - `验证清单`

## Rules

- Recommend one style first, then one backup with a clear tradeoff.
- Explain fit through audience, trust signal, density, proof assets, and emotional tone.
- Use concrete constraints instead of vague taste words:
  - color system
  - contrast level
  - typography
  - spacing rhythm
  - radius and border weight
  - imagery direction
  - motion restraint
  - component emphasis
  - anti-patterns
- Name the product evidence that should appear in the page or UI:
  - screenshots
  - dashboards
  - logs
  - docs
  - API snippets
  - benchmarks
  - testimonials
  - workflow diagrams
- Keep operational tools operational. Dashboards, admin tools, workflow apps, and devtools should stay dense, restrained, and scan-friendly.
- Prefer a known substyle before inventing a new label. Reuse `quiet-saas`, `technical-workbench`, or `frontier-ai-launch` when they fit.
- For high-polish frontend requests, choose a visual archetype by surface, audience, proof assets, density, motion budget, and implementation risk. Do not use a template name as a substitute for layout and component decisions.
- When motion matters, include a Motion Contract: term, trigger, frequency, purpose, states, properties, duration/easing, origin, interruptibility, reduced-motion, and verification evidence.
- If the user provides a URL, screenshot, or brand reference, treat it as a signal set. Extract what to borrow and what to avoid. Do not promise an exact clone unless the user explicitly asks for one.
- Do not copy third-party code, assets, text, prompts, or template structure into the output unless the license and user authorization allow it. Record source and license boundaries when external material shapes the design.

## Output Contract

Always keep the output compact but structured.

### 1. 结论

- `主风格`:
- `备选风格`:
- `适配原因`:

### 2. 风格判断

Summarize:

- target audience
- product maturity signal
- information density
- proof assets to surface
- what to avoid

### 3. Build Prompt

Write one ready-to-use prompt for the target tool. Default to Codex-style wording unless the user names another tool.

### 4. DESIGN.md

Emit a compact `DESIGN.md` block with only the sections needed for the request.

### 5. 验证清单

End with a short review checklist the builder can run after implementation.

## Tool Targeting

Read `references/output-templates.md` when adapting the same visual direction for different builders.

- Codex / Claude Code:
  - include concrete UI constraints and a short verification pass
- Cursor:
  - keep wording concise and file-task oriented
- v0 / Lovable:
  - emphasize sections, layout, component polish, and visual hierarchy

## References

- `references/style-taxonomy.md`
  Use this to choose the right style family and avoid mismatched aesthetics.
- `references/substyle-recipes.md`
  Use this when the user wants a more precise mood inside a larger style family.
- `references/visual-archetypes.md`
  Use this for polished homepage, portfolio, creator, personal brand, hero-led, motion-rich, single HTML, or presentation-like visual directions.
- `references/motion-craft-workflow.md`
  Use this to normalize animation terminology, decide whether motion should exist, specify component-level Motion Contract, and review motion quality.
- `references/output-templates.md`
  Use this for prompt scaffolds, `DESIGN.md` structure, and verification checklists.
