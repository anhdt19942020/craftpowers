# Agent Teams Native API Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use man:subagent-driven-development (recommended) or man:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the agent-teams skill to programmatically use Claude Code's native Agent Teams API (TeamCreate, SendMessage, shared TaskCreate) instead of fire-and-forget subagent dispatch.

**Architecture:** Three skills need updates: `agent-teams` (core workflow with TeamCreate/SendMessage), `writing-plans` (execution handoff references), and `subagent-driven-development` (add real Team mode alongside existing fire-and-forget). The agent-teams skill becomes the authoritative reference for the programmatic team workflow. Version bump to 6.11.0 (new feature).

**Tech Stack:** Markdown skills, Claude Code Agent Teams API (TeamCreate, SendMessage, TaskCreate, TaskUpdate, TaskList)

---

## File Structure

| File | Responsibility |
|------|---------------|
| `skills/agent-teams/SKILL.md` | Core team workflow — TeamCreate, SendMessage, shared TaskList patterns |
| `skills/writing-plans/SKILL.md` | Execution handoff — reference agent-teams for Team Agents option |
| `skills/subagent-driven-development/SKILL.md` | Add "Native Team" dispatch mode using real Agent Teams API |

---

### Task 1: Rewrite agent-teams SKILL.md with programmatic TeamCreate/SendMessage workflow

**Files:**
- Modify: `skills/agent-teams/SKILL.md:1-174`

The current skill describes the concept but contains zero programmatic API calls. Rewrite to include the actual TeamCreate → TaskCreate → Agent(team_name) → SendMessage workflow while preserving the existing decision logic, cost awareness, and common mistakes sections.

- [ ] **Step 1: Read current agent-teams skill**

```bash
cat skills/agent-teams/SKILL.md
```

Confirm current content matches what we analyzed (174 lines, no TeamCreate/SendMessage references).

- [ ] **Step 2: Rewrite the skill with programmatic workflow**

Replace the entire SKILL.md content. Key changes:

**Keep unchanged:**
- Frontmatter (name, description, phase)
- Overview section (core principle)
- Proactive Trigger section (pattern recognition table)
- When to Use decision graph
- Cost Awareness section
- Limitations section

**Replace "Setup" section** with:

```markdown
## Setup

Enable in your project or user settings:

```json
// .claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Optionally configure in `~/.claude.json`:

```json
{
  "teammateDefaultModel": "sonnet",
  "teammateMode": "inProcess"
}
```
```

**Replace "Prompt Patterns" section** with new "Team Workflow" section:

```markdown
## Team Workflow

### Step 1: Create Team

```
TeamCreate({
  team_name: "feature-profile",
  description: "Implement user profile feature"
})
```

### Step 2: Create Shared Tasks

```
TaskCreate({
  subject: "Build API endpoints",
  description: "Create GET/POST /api/profile endpoints..."
})
TaskCreate({
  subject: "Build React components",
  description: "Create ProfilePage, ProfileForm components..."
})
TaskCreate({
  subject: "Write integration tests",
  description: "Test API + UI integration..."
})
```

Use TaskUpdate to set dependencies:
```
TaskUpdate({ id: 3, blockedBy: [1, 2] })
```

### Step 3: Spawn Teammates

Each teammate is a full Claude Code session. Use tam quốc agents:

```
Agent({
  team_name: "feature-profile",
  name: "backend",
  subagent_type: "man:trieu-van",
  prompt: "You are the backend implementer. Check TaskList for tasks assigned to you. Complete each task, mark DONE via TaskUpdate, then check for more work."
})

Agent({
  team_name: "feature-profile",
  name: "frontend",
  subagent_type: "man:trieu-van",
  prompt: "You are the frontend implementer. Check TaskList for tasks assigned to you. Complete each task, mark DONE via TaskUpdate, then check for more work."
})

Agent({
  team_name: "feature-profile",
  name: "reviewer",
  subagent_type: "man:phap-chinh",
  prompt: "You are the code reviewer. Watch TaskList. When implementation tasks complete, review the changes and report findings via SendMessage to the lead."
})
```

Assign tasks to teammates:
```
TaskUpdate({ id: 1, owner: "backend" })
TaskUpdate({ id: 2, owner: "frontend" })
```

### Step 4: Monitor & Coordinate

