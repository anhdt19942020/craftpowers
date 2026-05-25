---
name: loop-checkpoint
description: Track agentic loop state across iterations. Start a loop with checkpoint, inspect status, resume after interruption.
---

# Loop Checkpoint

Tracks implement→verify→fix iterations so loops can be inspected and resumed.

## Commands

```
/man-loop-start <task>         # Start a tracked loop for <task>
/man-loop-status               # Show current loop state and iteration history
```

## When to use

Use when running a multi-iteration loop:
- Implement → run tests → fix failures → repeat
- Scrape → validate → retry → repeat
- Generate → evaluate → refine → repeat

Without checkpoint: lose track of which iteration, can't resume after interrupt.
With checkpoint: see pass/fail history, current iteration, stop when done.

## How /man-loop-start works

1. Ask user: task description (if not provided), max iterations (default 10)
2. Create `.claude/loop-checkpoint.json` via `loop_checkpoint.start_loop()`
3. Confirm: "Loop started. Run your loop. Use `/man-loop-status` to inspect."

## How /man-loop-status works

1. Read `.claude/loop-checkpoint.json`
2. Display:

```
Loop: <loop-id>
Task: <task>
Status: running | done | max_iterations_reached
Iteration: 3/10

History:
  [1] fail — tests: 12 failing (TypeError in auth.ts)
  [2] fail — tests: 5 failing (null check missing)
  [3] pass — all tests green

Action: Loop complete. Ready to commit.
```

3. If `status: max_iterations_reached` → warn: "Max iterations hit without passing. Review failures and consider `/man-debug`."
4. If no checkpoint: "No active loop. Start one with `/man-loop-start <task>`."

## Recording iterations

During loop execution, record each iteration result:

```python
from hooks.lib.loop_checkpoint import record_iteration
record_iteration(result="fail", notes="5 tests failing in auth module")
record_iteration(result="pass", notes="all tests green after null check fix")
```

Or manually update via skill:
```
/man-loop-status record pass  # Record current iteration as pass
/man-loop-status record fail  # Record current iteration as fail
```
