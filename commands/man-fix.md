---
description: "Debug and fix a bug, test failure, or unexpected behavior. Uses Agent Teams — lead coordinates bang-thong + phap-chinh."
---

You are the **team lead**. Do not delegate this role.

## Step 1 — Triage

Read the bug description (everything after `/man-fix`). Classify:

- **Simple** (single file, clear error, obvious cause): skip Agent Teams — fix directly in this session.
- **Complex** (intermittent, spans multiple files, multiple hypotheses, unclear cause): proceed to Agent Teams.

For complex bugs, tell the user:
> "Complex bug — spawning an Agent Team: bang-thong investigates root cause, phap-chinh reviews the fix."

## Step 2 — Create team and shared task list

```
TeamCreate({
  team_name: "fix-<bug-slug>",
  description: "Debug and fix: <bug summary>"
})

TaskCreate({
  subject: "Investigate root cause of <bug summary>",
  description: "Files to check: <relevant files>\nError: <exact error message>\nReport: root cause + proposed fix"
})
TaskCreate({
  subject: "Review fix from debugger",
  description: "Check: correctness, edge cases, test coverage, regressions\nReport: APPROVE or list issues"
})
TaskUpdate({ id: "2", addBlockedBy: ["1"] })
```

## Step 3 — Spawn teammates

**Teammate 1 — Debugger (spawn immediately):**

```
Agent({
  team_name: "fix-<bug-slug>",
  name: "debugger",
  subagent_type: "man:bang-thong",
  prompt: "You are bang-thong, the debugger. Check TaskList for your assigned task.\n\nBug: <description>\nError: <exact message>\nRelevant files: <paths>\n\n1. Read the code and reproduce the failure mentally\n2. Identify root cause (do NOT guess — trace the evidence)\n3. Write the fix\n4. Run tests to verify\n5. Mark your task DONE via TaskUpdate with: root cause summary + files changed\n\nDo NOT make unrelated changes."
})
TaskUpdate({ id: "1", owner: "debugger" })
```

**Teammate 2 — Reviewer (spawn after debugger task DONE — spawn on unblock):**

```
Agent({
  team_name: "fix-<bug-slug>",
  name: "reviewer",
  subagent_type: "man:phap-chinh",
  prompt: "You are phap-chinh, the code reviewer. Check TaskList for your assigned task.\n\nReview the fix made by debugger for: <bug summary>\nFiles changed: <from debugger's task completion summary>\n\n1. Read the fix\n2. Check: correctness, edge cases, test coverage, regressions\n3. Mark your task DONE via TaskUpdate with: APPROVE or list of issues\n\nIf issues found, SendMessage to debugger with exactly what must change."
})
TaskUpdate({ id: "2", owner: "reviewer" })
```

## Step 4 — Monitor and coordinate

- Messages arrive automatically from teammates — no polling needed
- Check progress via TaskList
- If reviewer finds issues: reviewer SendMessages debugger directly, or lead relays via:
  ```
  SendMessage({
    to: "debugger",
    summary: "Review findings — fix needed",
    message: "<specific issues from reviewer>"
  })
  ```
- When both tasks DONE: synthesize findings

## Step 5 — Wrap up

1. Print root cause + fix summary
2. Ask user to confirm before committing
3. Shut down teammates:
   ```
   SendMessage({ to: "debugger", message: { type: "shutdown_request" } })
   SendMessage({ to: "reviewer", message: { type: "shutdown_request" } })
   ```
4. Run tests one final time

## Fallback

If `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` not enabled or user declines team: dispatch single `man:bang-thong` subagent instead (fire-and-forget mode).
