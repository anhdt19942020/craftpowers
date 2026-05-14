---
description: "Debug and fix a bug, test failure, or unexpected behavior. Uses Agent Teams — lead coordinates bang-thong + phap-chinh. Supports competing-hypothesis mode for complex multi-cause bugs."
---

You are the **team lead**. Do not delegate this role.

## Step 1 — Triage

Read the bug description (everything after `/man-fix`). Count signals of multi-cause complexity:

- "intermittent", "sometimes", "flaky", "race"
- "not sure why", "could be X or Y", multiple possible causes named
- "fix didn't work", "regression after fix", "tried N things"
- spans 3+ files or 2+ subsystems (frontend + backend, app + DB, etc.)
- bug has been open >7 days

Classify:

| Class | Criteria | Workflow |
|---|---|---|
| **Simple** | single file, clear error, obvious cause, 0 signals | skip Agent Teams — fix directly in this session |
| **Complex (single hypothesis)** | unclear cause but only 1 signal | 1×bang-thong + 1×phap-chinh team (Step 2a) |
| **Complex (competing-hypothesis)** | 2+ signals | 3×bang-thong + 1×phap-chinh team (Step 2b) |

If 5+ signals: ASK the human partner before spawning — escalation per `## Failure & Timeout Policy` in agent-teams skill.

Tell the user the chosen mode:
- single: "Complex bug — spawning bang-thong + phap-chinh."
- competing: "Multiple plausible causes — spawning 3 parallel bang-thong (hypotheses A/B/C). Winner-first; siblings shut down on confirmation."

## Step 2a — Single-hypothesis team (when 1 signal)

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

Then go to Step 3a.

## Step 2b — Competing-hypothesis team (when 2+ signals)

**Lead enumerates 3 ORTHOGONAL hypotheses BEFORE seeing repro logs.** Orthogonality rule: confirming one hypothesis must NOT increase the prior of another.

- Bad (not orthogonal): `H1 = race on cart state`, `H2 = race on checkout state` — both "race", one trace style.
- Good (orthogonal): `H1 = race condition`, `H2 = API timeout/retry`, `H3 = DB connection pool exhaustion` — different evidence, different traces, different fixes.

```
TeamCreate({
  team_name: "fix-<bug-slug>",
  description: "Competing-hypothesis debug: <bug summary>"
})

# One task per hypothesis. The review task is NOT created upfront — it gets created in Step 4 after a winner is declared (TaskUpdate has AND-semantics blockedBy, no OR).
TaskCreate({
  subject: "Hypothesis A: <name>",
  description: "Statement: <H>\nFiles to investigate: <list>\nConfirm if: <criteria>\nRule out if: <criteria>"
})
TaskCreate({
  subject: "Hypothesis B: <name>",
  description: "Statement: <H>\nFiles to investigate: <list>\nConfirm if: <criteria>\nRule out if: <criteria>"
})
TaskCreate({
  subject: "Hypothesis C: <name>",
  description: "Statement: <H>\nFiles to investigate: <list>\nConfirm if: <criteria>\nRule out if: <criteria>"
})
```

If debugger output exceeds ~500 tokens: write to `.team/fix-<bug-slug>/hyp-<name>.md`.

Then go to Step 3b.

## Step 3a — Spawn single-hypothesis teammates

**Debugger (spawn immediately):**

```
Agent({
  team_name: "fix-<bug-slug>",
  name: "debugger",
  subagent_type: "man:bang-thong",
  prompt: "Bug: <description>\nError: <exact message>\nRelevant files: <paths>\n\nClaim task #1. Report root cause + files changed via TaskUpdate completion summary. SendMessage lead when done."
})
TaskUpdate({ id: "1", owner: "debugger" })
```

**Reviewer (spawn after debugger task DONE — spawn on unblock):**

```
Agent({
  team_name: "fix-<bug-slug>",
  name: "reviewer",
  subagent_type: "man:phap-chinh",
  prompt: "Review fix made by debugger on task #1. Check correctness, edge cases, regressions. Claim task #2. If debugger's task summary references a `.team/<slug>/handoff.md` path, Read that file before reviewing. Report APPROVE or list of issues via TaskUpdate. SendMessage lead — not debugger directly."
})
TaskUpdate({ id: "2", owner: "reviewer" })
```

