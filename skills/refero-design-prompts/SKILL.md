---
name: refero-design-prompts
description: Use when a website, product UI, dashboard, landing page, or frontend brief needs a structured visual direction, build prompt, project-level DESIGN.md contract, verification criteria, or a reusable bundled template, especially for Refero-style aesthetics.
---

# Refero Design Prompts

## Overview

Turn a loose product or page brief into the requested combination of:

1. a recommended visual direction
2. a build-ready prompt
3. a project-level `DESIGN.md`

Use this skill when the visual bar is unclear, the user wants better frontend prompting, or an agent needs fewer aesthetic guesses.

## Workflow

1. Identify the surface and outcome.
   - Surface examples: landing page, marketing site, docs site, dashboard, product UI, onboarding, settings, pricing.
   - Outcome examples: earn trust, explain workflow, show product proof, improve scanability, feel premium, feel technical.
2. Establish product truth before visual decisions.
   - Inspect supported data, actions, states, APIs, assets, existing tokens, and shared components.
   - Do not invent visible controls, metrics, states, or product claims that the requirements and implementation cannot support.
3. Choose or preserve the visual direction.
   - Read `references/style-taxonomy.md` when the fit is unclear or the user asks for alternatives.
   - Read `references/substyle-recipes.md` when the user wants a more specific temperament such as quieter SaaS, denser workbench, or frontier AI launch.
   - Read `references/visual-archetypes.md` when the user asks for a polished homepage, portfolio, creator page, personal brand, strong hero, motion-heavy visual direction, single HTML showcase, or HTML presentation feel.
   - Read `references/motion-craft-workflow.md` when the request mentions animation, transition, motion, microinteraction, component polish, gesture, smoothness, review of existing motion, or exact animation terminology.
   - Read `references/design-md-contract.md` when creating or updating a durable project-level `DESIGN.md`, or when a known template or brand reference should come from the user's unified template source.
4. Lock the output mode.
   - `prompt`
   - `DESIGN.md`
   - `prompt + DESIGN.md + verification`
5. Emit only the artifacts selected by the output mode. When several are requested, use this order: `结论`, `风格判断`, `Build Prompt`, `DESIGN.md`, `验证清单`.

## Bundled Template Library

Use the bundled local assets as the default unified template source. Do not load every template; inspect only the discovery surface and the selected template.

- Brand and product design systems:
  - Start with `assets/templates/awesome-design-md/README.md`.
  - Read the selected `assets/templates/awesome-design-md/design-md/<slug>/DESIGN.md` and its adjacent `README.md` when present.
  - Use one primary template and at most one secondary template.
- Personal homepage, portfolio, Hero, single HTML, and HTML presentation:
  - Start with `assets/templates/personal-homepage-skill/README.md` and `src/data/templates.ts`.
  - Use `demo/template-gallery.html` or `assets/template-previews/` when visual comparison is needed.
  - Reuse executable starters from `templates/`; copy the complete selected subtree with its referenced assets, scripts, and media.
- Record the local asset path, upstream commit from `UPSTREAM_COMMIT`, license, borrowed patterns, and excluded assets in the project `DESIGN.md`.
- Browse upstream only when the local snapshot has no suitable template or the user explicitly asks for the latest version.

## Rules

- When direction is unclear, recommend one primary style and at most one backup with a clear tradeoff. Preserve an approved direction instead of reopening style selection.
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
- Existing product capabilities and the local design system take precedence over references. Extend existing tokens and components instead of creating a parallel system.
- Prefer a known substyle before inventing a new label. Reuse `quiet-saas`, `technical-workbench`, or `frontier-ai-launch` when they fit.
- For high-polish frontend requests, choose a visual archetype by surface, audience, proof assets, density, motion budget, and implementation risk. Do not use a template name as a substitute for layout and component decisions.
- When motion matters, include a Motion Contract: term, trigger, frequency, purpose, states, properties, duration/easing, origin, interruptibility, reduced-motion, and verification evidence.
- For durable frontend systems, use `DESIGN.md` as the visual source of truth: source references, semantic tokens, typography, spacing, component states, motion, assets, responsive rules, do/avoid, and verification.
- When a known template or brand reference is requested, use the bundled local template source first. The imported upstream README and template registry are discovery surfaces; do not maintain a parallel template index.
- If the user provides a URL, screenshot, or brand reference, treat it as a signal set. Extract what to borrow and what to avoid. Do not promise an exact clone unless the user explicitly asks for one.
- Do not copy third-party code, assets, text, prompts, or template structure into the output unless the license and user authorization allow it. Record source and license boundaries when external material shapes the design.

## Output Contract

Keep the output compact and include only the sections required by the selected mode.

### 1. 结论

Include only when choosing or comparing visual directions.

- `主风格`:
- `备选风格`:
- `适配原因`:

### 2. 风格判断

Include only when the fit needs explanation.

Summarize:

- target audience
- product maturity signal
- information density
- proof assets to surface
- what to avoid

### 3. Build Prompt

Include in `prompt` modes. Write one ready-to-use prompt for the target tool. Default to Codex-style wording unless the user names another tool.

### 4. DESIGN.md

Include in `DESIGN.md` modes. Use the project-level contract for durable systems; keep one-off briefs proportional to scope.

### 5. 验证清单

Include when verification is requested or the output is intended for implementation.

## Tool Targeting

Read `references/output-templates.md` when adapting the same visual direction for different builders.

- Codex / Claude Code:
  - include concrete UI constraints and a short verification pass
- Cursor:
  - keep wording concise and file-task oriented
- v0 / Lovable:
  - emphasize sections, layout, component polish, and visual hierarchy