As lead, you:
- Receive messages automatically from teammates (no polling needed)
- Use SendMessage to redirect, unblock, or assign new work:

```
SendMessage({
  to: "frontend",
  summary: "API contract ready",
  message: "Backend finished the API. Endpoints: GET /api/profile, POST /api/profile. Schema: { name: string, email: string, avatar_url: string }. You can start integration now."
})
```

- Check progress via TaskList
- If reviewer finds issues:

```
SendMessage({
  to: "backend",
  summary: "Fix review findings",
  message: "Reviewer found SQL injection in profile update endpoint. Use parameterized queries instead of string interpolation. See task #4 for details."
})
```

### Step 5: Shutdown

When all tasks complete:

```
SendMessage({
  to: "backend",
  message: { type: "shutdown_request" }
})
SendMessage({
  to: "frontend",
  message: { type: "shutdown_request" }
})
SendMessage({
  to: "reviewer",
  message: { type: "shutdown_request" }
})
```

Run final test suite, ask user to commit.
```

**Replace "Controls Quick Reference" section** with:

```markdown
## Lead Responsibilities

| Responsibility | How |
|----------------|-----|
| Create team | `TeamCreate({ team_name, description })` |
| Define work | `TaskCreate` for each task, `TaskUpdate` for dependencies |
| Spawn teammates | `Agent({ team_name, name, subagent_type, prompt })` |
| Assign tasks | `TaskUpdate({ id, owner: "teammate-name" })` |
| Monitor progress | `TaskList` — check periodically |
| Coordinate | `SendMessage` to redirect, unblock, share findings |
| Handle idle | Teammates go idle after each turn — normal. SendMessage wakes them |
| Shutdown | `SendMessage({ message: { type: "shutdown_request" } })` to each |
```

**Add new "Coordination Patterns" section** after Lead Responsibilities:

```markdown
## Coordination Patterns

### Cross-Layer Feature (frontend + backend + tests)

```
TeamCreate({ team_name: "feature-X" })

# Create tasks with dependencies
TaskCreate({ subject: "Define API contract" })           # Task 1
TaskCreate({ subject: "Implement backend endpoints" })    # Task 2
TaskCreate({ subject: "Implement frontend components" })  # Task 3
TaskCreate({ subject: "Write integration tests" })        # Task 4
TaskUpdate({ id: 2, blockedBy: [1] })
TaskUpdate({ id: 3, blockedBy: [1] })
TaskUpdate({ id: 4, blockedBy: [2, 3] })

# Spawn — lead handles Task 1 (API contract), then assigns
Agent({ team_name: "feature-X", name: "backend", subagent_type: "man:trieu-van", ... })
Agent({ team_name: "feature-X", name: "frontend", subagent_type: "man:trieu-van", ... })
Agent({ team_name: "feature-X", name: "tester", subagent_type: "man:hoang-trung", ... })
```

### Multi-Perspective Review

```
TeamCreate({ team_name: "review-PR-42" })

TaskCreate({ subject: "Security review" })
TaskCreate({ subject: "Performance review" })
TaskCreate({ subject: "Coverage review" })

Agent({ team_name: "review-PR-42", name: "security", subagent_type: "man:tu-ma-y", ... })
Agent({ team_name: "review-PR-42", name: "perf", subagent_type: "man:phap-chinh", ... })
Agent({ team_name: "review-PR-42", name: "coverage", subagent_type: "man:hoang-trung", ... })
```

### Competing-Hypothesis Debug

```
TeamCreate({ team_name: "debug-checkout" })

TaskCreate({ subject: "Investigate race condition in cart state" })
TaskCreate({ subject: "Investigate API timeout/retry behavior" })
TaskCreate({ subject: "Investigate DB connection pool exhaustion" })

# All bang-thong agents — each investigates one hypothesis
Agent({ team_name: "debug-checkout", name: "hyp-race", subagent_type: "man:bang-thong", ... })
Agent({ team_name: "debug-checkout", name: "hyp-timeout", subagent_type: "man:bang-thong", ... })
Agent({ team_name: "debug-checkout", name: "hyp-pool", subagent_type: "man:bang-thong", ... })
```

**Keep Common Mistakes table** but add one row:

```markdown
| Not using TaskUpdate for dependencies | Tasks execute out of order — use `blockedBy` |
```

