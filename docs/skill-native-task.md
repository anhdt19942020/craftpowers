# Claude Native Task Management in Mankit Skills

This document describes how Mankit skills use Claude Native Task Management to track progress, coordinate subagents, and manage complex workflows.

## Overview

Claude Code provides 4 native tools for in-session task management:

| Tool | Purpose |
|------|---------|
| `TaskCreate` | Create new task with metadata and dependencies |
| `TaskUpdate` | Update status, assign owner, set dependencies |
| `TaskGet` | Get full details of a task |
| `TaskList` | List all tasks with status and blockedBy |

**Important:** Tasks are **session-scoped** — they disappear when the session ends. Plan files (markdown with checkboxes) are the **persistent** layer.

## 3-Task Rule

| Task count | Create Tasks? | Reason |
|------------|--------------|--------|
| < 3 | No | Overhead exceeds benefit |
| ≥ 3 | Yes | Tracking is meaningful, supports parallel execution |

## Task Lifecycle

```
pending → in_progress → completed
```

- **pending**: Not yet started
- **in_progress**: Currently executing (only 1 task/agent at a time)
- **completed**: Done

## Hydration Pattern — Bridge Between Sessions

```
┌──────────────────┐  Hydrate   ┌───────────────────┐
│ Plan Files       │ ─────────► │ Claude Tasks      │
│ (persistent)     │            │ (session-scoped)  │
│ [ ] Phase 1      │            │ ◼ pending         │
│ [ ] Phase 2      │            │ ◼ pending         │
└──────────────────┘            └───────────────────┘
                                        │ Work
                                        ▼
┌──────────────────┐  Sync-back ┌───────────────────┐
│ Plan Files       │ ◄───────── │ Task Updates      │
│ (updated)        │            │ (completed)       │
│ [x] Phase 1      │            │ ✓ completed       │
│ [ ] Phase 2      │            │ ◼ in_progress     │
└──────────────────┘            └───────────────────┘
```

### Hydration (Session Start)

1. Read plan files: `plan.md` + `phase-XX-*.md`
2. Identify unchecked `[ ]` items = remaining work
3. `TaskCreate` per unchecked item with metadata
4. Set `addBlockedBy` dependency chains
5. Checked `[x]` items = done, skip

### Sync-Back (Session End)

1. Collect completed tasks (`TaskUpdate(status: "completed")`) + metadata (`phase`, `phaseFile`, `planDir`)
2. Sweep all `phase-XX-*.md` in plan
3. Reconcile/backfill: update `[ ]` → `[x]` for all completed items (not just current phase)
4. Update `plan.md` frontmatter status + progress table
5. If completed tasks cannot be mapped to phase files, report unresolved mappings before concluding done
6. Git commit to persist state transition

---

## Skills Using Task Management

### 1. Writing-Plans Skill (`man-plan`)

**When to create tasks:**
- Multi-phase feature (3+ phases)
- Complex dependencies between phases
- Plan will be executed by `executing-plans`

**Task Schema for Phase:**

```javascript
TaskCreate(
  subject: "Setup environment and dependencies",
  activeForm: "Setting up environment",
  description: "Install packages, configure env. See phase-01-setup.md",
  metadata: {
    phase: 1,
    priority: "P1",
    effort: "2h",
    planDir: "plans/260205-auth/",
    phaseFile: "phase-01-setup.md"
  }
)
```

**Task Schema for Critical Step:**

```javascript
TaskCreate(
  subject: "Implement OAuth2 token refresh",
  activeForm: "Implementing token refresh",
  description: "Handle token expiry, refresh flow, error recovery",
  metadata: {
    phase: 3,
    step: "3.4",
    priority: "P1",
    effort: "1.5h",
    planDir: "plans/260205-auth/",
    phaseFile: "phase-03-api.md",
    critical: true,
    riskLevel: "high"
  },
  addBlockedBy: ["{phase-2-task-id}"]
)
```

**Dependency Chains:**

```
Phase 1 (no blockers)              ← start here
Phase 2 (addBlockedBy: [P1-id])    ← auto-unblocked when P1 completes
Phase 3 (addBlockedBy: [P2-id])
Step 3.4 (addBlockedBy: [P2-id])   ← critical steps share phase dependency
```

---

### 2. Executing-Plans Skill (`man-execute`)

**Workflow Integration:**

**Step 2 Implementation:**
1. `TaskList()` — check existing tasks (hydrated by planning)
2. If tasks exist → pick them up, skip re-creation
3. If no tasks → read plan phases, `TaskCreate` for each unchecked item
4. `TaskUpdate(status: "in_progress")` when starting a task

**Step 3 Finalize:**
1. Sync checkboxes `[ ]` → `[x]` across all phase files, then update `plan.md`
2. `TaskUpdate` marks all session tasks complete after sync-back confirmation

**Same-Session Handoff:**
```
writing-plans hydrates tasks → tasks exist → executing-plans picks them up → skips re-creation
```

**Cross-Session Resume:**
```
new session → TaskList() empty → read plan files → re-hydrate from unchecked [ ] items
```

