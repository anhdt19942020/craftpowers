---
name: effort-tuning
description: Use when dispatching subagents or teammates to choose the right model and effort level per task — referenced by subagent-driven-development, dispatching-parallel-agents, and agent-teams
phase: BUILD
---

# Effort Tuning

## Overview

Not every task needs maximum reasoning. A typo fix with Opus costs 10x more than with Haiku and takes longer. This skill is the canonical reference for choosing model and effort level when dispatching work.

**Core principle:** Use the least powerful model that can handle the task. Over-provisioning wastes tokens; under-provisioning causes thrashing.

## Model Tiers

| Tier | Models | Cost | Speed | Use for |
|------|--------|------|-------|---------|
| **Cheap** | Haiku | $$ | Fast | Read-only research, grep, file exploration, formatting |
| **Standard** | Sonnet | $$$ | Medium | Implementation with clear spec, tests, single-file changes |
| **Capable** | Opus | $$$$ | Slower | Architecture, multi-file coordination, code review, debugging |

## Task → Model Decision Table

| Task type | Complexity signals | Model | Effort |
|-----------|-------------------|-------|--------|
| Typo fix, rename, format | 1 file, mechanical | Haiku | Low |
| Grep, search, read files | Read-only, no judgment | Haiku | Low |
| Implement function from spec | 1-2 files, clear spec | Sonnet | Medium |
| Write tests from spec | Test patterns exist | Sonnet | Medium |
| Multi-file implementation | 3+ files, integration | Sonnet | High |
| Code review | Judgment, pattern matching | Opus | High |
| Architecture, design | Broad codebase knowledge | Opus | High |
| Debug complex/intermittent | Root cause analysis | Opus | High |
| Security review | Threat modeling | Opus | High |

**Upgrade signal:** If a Sonnet subagent returns BLOCKED or thrashes (3+ attempts), re-dispatch with Opus. Don't retry the same model without changes.

**Downgrade signal:** If you're dispatching Opus for a task with a complete spec touching 1-2 files, use Sonnet instead.

## For Subagent Dispatch

When using **subagent-driven-development** or **dispatching-parallel-agents**:

```
Agent({
  model: "haiku",   // or "sonnet" or "opus"
  prompt: "..."
})
```

**Implementer subagents:** Default Sonnet. Only upgrade to Opus if task requires multi-file coordination or design judgment.

**Reviewer subagents:** Default Opus for spec review (needs judgment). Sonnet is fine for mechanical checks (lint, format, test count).

**Research subagents:** Default Haiku. They grep, read files, summarize — no reasoning needed.

## For Agent Teams

When using **agent-teams**, set teammate models based on role:

| Teammate role | Model | Reasoning |
|---------------|-------|-----------|
| Lead (coordinator) | Opus | Architectural decisions, synthesis |
| Backend implementation | Sonnet | Clear specs, focused scope |
| Frontend implementation | Sonnet | Component building, UI logic |
| Test writer | Sonnet | Pattern-based, spec-driven |
| Reviewer | Opus | Judgment, cross-cutting concerns |
| Research/scout | Haiku | Read-only exploration |

Configure default in `~/.claude.json`:

```json
{
  "teammateDefaultModel": "sonnet"
}
```

Override per-teammate when their role demands it. Most teammates are implementers → Sonnet is the right default.

## /fast Toggle

Claude Code's `/fast` mode uses the same model with faster output. Use it for:

- Quick edits after a plan is clear
- Mechanical implementation steps
- Running through a checklist of small fixes

Turn OFF `/fast` for:
- Architecture decisions
- Complex debugging
- Code review where nuance matters

## Cost Impact

| Scenario | Without tuning | With tuning | Savings |
|----------|---------------|-------------|---------|
| 5-task plan, all Opus | 5 × Opus | 1 Opus + 4 Sonnet | ~40% |
| 3 parallel searches | 3 × Sonnet | 3 × Haiku | ~60% |
| Agent team (1+3) | All Opus | 1 Opus + 3 Sonnet | ~35% |
| Review + implement | Both Opus | Opus review + Sonnet impl | ~25% |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using Opus for everything | Check task table — most implementation is Sonnet |
| Using Haiku for implementation | Haiku can't hold multi-step reasoning — use Sonnet minimum |
| Retrying failed Sonnet with Sonnet | Upgrade to Opus, or provide more context |
| Never using /fast | Toggle it for mechanical steps in known territory |
| Forgetting to downgrade after hard task | Reset to Sonnet after the Opus-level task is done |