**Keep Limitations section** unchanged.

- [ ] **Step 3: Verify the rewritten skill**

Read the file back, confirm:
- Frontmatter preserved
- TeamCreate/SendMessage/TaskCreate used programmatically
- All 3 coordination patterns present
- Cost awareness preserved
- Common mistakes preserved + new row
- No placeholder text

- [ ] **Step 4: Commit**

```bash
git add skills/agent-teams/SKILL.md
git commit -m "feat(agent-teams): wire to native TeamCreate/SendMessage/TaskCreate API"
```

---

### Task 2: Update writing-plans Execution Handoff to reference programmatic team workflow

**Files:**
- Modify: `skills/writing-plans/SKILL.md:205-235`

The "If Team Agents chosen" section currently describes a manual Ctrl+T UI flow. Replace with programmatic TeamCreate/SendMessage workflow that references agent-teams skill.

- [ ] **Step 1: Read current handoff section**

```bash
cat skills/writing-plans/SKILL.md
```

Focus on lines 205-235 — "If Team Agents chosen" block.

- [ ] **Step 2: Replace the Team Agents handoff block**

Replace lines 205-235 with:

```markdown
**If Team Agents chosen:**

You are the **team lead**. Use the native Agent Teams API. Follow this exact sequence:

1. **Create team** — name derived from plan:
   ```
   TeamCreate({
     team_name: "<feature-name>",
     description: "Implement <plan goal>"
   })
   ```

2. **Create shared task list** — convert every plan task to a TaskCreate call with owner:
   ```
   TaskCreate({ subject: "Task 1: <name>", description: "<full task spec from plan>" })
   TaskCreate({ subject: "Task 2: <name>", description: "<full task spec from plan>" })
   ...
   ```
   Set dependencies with TaskUpdate:
   ```
   TaskUpdate({ id: 2, blockedBy: [1] })  // if Task 2 depends on Task 1
   ```

3. **Spawn teammates** based on task types present in the plan:
   - Has implementation tasks → spawn `man:trieu-van` teammate
   - Has test tasks → spawn `man:hoang-trung` teammate
   - Has debug tasks → spawn `man:bang-thong` teammate
   - Always spawn `man:phap-chinh` for final review

   ```
   Agent({
     team_name: "<feature-name>",
     name: "implementer",
     subagent_type: "man:trieu-van",
     prompt: "You are triệu-vân, the implementer. Check TaskList for tasks assigned to you. For each: read the task description (contains full spec), implement with TDD, mark DONE via TaskUpdate, then check for more work."
   })
   ```

4. **Assign tasks** to teammates:
   ```
   TaskUpdate({ id: 1, owner: "implementer" })
   TaskUpdate({ id: 2, owner: "tester" })
   ```

5. **Monitor & coordinate** — messages arrive automatically. Use SendMessage to:
   - Share context between teammates when tasks have cross-dependencies
   - Redirect reviewer findings to the implementer
   - Unblock teammates waiting on information

6. **Wrap up** — when all tasks DONE:
   - SendMessage shutdown to all teammates
   - Run full test suite
   - Ask user to commit

**Full reference:** See man:agent-teams for the complete Team Workflow, Coordination Patterns, and Lead Responsibilities.
```

- [ ] **Step 3: Verify the updated skill**

Read back, confirm:
- TeamCreate/TaskCreate/SendMessage used
- References man:agent-teams for full docs
- tam quốc agents dispatched with man: prefix
- No Ctrl+T UI references remain

- [ ] **Step 4: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat(writing-plans): update Team Agents handoff to use native API"
```

---

### Task 3: Add Native Team dispatch mode to subagent-driven-development

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md:19-47`

The "Team Agents (recommended)" section currently dispatches tam quốc agents as fire-and-forget subagents. Add a note clarifying two modes: fire-and-forget (current) vs native team (coordinated).

- [ ] **Step 1: Read current dispatch modes section**

```bash
cat skills/subagent-driven-development/SKILL.md
```

Focus on lines 15-47 — Dispatch Modes section.

- [ ] **Step 2: Update the Dispatch Modes section**

Replace lines 15-47 with:

