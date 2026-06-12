> **SUPERSEDED** — Agents referenced in this doc were merged into Tam Quoc personas (commit c301afc). This document is kept for historical reference only.

---

# Three Subagents for Solo Fullstack Workflow — Design

**Date:** 2026-05-07
**Status:** Draft (pending user review)
**Scope:** Add 3 subagents to mankit plugin to fill gaps in solo fullstack workflow.
**Plugin version:** 6.0.0 → 6.1.0

---

## Background

User proposed 7 subagents for solo fullstack dev workflow:
spec-writer, codebase-explorer, implementer, code-reviewer, test-writer, debugger, release-prep.

Audit of current mankit plugin (5 agents, 25 skills, 6 commands) shows 4 of 7 already
covered:
- spec-writer → `writing-plans` + `to-prd` + `to-issues` + `brainstorming` + `/man-plan`
- code-reviewer → `agents/code-reviewer.md` + `requesting-code-review` skill
- test-writer → `agents/test-engineer.md` + `test-driven-development` skill
- debugger → `agents/debugger.md` + `systematic-debugging` skill

Three gaps remain:
1. **codebase-explorer** — no read-only repo scout
2. **implementer** — prompt exists in `subagent-driven-development`, not registered as agent
3. **release-prep** — `finishing-a-development-branch` covers branch close, not deploy artifacts

This spec adds those three, in hybrid form (agent + skill where checklist depth warrants).

---

## Workflow Integration

```
/man-brainstorm
    ↓
/man-explore           ← NEW: codebase-explorer agent (read-only scout)
    ↓
/man-plan              ← writing-plans skill consumes explorer output
    ↓
executing-plans
    ├─ dispatch implementer per task   ← NEW: implementer agent
    ├─ code-reviewer                   ← existing
    ├─ secure-reviewer                 ← existing
    └─ test-engineer                   ← existing
    ↓
/man-fix (if needed)
    ↓
/man-release           ← NEW: release-prep skill (pre-deploy audit)
    ↓
/man-ship              ← finishing-a-development-branch
```

---

## File Layout

```
agents/
  codebase-explorer.md         NEW
  implementer.md               NEW
  release-prep.md              NEW
skills/
  release-prep/
    SKILL.md                   NEW
    rules/
      node.md                  NEW
      python.md                NEW
      migrations.md            NEW
      docker.md                NEW
commands/
  man-explore.md               NEW
  man-release.md               NEW
.claude-plugin/
  plugin.json                  bump 6.0.0 → 6.1.0
  marketplace.json             bump 6.0.0 → 6.1.0
```

7 new files, 2 version bumps. No existing file rewrites; only additive notes appended
to `writing-plans/SKILL.md`, `subagent-driven-development/SKILL.md`, and
`finishing-a-development-branch/SKILL.md`.

---

## Component 1: codebase-explorer agent

**File:** `agents/codebase-explorer.md`

**Frontmatter:**
```yaml
name: codebase-explorer
description: Read-only repo scout. Maps files, patterns, conventions, and duplicate
              risks for a feature before implementation. Returns file:line table.
              Use BEFORE writing-plans on any non-trivial feature.
tools: Read, Grep, Glob, Bash
model: sonnet
```

**Bash whitelist:** `git log`, `git blame`, `ls`, `find` only. No edit, no run.

**Workflow:**
1. Read CLAUDE.md, AGENTS.md to learn project conventions.
2. Glob candidate files by feature keywords.
3. Grep symbols/patterns related to the feature.
4. Detect conventions: naming style, error handling style, folder structure, test
   colocation pattern.
5. Flag duplicates: existing utils, helpers with same name, similar features.
6. Return compressed file:line table.

**Output contract:**
```
## Touch points
<path>:<line>    <description>
...

## Conventions
- Naming: ...
- Errors: ...
- Tests: ...

## Duplicate risk
<path>:<line> — <reason DON'T duplicate>
```

**Hard refusal:** Never proposes fixes. Never edits. Read-only.

**Distinction from built-in `Explore` / `general-purpose`:** project-aware (reads
CLAUDE.md), output format optimized for `writing-plans` consumption.

---

## Component 2: implementer agent

**File:** `agents/implementer.md`

**Frontmatter:**
```yaml
name: implementer
description: Implements ONE task from a plan. Reads task spec + project conventions,
              writes code, runs tests, returns diff summary. Dispatched per-task by
              executing-plans / subagent-driven-development.
tools: Read, Edit, Write, Glob, Grep, Bash
model: sonnet
```

**Source prompt:** wrap existing
`skills/subagent-driven-development/implementer-prompt.md` content into agent file.
Append:
- Read CLAUDE.md, AGENTS.md, codebase-explorer output (if provided) before edit.
- TDD by default per `test-driven-development` skill: test first, then code.
- Run tests after each edit, fix on failure.
- Refuse scope creep: stick to assigned task; flag related issues for main thread.

**Input contract:**
```
Task: <id> — <title>
Spec: <link to plan section>
Touch points: <from codebase-explorer, optional>
Acceptance: <test command + expected result>
```

