---
name: session-recovery
description: Use when resuming a previous session or after auto-compaction to rebuild working state from durable sources (git, plan files, disk)
phase: MAINTAIN
---

# Session Recovery

## Overview

After `/resume`, `--resume`, or auto-compaction, your conversation memory is incomplete. Plan details, file states, review decisions, and progress may be summarized or lost. This skill teaches you to rebuild working state from **durable sources** — git history, plan files on disk, and file system — instead of trusting compacted memory.

**Core principle:** Memory is lossy. Disk is truth. Always verify before continuing.

## When This Activates

| Trigger | How you know | Action |
|---------|-------------|--------|
| `/resume` or `--resume` | SessionStart hook fires with `source: "resume"` — you'll see a system reminder | Follow full recovery protocol below |
| After `/compact` | Context was just compressed | Follow recovery protocol (context-management covers the pre-compact side) |
| After auto-compaction | You notice gaps in your memory, or the conversation summary mentions prior work | Follow recovery protocol |
| User says "continue from yesterday" | No automatic trigger — user is referencing prior session | Ask what they were working on, then recover |

## Recovery Protocol

Run these steps in order. Each step takes seconds and prevents minutes of confusion.

### Step 1: Check Git State

```bash
git status                          # uncommitted work?
git log --oneline -10               # what was done recently?
git branch                          # which branch am I on?
```

**What to look for:**
- Uncommitted changes → you were mid-edit when session ended
- Recent commits with task numbers → progress indicator
- Wrong branch → switch before continuing

### Step 2: Find the Plan (if applicable)

```bash
ls docs/mankit/plans/               # any plan files?
```

If a plan file exists, **re-read it from disk** — this is the source of truth for task specs. Never trust compacted memory for task details.

Cross-reference with git log: commits since plan creation = completed tasks.

### Step 3: Check for Active Worktrees

```bash
git worktree list                   # any worktrees from prior session?
```

Active worktrees mean prior work was isolated. Check if they have uncommitted changes before removing.

### Step 4: Rebuild Context

Based on what you found, construct a mental model:

| Found | Means | Next action |
|-------|-------|-------------|
| Plan file + N commits | Tasks 1-N likely done | Re-read plan, identify next task |
| Uncommitted changes | Mid-task when session ended | Review changes, decide: commit or continue |
| Active worktree | Work was isolated | Check worktree state, continue there |
| Nothing | Fresh start or work was completed | Ask user what to do |

### Step 5: Confirm with User

Before resuming work, briefly state what you found:

```
"I found plan X with 5 tasks. Git shows 3 commits since plan creation, 
likely tasks 1-3 complete. Branch: feat/X. No uncommitted changes. 
Resuming from Task 4 — correct?"
```

**Never** silently continue from assumed state. Always confirm.

## What NOT to Trust After Resume

| Source | Trust level | Why |
|--------|------------|-----|
| Compacted conversation summary | Low | Summaries lose detail, especially code specifics |
| "I remember working on X" | None | Your memory is reconstructed, not recalled |
| Task completion state in summary | Medium | Cross-check with git log |
| Plan file on disk | High | Durable, unchanged since written |
| Git history | High | Immutable record of actual changes |
| File contents on disk | High | Current truth |

## Integration with Other Skills

**After recovery, hand off to the appropriate skill:**

- If executing a plan → resume with man:subagent-driven-development or man:executing-plans
- If context was high before resume → use man:context-management to stay lean
- If dispatching work → use man:effort-tuning for model selection

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Continuing without checking git | Always run git status + log first |
| Trusting compacted task list | Re-read plan file from disk |
| Assuming branch is correct | Check git branch before editing |
| Not confirming with user | State what you found, ask if correct |
| Re-reading entire codebase | Only read files relevant to next task |
| Ignoring uncommitted changes | Review them — they may be partial work |
