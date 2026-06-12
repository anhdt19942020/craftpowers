## Lead Loop (Full)

The lead is not a passive coordinator. Run this loop until Definition of Done:

```
1. PLAN
   - TaskCreate for every known work item
   - TaskUpdate({ addBlockedBy }) to encode dependencies
   - Decide topology (hub-and-spoke by default, see ## Messaging Topology)

2. SPAWN (spawn-on-unblock — never spawn blocked teammates)
   - For each task with no blockedBy and no owner: spawn one teammate
   - Set teammate prompt: role + task ref + minimum context (persona auto-loads Team Mode)

3. MONITOR (every coordination round)
   - Process incoming teammate messages (auto-delivered between turns)
   - TaskList to see status drift
   - If a teammate has been silent for >3 rounds since last message: nudge (see ## Failure & Timeout Policy)

4. COORDINATE
   - Relay reviewer findings to implementer (hub-and-spoke)
   - SendMessage to unblock, share contracts, redirect scope
   - When a previously-blocked task is now unblocked: SPAWN its owner

5. SYNTHESIZE
   - Read shared artifacts (.team/<team-name>/*) when handoffs happen
   - Keep a running mental model of who owns what and what's done

6. REFLECT (metacognition checkpoint)
   - After every 3 completed tasks, or after any task with 2+ review rejections
   - Evaluate: are completed tasks achieving the plan's intent? Is confidence trending down?
   - If reflection flags REPLAN_TASK: update task spec, re-dispatch teammate
   - If reflection flags REPLAN_PHASE: STOP, present findings to human partner, wait for revised plan
   - Track confidence scores across tasks — 3 consecutive declining scores triggers phase replan

7. GATE — check ## Definition of Done before shutdown

8. CEO REVIEW (advisory gate)
   - Spawn `man:final-approver` as fire-and-forget subagent (NOT a teammate — no TeamCreate needed)
   - Prompt must include: (a) the original plan/goal OR path to plan file if exists, (b) your synthesis, (c) TaskList summary, (d) path to any `.team/` artifacts
   - Wait for final-approver's verdict: APPROVE or FLAG
   - Append CEO verdict to your final user summary verbatim — do not paraphrase or filter
   - If FLAG: include the flagged concerns in your summary. The human partner decides whether to rework — you do not re-dispatch teammates based on CEO feedback alone
   - **Skip CEO review when:** team had only 1 teammate AND task was a quick fix (< 3 tasks). The overhead isn't justified for trivial runs.

   ```
   Agent({
     subagent_type: "man:final-approver",
     prompt: "Review this team run as final approver.\n\nPlan: <path to docs/mankit/plans/*.md if present, else 'no formal plan'>\n\nOriginal goal: <goal>\n\nLeader synthesis: <synthesis>\n\nTask summary:\n<TaskList dump>\n\nArtifacts: <paths>\n\nIssue your verdict: APPROVE or FLAG."
   })
   ```

8. PERSIST STATE (after each task completion)
   - Write `.team/<team-name>/plan-state.yaml` with current state
   - This allows any new session to resume the team's work if session dies
   - Format:

   ```yaml
   plan: docs/mankit/plans/<plan-file>.md
   team: <team-name>
   branch: <branch-name>
   updated: <ISO timestamp>
   tasks:
     - id: 1
       subject: "<task subject>"
       status: completed
       owner: backend
       summary: "<one-line what was done>"
     - id: 2
       subject: "<task subject>"
       status: in_progress
       owner: frontend
       summary: null
     - id: 3
       subject: "<task subject>"
       status: pending
       owner: null
       blocked_by: [1, 2]
       summary: null
   decisions:
     - "reviewer said use interface X instead of Y (task 1 review)"
   ```

   Update this file every time a task transitions to `completed` or `in_progress`. On session resume, read this file to restore team state without re-planning.

9. SHUTDOWN
   - SendMessage({ to: <each teammate>, message: { type: "shutdown_request" } })
   - Run final verification (tests, build)
   - Final `plan-state.yaml` update with all tasks completed
   - Report synthesis + CEO verdict to user; ask before TeamDelete
```

**Coordination round cap:** `max_coordination_rounds = 10`. A round = one cycle of MONITOR→COORDINATE→REFLECT→SPAWN. If the team has not progressed (no task transition to `completed`) for 10 rounds, **stop and escalate to the human partner** — the team is stuck or the plan is wrong.