**Output contract:**
```
## Diff
<file>: +<n>/-<n>
...

## Test
<command>: PASS | FAIL

## Followups
- <related issue out of scope, if any>
```

**Refusal triggers:**
- Task spans >2 unrelated files
- Scope ambiguous → escalate to main

**Distinction from main Claude:** isolated context (no main-thread tool noise);
parallelizable across independent tasks.

---

## Component 3: release-prep agent + skill

### Agent dispatcher

**File:** `agents/release-prep.md`

**Frontmatter:**
```yaml
name: release-prep
description: Pre-deploy gate. Audits env vars, migrations, breaking changes; drafts
              changelog from git diff. Detects stack, applies matching rules. Run
              after tests pass, before /man-ship.
tools: Read, Grep, Glob, Bash
model: sonnet
```

**Bash whitelist:** `git log`, `git diff`, `git status`, `ls`, `find`, lock-file
read commands. No deploy, no push, no edit.

The agent reads stack-detection signals, then loads matching rule files from
`skills/release-prep/rules/`.

### Skill checklist

**File:** `skills/release-prep/SKILL.md`

**Workflow:**
1. Detect stack (parallel):
   - `package.json` present → node
   - `requirements.txt` or `pyproject.toml` → python
   - `prisma/`, `drizzle/`, `migrations/`, `alembic/` → migrations
   - `Dockerfile` or `docker-compose.yml` → docker
2. Load matching `rules/*.md` files.
3. Run checklist per rule.
4. Aggregate report.

### Per-stack rules

**`rules/node.md`:**
- New `process.env.X` reads in diff → confirm key exists in `.env.example`
- `package.json` deps changed → `package-lock.json` updated
- Build script passes locally
- Breaking TypeScript type exports → flag consumer impact

**`rules/python.md`:**
- New env reads → in `.env.example` or settings module
- `requirements.txt` / `pyproject.toml` lock updated
- Pydantic schema breaking change → flag

**`rules/migrations.md`:**
- New migration → reversible (has `down`)
- Destructive change (DROP, ALTER NOT NULL) → warn
- Migration order conflict with main branch

**`rules/docker.md`:**
- Dockerfile changed → image tag bump
- Compose service env additions → `.env.example` sync
- Multi-stage build cache layer optimal

### Output

```
## Pre-Ship Report

### Pass (n)
- ...

### Warning (n)
- ...

### Block (n)
- ...

### Changelog draft
<from `git log main..HEAD`, grouped by conventional-commit type>
```

**Refusal:** Never deploys, never pushes. Read-only audit.

---

## Commands

### `commands/man-explore.md`

```markdown
---
description: "Scan codebase for files, patterns, and conventions touched by a feature.
              Read-only. Run before /man-plan."
---
Invoke the `codebase-explorer` agent with the user's feature description as input.
Report the file:line table, conventions, and duplicate-risk warnings exactly as
returned. Do NOT propose code changes.
```

### `commands/man-release.md`

```markdown
---
description: "Pre-deploy audit: env vars, migrations, breaking changes, changelog.
              Run after tests pass, before /man-ship."
---
Invoke the `release-prep` skill. Report the pre-ship report verbatim. If any
block items appear, tell the user to fix before /man-ship.
```

---

## Skill touch-ups (additive, no rewrites)

- `skills/writing-plans/SKILL.md` — note: "If codebase-explorer output exists,
  reference its file:line table when listing affected files."
- `skills/subagent-driven-development/SKILL.md` — note: "Dispatch the
  `implementer` agent per independent task instead of inline implementation."
- `skills/finishing-a-development-branch/SKILL.md` — note: "Run /man-release first
  if not already done."

---

## Versioning

- `.claude-plugin/plugin.json` version `6.0.0` → `6.1.0`
- `.claude-plugin/marketplace.json` version `6.0.0` → `6.1.0`
- Commit message: `feat: add codebase-explorer, implementer, release-prep subagents`

After push, refresh:
```
/plugin marketplace update craftpowers-dev
/plugin install mankit@craftpowers-dev
/reload-plugins
```

---

## Testing strategy

- Manual smoke test each agent against a sample feature in this repo:
  - codebase-explorer: ask it to scout "add a new command for /man-status"
  - implementer: feed it one task from an existing plan
  - release-prep: run on this commit (multi-file change)
- Verify install: fresh marketplace update + reinstall.

---

## Out of scope (YAGNI)

- Frontend visual verification agent
- Monitoring/observability post-deploy checks
- Slack/email notification on release-prep block
- Auto-fix of release-prep block items
- Stack support beyond Node, Python, migrations, Docker (Go/Rust/Ruby etc.)

These can be added incrementally if real demand appears. No speculative
implementation.

---

## Acceptance criteria

- 7 new files exist in repo
- Plugin installs cleanly via marketplace, no manifest errors
- `/man-explore`, `/man-release` appear in slash command list
- 3 new agents appear when listing subagents
- Smoke test of each agent returns sane output on this repo
- Existing 6 `/man-*` commands continue to work unchanged
