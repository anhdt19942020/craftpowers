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

## opusplan — Hybrid Planning Mode

`opusplan` runs Opus for the planning phase then Sonnet for execution. Best for workflows where planning quality matters more than execution speed.

**When to use opusplan:**
- writing-plans + executing-plans flow — Opus designs the plan, Sonnet implements
- Complex refactors where the plan is the hard part
- Architecture decisions followed by mechanical changes

**How to enable:**
```bash
# Set as default model
claude --model opusplan

# Or via environment variable
export ANTHROPIC_DEFAULT_MODEL=opusplan
```

**Cost tradeoff:** opusplan costs more than pure Sonnet but less than pure Opus. The Opus planning phase is typically 1-3 turns; Sonnet handles the remaining 10-50 turns.

**Do NOT use opusplan for:**
- Quick fixes (use Haiku or Sonnet)
- Pure research/reading tasks (use Sonnet)
- Tasks where the plan is already written (use Sonnet directly)

## Per-Agent Effort Levels

Each mankit agent has an optimal effort level based on its role:

| Agent | Model | Effort | Rationale |
|-------|-------|--------|-----------|
| Gia Cát Lượng (architect) | Opus | max | Architecture needs deep reasoning |
| Lưu Bị (tech lead) | Opus | high | Coordination needs broad context |
| Bàng Thống (debugger) | Opus | max | Root-cause analysis is reasoning-heavy |
| Tư Mã Ý (secure-reviewer) | Sonnet | high | Security review is methodical, not creative |
| Pháp Chính (code-reviewer) | Sonnet | high | Code review is pattern matching |
| Triệu Vân (implementer) | Sonnet | default | Implementation follows specs |
| Quan Vũ (backend dev) | Sonnet | default | Implementation follows specs |
| Trương Phi (frontend dev) | Sonnet | default | Implementation follows specs |
| Hoàng Trung (test-engineer) | Haiku | default | Test review is mechanical |
| Mã Lương (doc-writer) | Haiku | default | Documentation is structured |
| quick-fix | Haiku | low | Surgical edits need speed, not depth |
| journal-writer | Haiku | low | Append-only logging |
| codebase-explorer | Sonnet | default | Broad read, moderate reasoning |
| release-prep | Sonnet | default | Checklist execution |

**Effort level flags:**
- `max` — deepest reasoning, highest cost. Use for architecture and debugging.
- `high` — thorough analysis. Use for reviews and coordination.
- `default` — balanced. Use for most implementation.
- `low` — fast and cheap. Use for mechanical tasks.

## Extended Context (1M)

Append `[1m]` to model env vars for 1M token context window:

```bash
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-4-7[1m]"
```

**When to enable 1M:**
- codebase-explorer on repos with 500+ files
- Full-repo refactors touching 20+ files
- Architecture review of an entire monorepo

**When NOT to enable:**
- Normal development (200K is sufficient)
- Cost-sensitive sessions (1M context = higher per-turn cost)
- Quick fixes or focused tasks

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
