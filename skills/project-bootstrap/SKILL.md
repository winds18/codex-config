---
name: project-bootstrap
description: Use when starting a new software project from scratch and you want Codex to initialize project documents, project-level AGENTS rules, and a goal-first execution structure before writing substantial implementation code
---

# Project Bootstrap

## Overview

Use this skill to turn the global Codex operating rules into a concrete project-level starting structure.

This skill is for new projects, not normal feature work inside an already-structured repository.

## When to Use

Use when:

- a new project starts from an empty or nearly empty directory
- the user wants Codex to initialize the repo structure before major coding
- the project should follow goal-first execution
- the project should be suitable for autonomous or low-interruption Codex workflows

Do not use when:

- the repository already has a mature local `AGENTS.md`
- the task is just adding one feature to an existing project
- the user only wants brainstorming, not actual project initialization

## Required Outputs

The minimum project bootstrap output set is:

- `AGENTS.md`
- `README.md`
- `docs/spec.md`
- `docs/plan.md`
- `CHANGELOG.md`

Add `.codex/` files only when they will actually reduce ambiguity or improve automation.

## Workflow

1. Read the global operating rules from `~/.codex/AGENTS.md`.
2. Understand the intended project mission, constraints, stack, and exclusions.
3. Create or update the minimum project document set.
4. Convert global philosophy into repository-specific, executable rules.
5. Keep project documents concrete and short.
6. Do not start large-scale implementation until the project document layer exists.

## Ground Rules

- Do not copy the entire global `AGENTS.md` into the repository.
- Keep the project `AGENTS.md` specific to the repo's actual commands and risks.
- Put Mission and scope in `docs/spec.md`.
- Put Working Goal and stage sequencing in `docs/plan.md`.
- Keep the autonomous-execution boundary explicit.
- If a project is intended for unattended Codex execution, write down when Codex must stop and ask.

## References

Read these only when needed:

- `references/project-expansion-workflow.md`
  Use for the detailed initialization flow and file responsibilities.
- `references/project-AGENTS-template.md`
  Use when drafting the repository `AGENTS.md`.

## Expected Behavior

After using this skill, the repository should have:

- a clear project entry point
- a project-level operating contract
- a goal-first planning document
- a minimal changelog
- a clear next implementation stage

If these are missing, the bootstrap is incomplete.