Then Step 4a.

## Step 3b — Spawn 3 hypothesis debuggers in parallel

All three spawn at once (no dependencies between hypotheses):

```
Agent({
  team_name: "fix-<bug-slug>", name: "hyp-A",
  subagent_type: "man:bang-thong",
  prompt: "You are investigating ONE specific hypothesis: <H1 statement>.\nFiles: <list>\nConfirm if: <criteria>\nRule out if: <criteria>\n\nDo NOT broaden scope. Do NOT investigate sibling hypotheses. Do NOT peer-DM other debuggers.\n\nIf you rule out: SendMessage lead 'RULED OUT: <reason>'. TaskUpdate completed with the same reason. Stop.\n\nIf you confirm: write reproducer + fix, run tests, TaskUpdate completed with 'CONFIRMED: <root cause + fix summary>'. SendMessage lead."
})
TaskUpdate({ id: "1", owner: "hyp-A" })

# Same shape for hyp-B (task #2) and hyp-C (task #3) with their own H statements.
```

The reviewer is NOT spawned yet — see Step 4b.

Then Step 4b.

## Step 4a — Monitor (single hypothesis)

Hub-and-spoke (see `## Messaging Topology` in agent-teams skill): reviewer reports to lead; lead relays to debugger — never reviewer→debugger direct. Messages arrive automatically — no polling needed.

If reviewer finds issues: `SendMessage({ to: "debugger", summary: "Review findings", message: "<issues>" })`

**Definition of Done gate** (before Step 5 — see `## Definition of Done` in agent-teams skill):
- Both tasks `status=completed`
- Reviewer summary states `APPROVE`
- Tests pass

If gate fails: relay issues to debugger, loop. Honor `max_coordination_rounds=10`.

## Step 4b — Monitor (competing hypothesis, winner-first)

Read incoming messages each coordination round.

**Winner-first protocol:**

1. **First CONFIRMED with reproducer wins.** When the first debugger reports CONFIRMED:
   - Do NOT immediately shut down siblings. Wait ONE more coordination round.
   - Reason: catch convergent-evidence case where the bug has multiple causes (e.g., race + retry amplification). If a second debugger also reports CONFIRMED within that round, the bug is multi-cause.
2. **After the wait round:**
   - Single winner: `SendMessage shutdown_request` to losers; record their RULED OUT reasons in the team's `.team/.../audit.md` for future reference.
   - Multiple winners (convergent): keep both winners alive; lead writes a synthesis task describing the combined fix needed.
3. **Spawn reviewer NOW** (not upfront — review needs the winner's task ID):
   ```
   TaskCreate({ subject: "Review fix from <winner-name>", description: "..." })
   TaskUpdate({ id: <review-id>, addBlockedBy: [<winner-task-id>] })
   Agent({ name: "reviewer", subagent_type: "man:phap-chinh", prompt: "..." })
   ```
4. **All 3 RULED OUT:** hypotheses were wrong. Stop. Ask the human partner for a new hypothesis set — do NOT silently spawn replacements.

**Coordination round cap:** 10. If no winner by round 10: escalate to human.

**Hub-and-spoke:** all debuggers and the reviewer report to lead. No peer DMs. Lead relays.

**Definition of Done gate** (same as single-hypothesis): all relevant tasks completed, reviewer APPROVE, tests pass.

## Step 5 — Wrap up

1. Print root cause + fix summary (include all confirmed hypotheses if convergent)
2. Ask user to confirm before committing
3. Shut down remaining teammates:
   ```
   SendMessage({ to: "<name>", message: { type: "shutdown_request" } })
   ```
4. Run tests one final time
5. TeamDelete

## Fallback

If `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` not enabled or user declines team: dispatch single `man:bang-thong` subagent instead (fire-and-forget mode). Competing-hypothesis mode is unavailable without Agent Teams.