```markdown
## Dispatch Modes

This skill supports three dispatch modes. The mode is chosen during the Execution Handoff in writing-plans.

### Team Agents — Native Team (recommended for coordinated work)

Use when tasks have cross-dependencies, need inter-agent communication, or span multiple layers.

Creates a real Agent Team using TeamCreate/SendMessage/shared TaskList. Teammates are persistent sessions that coordinate through the shared task list and direct messages.

**REQUIRED SUB-SKILL:** Use man:agent-teams for the full Team Workflow.

| Task Type | subagent_type | Agent | Model |
|-----------|--------------|-------|-------|
| Implement | `man:trieu-van` | triệu-vân | Sonnet |
| Debug | `man:bang-thong` | bàng-thống | Opus |
| Code review | `man:phap-chinh` | pháp-chính | Opus |
| Security review | `man:tu-ma-y` | tư-mã-ý | Opus |
| Explore codebase | `man:gia-cat-luong` | gia-cát-lượng | Sonnet |
| Quick fix | `man:truong-phi` | trương-phi | Sonnet |
| Tests | `man:hoang-trung` | hoàng-trung | Sonnet |
| Docs | `man:ma-luong` | mã-lương | Sonnet |
| Journal | `man:quan-vu` | quan-vũ | Sonnet |
| Release | `man:luu-bi` | lưu-bị | Opus |

**Cost:** ~3-4x single session (persistent teammates). Use only when coordination justifies cost.

### Team Agents — Fire-and-Forget (recommended for independent tasks)

Same tam quốc agents, but dispatched as independent subagents via `Agent(subagent_type="man:...")`. No TeamCreate, no SendMessage, no shared TaskList. Each agent runs in isolation, returns result, and exits.

**Use this when:** Tasks are independent — no inter-agent communication needed.

**IMPORTANT:** Always use `man:` prefix (e.g., `subagent_type: "man:trieu-van"`). Without prefix, plugins like cavecrew may intercept the dispatch.

**Plugins are tools, not agents.** Cavecrew, context-mode, and other plugins provide supporting capabilities (compressed output, context management, etc.) that team agents can leverage. They do not replace team agents.

### Generic Subagent

Dispatch using generic `subagent_type` without `man:` prefix. Useful when no specialized agent exists for the task.

### Inline Execution

No subagent dispatch. Execute in current session using man:executing-plans.
```

- [ ] **Step 3: Verify the updated skill**

Read back, confirm:
- Two Team Agents sub-modes clearly distinguished
- Native Team references man:agent-teams
- Fire-and-Forget preserves current behavior
- Agent table preserved
- man: prefix warning preserved

- [ ] **Step 4: Commit**

```bash
git add skills/subagent-driven-development/SKILL.md
git commit -m "feat(sdd): split Team Agents into Native Team vs Fire-and-Forget modes"
```

---

### Task 4: Bump version to 6.11.0

**Files:**
- Run: `bash scripts/bump-version.sh 6.11.0`

New feature (native Agent Teams API integration) → minor bump.

- [ ] **Step 1: Run bump script**

```bash
bash scripts/bump-version.sh 6.11.0
```

If `jq` not available on Windows, manually update all 5 files:
- `package.json`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.cursor-plugin/plugin.json`
- `gemini-extension.json`

- [ ] **Step 2: Verify version consistency**

```bash
bash scripts/bump-version.sh --check
```

Or manually grep:
```bash
grep -r "6.11.0" package.json .claude-plugin/ .cursor-plugin/ gemini-extension.json
```

- [ ] **Step 3: Commit**

```bash
git add package.json .claude-plugin/ .cursor-plugin/ gemini-extension.json
git commit -m "feat: bump version to 6.11.0 — native Agent Teams API"
```

---

## Self-Review

**Spec coverage:**
- ✅ TeamCreate programmatic usage → Task 1 (agent-teams skill)
- ✅ SendMessage inter-agent communication → Task 1 (coordination patterns)
- ✅ Shared TaskCreate/TaskList → Task 1 (team workflow steps 2-4)
- ✅ writing-plans handoff updated → Task 2
- ✅ subagent-driven-development modes clarified → Task 3
- ✅ Version bump → Task 4

**Placeholder scan:** No TBD/TODO/placeholders found.

**Type consistency:** TeamCreate, SendMessage, TaskCreate, TaskUpdate, TaskList — consistent naming across all 3 skills.
