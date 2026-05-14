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

If debugger output (diff, logs) exceeds ~500 tokens, debugger writes to `.team/fix-<bug-slug>/handoff.md` and references the path. See `## Shared Artifacts` in `skills/agent-teams/SKILL.md`.

## Step 3 — Spawn teammates

**Teammate 1 — Debugger (spawn immediately):**

```
Agent({
  team_name: "fix-<bug-slug>",
  name: "debugger",
  subagent_type: "man:bang-thong",
  prompt: "Bug: <description>\nError: <exact message>\nRelevant files: <paths>\n\nClaim task #1. Report root cause + files changed via TaskUpdate completion summary. SendMessage lead when done."
})
TaskUpdate({ id: "1", owner: "debugger" })
```

**Teammate 2 — Reviewer (spawn after debugger task DONE — spawn on unblock):**

```
Agent({
  team_name: "fix-<bug-slug>",
  name: "reviewer",
  subagent_type: "man:phap-chinh",
  prompt: "Review fix made by debugger on task #1. Check correctness, edge cases, regressions. Claim task #2. If debugger's task summary references a `.team/<slug>/handoff.md` path, Read that file before reviewing. Report APPROVE or list of issues via TaskUpdate. SendMessage lead — not debugger directly."
})
TaskUpdate({ id: "2", owner: "reviewer" })
```

## Step 4 — Monitor and coordinate

Hub-and-spoke (see `## Messaging Topology` in agent-teams skill): reviewer reports to lead; lead relays to debugger — never reviewer→debugger direct. Messages arrive automatically — no polling needed.

If reviewer finds issues: `SendMessage({ to: "debugger", summary: "Review findings", message: "<issues>" })`

**Definition of Done gate** (before Step 5 — see `## Definition of Done` in agent-teams skill):
- Both tasks `status=completed`
- Reviewer summary states `APPROVE`
- Tests pass

If gate fails: relay issues to debugger, loop. Honor `max_coordination_rounds=10`.

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
