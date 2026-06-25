---
name: feature-thread-launch
description: Use when the main project thread should delegate a bounded feature, bugfix, refactor, or noisy verification task into a separate feature thread with minimal overhead
---

# Feature Thread Launch

## Overview

Use this skill when the main thread should stay as the project control plane, and a concrete implementation task should be pushed into a separate feature thread.

This skill is intentionally lightweight. Its purpose is to launch reliable feature threads without turning handoff into bureaucracy.

## When to Use

Use when:

- the main thread has identified a concrete implementation task
- the task will create logs, repeated edits, debugging loops, or noisy validation work
- the task should be isolated in a feature thread, ideally in a worktree
- the user wants the main thread context preserved for project control

Do not use when:

- the work is only a tiny low-noise control-plane edit
- the task is still too vague to define a bounded objective
- the repository has not yet been bootstrapped into a project-level workflow

## Required Launch Inputs

Keep the launch packet minimal but sufficient:

- bounded objective
- acceptance criteria
- relevant files or directories
- constraints that must remain unchanged
- worktree preference when applicable

Add subagent recommendations only when they will reduce noise or accelerate reading-heavy work.

## Launch Workflow

1. Confirm the task should not stay in the main thread.
2. Define one bounded feature-thread objective.
3. Define acceptance criteria close to the real delivery path.
4. Point to the relevant code area and known risks.
5. Prefer a worktree for long, noisy, or unattended work.
6. Instruct the feature thread to use subagents early for exploration, log triage, test-gap scanning, and first-pass review when useful.
7. Require a short return summary with verification evidence, changed files, goal delta, and known limits.

## Ground Rules

- Keep launch packets short and executable.
- Prefer framework and main delivery path before detail completion.
- Do not let documentation, edge-case polish, or exhaustive test expansion block the main feature path before it is alive.
- If a feature thread gets trapped in local optimization, correct its goal or stage objective quickly.
- One feature thread should normally have one primary write path.

## References

Read this only when needed:

- `references/feature-thread-launch-checklist.md`
  Use for the standard handoff checklist and lightweight launch format.

## Expected Behavior

After using this skill, the main thread should preserve project-level control context while the feature thread executes one bounded delivery unit with minimal noise.

If the launch packet becomes long, vague, or overloaded with premature detail work, the launch is too heavy.