---

### 3. Systematic-Debugging Skill (`man-debug`)

**Task Schemas by Complexity:**

**Standard Workflow (6 steps):**

```javascript
TaskCreate(subject="Debug & investigate", metadata={step: 1})
TaskCreate(subject="Scout related code", metadata={step: 2})
TaskCreate(subject="Implement fix", metadata={step: 3}, addBlockedBy=[step1, step2])
TaskCreate(subject="Run tests", metadata={step: 4}, addBlockedBy=[step3])
TaskCreate(subject="Code review", metadata={step: 5}, addBlockedBy=[step4])
TaskCreate(subject="Finalize", metadata={step: 6}, addBlockedBy=[step5])
```

**Deep Workflow (8 steps):**

```javascript
TaskCreate(subject="Debug & investigate", metadata={step: 1, phase: "diagnose"})
TaskCreate(subject="Research solutions", metadata={step: 2, phase: "research"})
TaskCreate(subject="Brainstorm approaches", metadata={step: 3, phase: "design"}, addBlockedBy=[step2])
TaskCreate(subject="Create implementation plan", metadata={step: 4, phase: "design"}, addBlockedBy=[step3])
TaskCreate(subject="Implement fix", metadata={step: 5, phase: "implement"}, addBlockedBy=[step1, step4])
TaskCreate(subject="Run tests", metadata={step: 6, phase: "verify"}, addBlockedBy=[step5])
TaskCreate(subject="Code review", metadata={step: 7, phase: "verify"}, addBlockedBy=[step6])
TaskCreate(subject="Finalize & docs", metadata={step: 8, phase: "finalize"}, addBlockedBy=[step7])
```

**Parallel Issue Coordination:**

```javascript
// Issue A tree
TaskCreate(subject="[Issue A] Debug", metadata={issue: "A", step: 1})
TaskCreate(subject="[Issue A] Fix", metadata={issue: "A", step: 2}, addBlockedBy=[A-step1])
TaskCreate(subject="[Issue A] Verify", metadata={issue: "A", step: 3}, addBlockedBy=[A-step2])

// Issue B tree
TaskCreate(subject="[Issue B] Debug", metadata={issue: "B", step: 1})
TaskCreate(subject="[Issue B] Fix", metadata={issue: "B", step: 2}, addBlockedBy=[B-step1])
TaskCreate(subject="[Issue B] Verify", metadata={issue: "B", step: 3}, addBlockedBy=[B-step2])

// Final shared task
TaskCreate(subject="Integration verify", addBlockedBy=[A-step3, B-step3])
```

---

### 4. Debug-Flight-Recorder Skill (`man-trace`)

**Investigation Pipeline as Tasks:**

```javascript
TaskCreate(subject="Assess incident scope", metadata={debugStage: "assess"})
TaskCreate(subject="Collect logs and evidence", metadata={debugStage: "collect"}, addBlockedBy=[assess])
TaskCreate(subject="Analyze root cause", metadata={debugStage: "analyze"}, addBlockedBy=[collect])
TaskCreate(subject="Implement fix", metadata={debugStage: "fix"}, addBlockedBy=[analyze])
TaskCreate(subject="Verify fix resolves issue", metadata={debugStage: "verify"}, addBlockedBy=[fix])
```

**Parallel Evidence Collection:**

```javascript
// Parallel — no blockedBy between them
TaskCreate(subject="Collect CI/CD pipeline logs", metadata={source: "ci", agentIndex: 1})
TaskCreate(subject="Collect application server logs", metadata={source: "server", agentIndex: 2})
TaskCreate(subject="Query database for anomalies", metadata={source: "db", agentIndex: 3})

// Analyze blocks on ALL collection completing
TaskCreate(subject="Analyze root cause from collected evidence",
  addBlockedBy=["{ci-id}", "{server-id}", "{db-id}"])
```

---

### 5. Requesting-Code-Review Skill (`man-review`)

**Review Pipeline as Tasks:**

```javascript
TaskCreate(subject="Scout edge cases", metadata={reviewStage: "scout"})
TaskCreate(subject="Review implementation", metadata={reviewStage: "review"}, blockedBy=[scout])
TaskCreate(subject="Fix critical issues", metadata={reviewStage: "fix"}, blockedBy=[review])
TaskCreate(subject="Verify fixes pass", metadata={reviewStage: "verify"}, blockedBy=[fix])
```

**Parallel Review Coordination:**

```javascript
// No blockedBy between parallel reviews
TaskCreate(subject="Review backend auth changes",
  metadata={scope: "src/api/", agentIndex: 1, totalAgents: 2})
TaskCreate(subject="Review frontend auth UI",
  metadata={scope: "src/components/", agentIndex: 2, totalAgents: 2})

// Fix task blocks on BOTH completing
TaskCreate(subject="Fix all review issues",
  addBlockedBy=["{backend-review-id}", "{frontend-review-id}"])
```

**Re-Review Cycle:**

```javascript
TaskCreate(subject="Re-review after fixes",
  addBlockedBy=["{fix-task-id}"],
  metadata={reviewStage: "review", cycle: 2})
```

