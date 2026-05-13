---
name: cost-budgeting
description: Use when session-summary hook reports token usage at session end, or when planning a multi-task session to estimate and control token spend
phase: MAINTAIN
---

# Cost Budgeting

## Overview

Every session costs tokens. Without awareness, a 5-task plan can burn 500K+ tokens when 200K would suffice. This skill helps you track, estimate, and reduce token spend — both within a session and across sessions.

**Core principle:** Know what you're spending before you spend it. The cheapest token is the one you don't use.

## Session Summary

The `session-summary` hook fires at session end and reports:

```
[craftpowers/session-summary] Input: 45.2K | Output: 12.8K | Total: 58.0K (~29% of 200k) | RTK savings: 15.3K (20.9%)
```

| Field | What it means |
|-------|---------------|
| **Input** | Tokens Claude read (your prompts, tool results, system messages) |
| **Output** | Tokens Claude wrote (responses, tool calls) |
| **Total** | Combined — this is what you pay for |
| **% of limit** | How much context window was used |
| **RTK savings** | Tokens saved by RTK command filtering |

## Estimating Cost Before Starting

Before a multi-task session, estimate total cost:

| Work type | Tokens per task | Example |
|-----------|----------------|---------|
| Simple edit (1 file, clear spec) | 5K-15K | Rename function, fix typo |
| Implementation (1-2 files) | 15K-40K | New function with tests |
| Multi-file implementation | 40K-80K | Feature spanning 3+ files |
| Code review | 20K-50K | Review + feedback loop |
| Research/exploration | 10K-30K | Grep, read files, summarize |
| Subagent dispatch (per agent) | 15K-40K | Implementer + reviewer |

**Formula:** Total ≈ (tasks × avg tokens per task) + coordination overhead (~20%)

**Example:** 5-task plan with implementation tasks:
- 5 × 30K = 150K implementation
- 150K × 1.2 = 180K with coordination
- Add 2 review subagents × 25K = 50K
- **Total estimate: ~230K tokens**

## Cost Reduction Strategies

### 1. Use RTK for All Commands

RTK filters command output, saving 50-90% on tool results. Always prefix:

```bash
rtk git status          # 59% savings
rtk git diff            # 80% savings
rtk cargo test          # 90% savings
```

If RTK savings shows "N/A", RTK is not installed or not being used.

### 2. Right-Size Models (see man:effort-tuning)

| Role | Cheap choice | Expensive choice | Savings |
|------|-------------|-----------------|---------|
| Grep/search subagent | Haiku | Opus | ~70% |
| Implementation subagent | Sonnet | Opus | ~40% |
| Reviewer subagent | Sonnet | Opus | ~40% |

### 3. Minimize Context Growth

- Offload research to subagents (their context doesn't grow yours)
- Compact strategically at 70% (see man:context-management)
- Don't re-read files you just wrote
- Use targeted git commands (`git diff -- file.py` not `git diff`)

### 4. Batch vs. Sequential

| Approach | Cost | When |
|----------|------|------|
| Single session, all tasks | Higher (context grows) | Tasks depend on each other |
| Subagent per task | Lower (fresh context each) | Independent tasks |
| Agent team | Highest (N+1 sessions) | Need coordination |

## Reading the Session Summary

After each session, check the summary and ask:

| If you see... | It means... | Action |
|---------------|-------------|--------|
| Total > 150K on simple tasks | Over-thinking or context bloat | Use man:effort-tuning, compact earlier |
| RTK savings: N/A | RTK not filtering commands | Add `rtk` prefix to all commands |
| RTK savings < 10% | Few commands run through RTK | Increase RTK usage |
| Input >> Output (10:1+) | Reading too much, writing too little | Offload reads to subagents |
| Output >> Input | Verbose responses | Already efficient |

## Budget Targets

| Session type | Target total tokens | Red flag if above |
|--------------|--------------------|--------------------|
| Quick fix (1-2 files) | 10K-30K | 50K |
| Single feature implementation | 50K-150K | 200K |
| Multi-task plan (5 tasks) | 150K-300K | 400K |
| Full plan with reviews | 200K-400K | 500K |

## Integration

- **man:effort-tuning** — choose cheaper models per task
- **man:context-management** — compact before context bloat
- **Session summary hook** — automatic cost report at session end
