---
name: autonomous-project-execution
description: Use when a project already has basic repository documents and you want Codex to continue autonomous, goal-driven implementation with minimal interruptions, stage-based validation, and controlled goal correction
---

# Autonomous Project Execution

## Overview

Use this skill after project bootstrap, when Codex should move from setup into sustained implementation.

This skill is for low-interruption, goal-driven execution across multiple stages.

## When to Use

Use when:

- the repository already has a project `AGENTS.md`
- the project has at least a minimal `docs/spec.md` and `docs/plan.md`
- the user wants Codex to keep pushing implementation forward
- the workflow should support unattended or lightly supervised execution

Do not use when:

- the project has not been initialized yet
- the user is still defining the core project shape
- the current task is a one-off quick fix with no need for ongoing orchestration

## Preconditions

Before relying on this skill, the project should already have:

- repository-level operating rules
- a project mission and scope
- a current working plan
- a known validation path

If those are missing, use `project-bootstrap` first.

## Execution Model

The main thread should act as the orchestrator.

It should:

1. read Mission and Constraints
2. read or refine the current Working Goal
3. execute one stage at a time
4. validate before advancing
5. correct the Working Goal when reality changes
6. interrupt only on meaningful risk or boundary changes

## Ground Rules

- Do not treat code generation as completion.
- Do not continue indefinitely without validation.
- Do not silently weaken the mission, scope, or quality floor.
- Prefer one primary writing path per stage.
- Use subagents to reduce noise, not to create uncontrolled parallel edits.
- Record meaningful goal changes in project documents or execution summaries.

## References

Read these only when needed:

- `references/autonomous-execution-workflow.md`
  Use for the stage loop, interruption rules, and goal-correction policy.
- `references/agent-role-matrix.md`
  Use for recommended orchestrator, worker, and subagent role boundaries.

## Expected Behavior

After using this skill, Codex should be able to:

- keep a project moving stage by stage
- validate before claiming completion
- adjust short-term goals without drifting from the mission
- use subagents intentionally
- minimize unnecessary interruptions

If these behaviors are missing, the autonomous execution setup is incomplete.