---

### 6. Subagent-Driven-Development Skill (`man-parallel`)

**When to create tasks:**
- ≤ 2 agents: Do not create (overhead > benefit)
- ≥ 3 agents: Create tasks (meaningful coordination)

**Task Schema:**

```javascript
TaskCreate(
  subject: "Implement {feature} in {directory}",
  activeForm: "Implementing {feature}",
  description: "Build {components} following {plan-phase}",
  metadata: {
    agentType: "implementer",
    scope: "src/auth/,src/middleware/",
    scale: 3,
    agentIndex: 1,                  // 1-indexed
    totalAgents: 3,
    worktree: ".worktrees/task-1",
    priority: "P1",
    effort: "2h"
  }
)
```

**Task Lifecycle:**

```
Step 1: TaskCreate per agent     → status: pending
Step 2: Before spawning agent    → TaskUpdate → status: in_progress
Step 3: Agent returns report     → TaskUpdate → status: completed
Step 3: Agent times out          → Keep in_progress, add error metadata
```

---

### 7. Agent-Teams Skill (`man-team`) — Agent Teams

**Tools API Surface:**

| Tool | Operation | Purpose |
|------|-----------|---------|
| TeammateTool | `spawnTeam` | Create team + task list |
| TeammateTool | `cleanup` | Remove team/task dirs |
| SendMessage | `message` | DM to one teammate |
| SendMessage | `broadcast` | Send to ALL teammates |
| SendMessage | `shutdown_request` | Ask teammate to exit |
| SendMessage | `plan_approval_response` | Lead approves/rejects plan |

**Task Fields:**

| Field | Purpose |
|-------|---------|
| `status` | `pending` → `in_progress` → `completed` |
| `owner` | Agent name assigned to task |
| `blocks` | Task IDs this task blocks |
| `blockedBy` | Task IDs that must complete first |
| `addBlocks` | Set blocking relations (write) |
| `addBlockedBy` | Set dependency relations (write) |
| `metadata` | Arbitrary key-value pairs |

**Hook Events:**
- **TaskCompleted**: Fires when teammate calls `TaskUpdate(status: "completed")`
- **TeammateIdle**: Fires after `SubagentStop` for team members

**Event Lifecycle:**
```
SubagentStart(worker) → TaskCompleted(task) → SubagentStop(worker) → TeammateIdle(worker)
```

---

## Best Practices

### Task Creation

1. **Create tasks BEFORE starting work** (upfront planning)
2. **Only 1 task `in_progress` per agent** at a time
3. **Mark complete IMMEDIATELY** after finishing (do not batch)
4. **Use metadata** for filtering: `{step, phase, issue, severity}`
5. **If task fails** → keep `in_progress`, create subtask for blocker

### Naming Conventions

**subject** (imperative): Action verb + deliverable, <60 chars
- "Setup database migrations"
- "Implement OAuth2 flow"
- "Create user profile endpoints"

**activeForm** (present continuous): Matches subject in -ing form
- "Setting up database"
- "Implementing OAuth2"
- "Creating user profile endpoints"

**description**: 1-2 sentences, concrete deliverables, reference phase file

### Required Metadata Fields

- `phase`: Phase number
- `priority`: P1/P2/P3
- `effort`: Estimated time
- `planDir`: Path to plan directory
- `phaseFile`: Phase file name

### Optional Metadata Fields

- `step`: Step within phase
- `critical`: Boolean for critical steps
- `riskLevel`: high/medium/low
- `dependencies`: Description
- `feature`: Feature name
- `owner`: Agent assignment

### Dependency Management

```javascript
// Forward references: "I need X done first"
addBlockedBy: ["{prior-task-id}"]

// Backward references: "X blocks these children"
addBlocks: ["{child-task-id}"]
```

### Error Handling

If `TaskCreate` fails:
1. Log warning
2. Continue with sequential execution
3. Tasks add visibility, not core functionality

---

## Subagent vs Agent Teams Comparison

| Aspect | Subagents | Agent Teams |
|--------|-----------|-------------|
| **Context** | Own window; results return to caller | Own window; fully independent |
| **Communication** | Report back to main agent only | Message each other directly |
| **Coordination** | Main agent manages all work | Shared task list, self-coordination |
| **Best for** | Focused tasks, result-only | Complex work requiring discussion |
| **Token cost** | Lower | Higher (each teammate = separate instance) |
| **Task persistence** | Session-scoped | Session-scoped with shared task list |

---

## Quality Check Output Format

```
✓ Hydrated [N] phase tasks + [M] critical step tasks with dependency chain
✓ Registered [N] subagent tasks (worktree isolation, SCALE=3)
✓ Registered [N] review tasks (scout → review → fix → verify chain)
✓ Step [N]: [status] - [metrics]
```

---

## Validation Rules

1. **Dependency chain has no cycles**
2. **All phases have corresponding tasks**
3. **Required metadata fields present**
4. **Task count matches unchecked `[ ]` items**
5. **If Task tool calls = 0 at end of workflow** → workflow INCOMPLETE
