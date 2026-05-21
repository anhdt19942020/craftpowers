---
name: context-management
description: Use when context-tracker warns about high usage, before running /compact, or when deciding whether to offload work to subagents to preserve context
phase: MAINTAIN
---

# Context Management

## Overview

Context window is a finite resource. Losing critical state during auto-compaction is the #1 cause of agent confusion mid-task. This skill teaches you to compact **strategically** — preserving what matters, discarding what doesn't, and using subagents to keep your own context lean.

**Core principle:** Compact is not "forget everything" — it's "choose what to remember."

## When This Activates

The `context-tracker` hook fires a systemMessage when context usage crosses thresholds:

| Level | Threshold | What to do |
|-------|-----------|------------|
| Warning | ~70% (140K tokens) | Start planning — finish current task, then compact |
| Critical | ~87% (175K tokens) | Compact NOW — next auto-compaction may lose state |

These thresholds apply to ALL models, including Opus 4.7 (1M window). The 1M window is a safety buffer for compaction overhead — not a fill target. Compacting at 140K keeps summaries high-quality; waiting until 800K means the compactor itself runs out of room.

When you see `[craftpowers/context-tracker]` in a system message, follow the strategy below.

## Smart Compaction (Auto-configured)

Mankit configures two settings via `install.py` that make compaction intelligent:

### 1. Custom Compact Prompt (`compactPrompt`)

Tells Claude what to preserve vs compress during summarization:

| Preserve verbatim | Compress aggressively |
|---|---|
| CLAUDE.md rules | Tool command output → conclusions only |
| Plan file paths + phase | API responses → final data only |
| Task list + completion status | Test output → fail summary only |
| Branch + worktree paths | Git logs → last 5 commits |
| Architectural decisions | File exploration → file list only |
| User decisions + review findings | Grep/search → matched files only |
| File ownership (agent teams) | |

### 2. Auto-compact Threshold (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70`)

Default Claude auto-compacts at 95% — too late, summary quality degrades. Mankit triggers at 70%:
- More context budget available for high-quality summarization
- PreCompact hook auto-snapshots git state + plan files to `~/.claude/compact-snapshots/`
- PostCompact hook reads snapshot and injects specific recovery instructions

### 3. PreCompact Auto-Snapshot

When compaction triggers, the hook automatically saves to disk:
- Current branch, git status, last 5 commits
- Active plan file paths (scanned from `plans/`)
- Working directory, worktree state
- Timestamp and trigger type

PostCompact reads this snapshot and tells you exactly what to re-read — no guessing.

## Compact Strategy

### Step 1: Inventory What Matters

Before running `/compact`, identify state that must survive:

| Category | Examples | How to preserve |
|----------|----------|-----------------|
| **Active plan** | Plan file path, completed tasks, next task | Include in /compact prompt |
| **Branch state** | Current branch, worktree path, base branch | Include in /compact prompt |
| **Key decisions** | "Reviewer said use X not Y", "User wants Z" | Include in /compact prompt |
| **File locations** | Files being edited, test files | Re-read from disk after compact |
| **Git history** | What was already implemented | `git log` after compact |

### Step 2: Run /compact With Context

```
/compact Keep: <what you're doing> via <skill if applicable>.
Completed: <what's done>. Next: <what's next>.
Branch: <branch>. Worktree: <path if applicable>.
Decisions: <key decisions that affect remaining work>.
```

### Step 3: Recover After Compact

1. Re-read plan file from disk (source of truth — never rely on compacted memory for specs)
2. Run `git log --oneline <base>..HEAD` to see what was already implemented
3. Check git status for uncommitted work
4. Resume from next incomplete task

## Proactive Context Hygiene

Don't wait for the warning. These habits keep context lean:

**Offload to subagents:** Research, grep, file exploration — anything read-only that produces large output. Subagent context doesn't pollute yours; only their summary returns.

**Commit frequently:** Committed code is recoverable via git. Uncommitted changes are lost if context compacts and you forget the file path.

**Don't re-read files unnecessarily:** If you just wrote a file, don't read it back to verify. The Edit/Write tool would have errored if it failed.

**Summarize before moving on:** After completing a sub-task, write a 1-2 line summary of what changed. This survives compaction better than raw tool output.

## Uncommitted Code at Critical Threshold

If you're mid-function when critical threshold hits:

1. **Finish the current function** — 10% headroom (~20K tokens) is enough
2. **Commit as WIP** — `git commit -m "wip: <what> — compacting context"`
3. **Then compact** — committed code survives via `git diff`; uncommitted code in a compacted summary is guesswork

**Never** stop mid-function and compact. A half-written function summarized by compaction becomes subtly wrong reconstructions.

## Using /btw for Lightweight Notes

Before compacting, use `/btw` to record small observations that don't need a full message:

```
/btw Task 5 needs the bcrypt change from Task 3 review
/btw File src/auth/hash.ts has a TODO on line 42
```

`/btw` messages cost minimal context and survive as conversation markers. Use them to breadcrumb decisions that are too small for the compact prompt but too important to lose.

## Decision: Compact vs. Subagent vs. Continue

```dot
digraph decision {
    "Context above 70%?" [shape=diamond];
    "In the middle of a task?" [shape=diamond];
    "Remaining work is large?" [shape=diamond];
    "Continue — finish current task first" [shape=box];
    "Compact now with strategy above" [shape=box];
    "Dispatch subagent for remaining work" [shape=box];

    "Context above 70%?" -> "In the middle of a task?" [label="yes"];
    "Context above 70%?" -> "No action needed" [label="no"];
    "In the middle of a task?" -> "Continue — finish current task first" [label="yes — commit WIP first"];
    "In the middle of a task?" -> "Compact now with strategy above" [label="no or far from done"];
    "Continue — finish current task first" -> "Remaining work is large?" [label="task done"];
    "Remaining work is large?" -> "Dispatch subagent for remaining work" [label="yes — isolate context"];
    "Remaining work is large?" -> "Compact now with strategy above" [label="no — compact and continue"];
}
```

## Workflow-Specific Additions

When using **subagent-driven-development** or **executing-plans**, also preserve:
- Plan file path (re-read after compact)
- Task completion state (by number)
- Review decisions that affect later tasks

When using **agent-teams**, the lead's context is the bottleneck:
- Delegate heavy investigation to teammates
- Lead should only hold coordination state
- Compact lead context between team phases

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running /compact with no context prompt | Always specify what to keep |
| Trusting compacted memory for task specs | Re-read plan file from disk |
| Ignoring warning until critical | Start planning compact at 70% |
| Keeping large tool outputs in context | Use subagents for research-heavy work |
| Not checking git after compact | Run `git log` and `git status` to recover state |
| Stopping mid-function to compact | Finish function, commit WIP, then compact |
| Assuming opus-4-7 (1M) means no compact needed | Same thresholds — 1M is safety buffer, not fill target |
