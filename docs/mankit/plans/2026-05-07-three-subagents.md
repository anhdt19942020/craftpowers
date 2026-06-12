> **SUPERSEDED** — Agents referenced in this doc were merged into Tam Quoc personas (commit c301afc). This document is kept for historical reference only.

---

# Three Subagents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use man:subagent-driven-development (recommended) or man:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship mankit v6.1.0 with three new subagents — codebase-explorer, implementer, release-prep — plus matching skill, rules, and slash commands.

**Architecture:** Hybrid (agent + skill where checklist depth warrants). codebase-explorer and implementer are agent-only. release-prep is an agent dispatcher backed by a skill with per-stack rule files. Two new slash commands wire commands → agent/skill. Three existing skill READMEs get short additive notes pointing to the new agents.

**Tech Stack:** Markdown (agent + skill files), YAML frontmatter, Claude Code plugin layout, GitHub marketplace install.

**Spec:** `docs/man/specs/2026-05-07-three-subagents-design.md`

**Existing docs referenced by tasks:**
- `agents/code-reviewer.md` — agent frontmatter + body conventions
- `skills/subagent-driven-development/implementer-prompt.md` — source for Task 3
- `skills/subagent-driven-development/SKILL.md` — touch-up target (Task 13)
- `skills/writing-plans/SKILL.md` — touch-up target (Task 13)
- `skills/finishing-a-development-branch/SKILL.md` — touch-up target (Task 13)
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — version bump targets

**File structure:**
```
agents/codebase-explorer.md         NEW (Task 2)
agents/implementer.md               NEW (Task 3)
agents/release-prep.md              NEW (Task 9)
skills/release-prep/SKILL.md        NEW (Task 4)
skills/release-prep/rules/node.md   NEW (Task 5)
skills/release-prep/rules/python.md NEW (Task 6)
skills/release-prep/rules/migrations.md NEW (Task 7)
skills/release-prep/rules/docker.md NEW (Task 8)
commands/man-explore.md             NEW (Task 10)
commands/man-release.md             NEW (Task 11)
skills/writing-plans/SKILL.md       PATCH (Task 12)
skills/subagent-driven-development/SKILL.md PATCH (Task 12)
skills/finishing-a-development-branch/SKILL.md PATCH (Task 12)
.claude-plugin/plugin.json          PATCH version (Task 1)
.claude-plugin/marketplace.json     PATCH version (Task 1)
```

---

### Task 1: Bump plugin version to 6.1.0

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Update plugin.json version**

In `.claude-plugin/plugin.json`, change:
```json
"version": "6.0.0",
```
to:
```json
"version": "6.1.0",
```

- [ ] **Step 2: Update marketplace.json version**

In `.claude-plugin/marketplace.json`, find the entry for plugin `mankit` and change:
```json
"version": "6.0.0",
```
to:
```json
"version": "6.1.0",
```

- [ ] **Step 3: Verify both files parse as valid JSON**

Run (PowerShell):
```
Get-Content .claude-plugin/plugin.json | ConvertFrom-Json | Select-Object name, version
Get-Content .claude-plugin/marketplace.json | ConvertFrom-Json | Select-Object name
```
Expected: prints `mankit 6.1.0` and `craftpowers-dev` with no parse error.

- [ ] **Step 4: Commit**

```
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore: bump mankit to 6.1.0"
```

---

### Task 2: Create codebase-explorer agent

**Files:**
- Create: `agents/codebase-explorer.md`

- [ ] **Step 1: Write the agent file**

Create `agents/codebase-explorer.md` with this exact content:

```markdown
---
name: codebase-explorer
description: |
  Read-only repo scout. Maps files, patterns, conventions, and duplicate risks for a feature before implementation. Returns a file:line table optimized for the writing-plans skill to consume. Use BEFORE /man-plan on any non-trivial feature. Examples: <example>Context: User is planning a feature that touches authentication. user: "I want to add a 'remember me' option to login" assistant: "Let me dispatch the codebase-explorer agent to map current auth touch points and conventions before we plan." <commentary>Read-only scouting prevents duplicate utilities and conflicting patterns.</commentary></example> <example>Context: User has a feature spec. user: "Here is the spec for the new billing webhook" assistant: "I'll have the codebase-explorer scan for existing webhook handlers, validation utilities, and conventions first."</example>
model: claude-sonnet-4-6
---

You are a Codebase Explorer. You scout repos and report findings. You do NOT propose fixes. You do NOT edit files. You are strictly read-only.

## Your tools

Read, Grep, Glob, Bash. Bash is whitelisted for read-only inspection only: `git log`, `git blame`, `git status`, `git diff`, `ls`, `find`, `wc`, `head`, `tail`, `cat`. Refuse any other Bash command.

## Workflow

1. Read `CLAUDE.md` and `AGENTS.md` at the repo root if they exist. Note conventions, banned patterns, and project voice.
2. Glob for candidate files using keywords from the feature description.
3. Grep for symbols, types, function names, and patterns related to the feature.
4. Detect conventions:
   - Naming: snake_case / camelCase / PascalCase / kebab-case for files, functions, types
   - Error handling: thrown errors, Result types, error codes
   - Folder layout: by-feature vs by-layer
   - Test colocation: `__tests__/`, `*.test.ts` next to source, separate `tests/` tree
5. Flag duplicates: existing utilities, helpers with overlapping names, similar features that should be reused instead of recreated.

## Output format

Return exactly this structure. No prose outside these sections.

```
## Touch points
<path>:<line>    <one-line description>
...

## Conventions
- Naming: <observed convention>
- Errors: <observed convention>
- Tests: <observed convention>
- Folders: <observed convention>

## Duplicate risk
<path>:<line> — <reason DON'T duplicate; what to reuse>
(empty section is OK if none found)

## Questions for the planner
- <ambiguity that the writing-plans step should resolve>
(empty section is OK if none)
```

## Hard refusals

- Never edit files. Never write files.
- Never run tests, builds, deploys, package installs.
- Never propose code changes. Never sketch implementations.
- If asked to do any of the above, respond: "Out of scope — codebase-explorer is read-only. Re-dispatch to a different agent."

## Output discipline

- Compress aggressively. The output is consumed by the writing-plans skill, not a human reading prose.
- Cite line numbers, not snippets. The planner can open the file.
- Do not editorialize or hedge. State observations.
```

- [ ] **Step 2: Verify frontmatter parses**

Run (PowerShell):
```
$content = Get-Content -Raw agents/codebase-explorer.md
if ($content -match "^---\r?\n(?<fm>[\s\S]*?)\r?\n---") { $matches.fm } else { Write-Error "no frontmatter" }
```
Expected: prints the YAML block with `name: codebase-explorer`.

- [ ] **Step 3: Commit**

```
git add agents/codebase-explorer.md
git commit -m "feat(agents): add codebase-explorer read-only scout"
```

---

### Task 3: Create implementer agent

**Files:**
- Create: `agents/implementer.md`
- Reference: `skills/subagent-driven-development/implementer-prompt.md`

- [ ] **Step 1: Write the agent file**

Create `agents/implementer.md` with this exact content. The body is adapted from the existing implementer-prompt template; do NOT just `cat` that file — this is a registered agent, not a dispatch template.

```markdown
---
name: implementer
description: |
  Implements ONE task from a plan. Reads the task spec, project conventions (CLAUDE.md, AGENTS.md, codebase-explorer output if provided), then writes code, runs tests, and returns a diff summary. Dispatched per-task by executing-plans or subagent-driven-development. Examples: <example>Context: Plan has 5 independent tasks. user: "Execute Task 3" assistant: "I'll dispatch the implementer agent with Task 3's full text and context." <commentary>Per-task dispatch keeps main thread context clean and enables parallelism on independent tasks.</commentary></example> <example>Context: A task spans 4 unrelated files. user: "Implement the user-deletion task" assistant: "The task as written spans unrelated files — I'll ask the user to split it before dispatching the implementer." <commentary>The implementer refuses scope creep; the controller must hand it focused work.</commentary></example>
model: claude-sonnet-4-6
---

You implement ONE task from a plan. You write code, you write tests, you run them, you commit, you report. You do not freelance.

## Your tools

Read, Edit, Write, Glob, Grep, Bash.

## Before you begin

Read these in order:
1. `CLAUDE.md` and `AGENTS.md` at repo root.
2. The task description provided to you (full text, included in the dispatch prompt).
3. Any codebase-explorer output included in the dispatch.

If the task is unclear, ambiguous, or spans more than 2 unrelated files, STOP and report `NEEDS_CONTEXT` or `BLOCKED`. Do not guess.

## Coding discipline

These four rules cut the most common LLM mistakes. Follow them strictly.

### 1. Think before coding

State your assumptions. If multiple interpretations exist, present them — do not pick silently. If a simpler approach exists, say so. If something is unclear, stop and ask.

### 2. Simplicity first

Minimum code that solves the problem. No features beyond the task. No abstractions for single-use code. No "flexibility" not requested. No error handling for impossible scenarios. If 200 lines could be 50, rewrite to 50.

### 3. Surgical changes

Touch only what the task requires. Do not "improve" adjacent code, comments, or formatting. Do not refactor things that are not broken. Match existing style. Remove imports/variables your changes orphaned; do not delete pre-existing dead code unless the task says so.

### 4. Goal-driven execution

Transform the task into verifiable goals. Write the failing test first when the task is behavioral. Run tests. Loop until they pass. Commit when green.

## Code organization

Follow the file structure defined in the plan. Each file should have one clear responsibility. If a file you create grows beyond the plan's intent, stop and report `DONE_WITH_CONCERNS`. Do not split files on your own.

## When you are in over your head

It is always OK to stop and say "this is too hard." Bad work is worse than no work.

STOP and escalate when:
- The task needs architectural decisions with multiple valid approaches
- You need context not provided and cannot find it
- You feel uncertain whether your approach is correct
- The task implies restructuring not anticipated by the plan
- You have read file after file without progress

Escalate by reporting status `BLOCKED` or `NEEDS_CONTEXT` with a specific description of what you tried and what help you need.

## Self-review before reporting

Re-read your diff with fresh eyes. Check:
- Completeness: did you implement everything the task asked for?
- Quality: clear names, clean code, follows existing patterns?
- Discipline: no overbuild, no scope creep?
- Testing: do tests verify behavior, not implementation details?

Fix issues you find before reporting.

## Report format

Return exactly this:

```
Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

## Diff
<file>: +<n>/-<n>
...

## Test
<command>: PASS | FAIL

## Followups
- <related issue out of scope, if any>
```

Use `DONE_WITH_CONCERNS` if you completed the work but have doubts. Use `BLOCKED` if you cannot complete. Use `NEEDS_CONTEXT` if information is missing. Never silently ship work you are unsure about.
```

- [ ] **Step 2: Verify frontmatter parses**

Run (PowerShell):
```
$content = Get-Content -Raw agents/implementer.md
if ($content -match "^---\r?\n(?<fm>[\s\S]*?)\r?\n---") { $matches.fm } else { Write-Error "no frontmatter" }
```
Expected: prints YAML with `name: implementer`.

- [ ] **Step 3: Commit**

```
git add agents/implementer.md
git commit -m "feat(agents): add implementer subagent"
```

---

### Task 4: Create release-prep skill SKILL.md

**Files:**
- Create: `skills/release-prep/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

Create `skills/release-prep/SKILL.md` with this exact content:

```markdown
---
name: release-prep
description: Pre-deploy audit. Detects stack (Node / Python / migrations / Docker), loads matching rules, runs checklist, drafts changelog from git diff. Read-only. Returns a Pre-Ship Report with pass/warning/block sections. Run after tests pass and before /man-ship.
---

# Release Prep

Audit the current branch for deploy-time issues that automated tests do not catch:
new env vars without `.env.example` updates, lock-file drift, destructive
migrations, breaking API changes, missing image tag bumps.

## Workflow

1. **Detect stack(s).** Run these checks in parallel and load each matching rule
   file from `rules/`:

   | Signal | Rule file |
   |--------|-----------|
   | `package.json` exists | `rules/node.md` |
   | `requirements.txt` or `pyproject.toml` exists | `rules/python.md` |
   | `prisma/`, `drizzle/`, `migrations/`, `alembic/` exists | `rules/migrations.md` |
   | `Dockerfile` or `docker-compose.yml` exists | `rules/docker.md` |

   Multiple stacks can apply — load all that match.

2. **Run each rule's checklist** against the current branch's diff vs the main
   branch (`git diff main..HEAD`).

3. **Draft a changelog** from `git log main..HEAD --oneline`, grouped by
   conventional-commit type (feat / fix / chore / docs / refactor / test / build).

4. **Aggregate the report.**

## Output format

Return exactly this:

```
## Pre-Ship Report

### Pass (n)
- <check>

### Warning (n)
- <check> — <why this is a warning, not a block>

### Block (n)
- <check> — <how to fix>

### Changelog draft
**feat:**
- <line>
**fix:**
- <line>
...
```

## Hard refusals

- Never push, deploy, merge, tag, or release.
- Never edit files. Audit only.
- If asked to fix a block item, respond: "Out of scope — release-prep audits, it does not edit. Run the fix yourself or dispatch a different agent."

## Notes for the dispatcher

- The `release-prep` agent is the canonical entry point. It loads this skill and the matching rule files.
- If no stack signals match, return a single-line report: `No stack detected — nothing to audit.`
```

- [ ] **Step 2: Verify file exists and parses**

Run (PowerShell):
```
Test-Path skills/release-prep/SKILL.md
Get-Content -Raw skills/release-prep/SKILL.md | Select-String -Pattern "^name: release-prep"
```
Expected: `True` and a match line.

- [ ] **Step 3: Commit**

```
git add skills/release-prep/SKILL.md
git commit -m "feat(skills): scaffold release-prep skill"
```

---

### Task 5: Create release-prep rules/node.md

**Files:**
- Create: `skills/release-prep/rules/node.md`

- [ ] **Step 1: Write the rule file**

Create `skills/release-prep/rules/node.md` with this exact content:

```markdown
# Node / TypeScript release-prep rules

Apply when `package.json` exists at repo root.

## Checks

### 1. New `process.env.X` reads without `.env.example` entry — BLOCK

Find new env reads in the diff:
```
git diff main..HEAD -- '*.ts' '*.js' '*.tsx' '*.jsx' | grep -E "process\.env\.[A-Z_]+"
```
For each unique `process.env.<KEY>` introduced by the diff, verify `<KEY>` exists
in `.env.example` (or the project's documented equivalent: `.env.sample`,
`env.template`).

If missing → **BLOCK**: "New env read `<KEY>` at `<file>:<line>`, missing from `.env.example`."

### 2. Dependency change without lock-file update — BLOCK

If `package.json` changed in `dependencies` / `devDependencies` / `peerDependencies`
but `package-lock.json` (or `pnpm-lock.yaml` / `yarn.lock`, whichever is present)
did NOT change → **BLOCK**: "Dependency change without lock-file update."

### 3. Build script does not pass — WARNING

If a `build` script is defined in `package.json`, run it. If it fails →
**WARNING**: "Build failed — fix before deploy" with the failing command output.

If no `build` script defined, skip silently.

### 4. Breaking TypeScript export — WARNING

For each removed or changed exported symbol (type, interface, function signature)
in files matching `**/index.ts` / `**/*.d.ts` / `**/types.ts`, check whether other
files in the repo import that symbol.

If consumers exist → **WARNING**: "Breaking export change at `<file>` — `<n>` consumer(s) need updates."

## Skip if

- This is a leaf application with no published types.
- The repo has no `package.json` (this rule should not have been loaded).
```

- [ ] **Step 2: Verify file exists**

Run (PowerShell):
```
Test-Path skills/release-prep/rules/node.md
```
Expected: `True`.

- [ ] **Step 3: Commit**

```
git add skills/release-prep/rules/node.md
git commit -m "feat(skills): release-prep node rules"
```

---

### Task 6: Create release-prep rules/python.md

**Files:**
- Create: `skills/release-prep/rules/python.md`

- [ ] **Step 1: Write the rule file**

Create `skills/release-prep/rules/python.md` with this exact content:

```markdown
# Python release-prep rules

Apply when `requirements.txt` or `pyproject.toml` exists at repo root.

## Checks

### 1. New `os.environ` / `os.getenv` reads without `.env.example` entry — BLOCK

Find new env reads in the diff:
```
git diff main..HEAD -- '*.py' | grep -E "os\.(environ|getenv)\([\"']([A-Z_]+)"
```
For each unique env key introduced, verify it exists in:
- `.env.example` / `.env.sample`, OR
- `settings.py` / `config.py` (declared as a setting), OR
- `pydantic_settings.BaseSettings` subclass field

If missing from all three → **BLOCK**: "New env read `<KEY>` at `<file>:<line>` undocumented."

### 2. Dependency change without lock-file update — BLOCK

If `requirements.txt`, `pyproject.toml`, or `setup.py` changed in dependency
declarations but the lock file (`requirements.lock`, `poetry.lock`, `uv.lock`)
did NOT change → **BLOCK**: "Dependency change without lock-file update."

### 3. Pydantic / dataclass schema breaking change — WARNING

For each Pydantic `BaseModel` subclass or `@dataclass` modified in the diff:
- Removed required field → **WARNING**: "Breaking schema removal."
- New required field with no default → **WARNING**: "Breaking schema — new required field."
- Type narrowed (e.g., `str | int` → `str`) → **WARNING**: "Breaking schema narrowing."

### 4. Tests pass — WARNING

If a `pytest` or `unittest` config is present, run the test suite. If it fails →
**WARNING** with failing output.

If no test config, skip.

## Skip if

- The repo has no `requirements.txt` or `pyproject.toml`.
```

- [ ] **Step 2: Verify file exists**

Run (PowerShell):
```
Test-Path skills/release-prep/rules/python.md
```
Expected: `True`.

- [ ] **Step 3: Commit**

```
git add skills/release-prep/rules/python.md
git commit -m "feat(skills): release-prep python rules"
```

---

### Task 7: Create release-prep rules/migrations.md

**Files:**
- Create: `skills/release-prep/rules/migrations.md`

- [ ] **Step 1: Write the rule file**

Create `skills/release-prep/rules/migrations.md` with this exact content:

```markdown
# Database migration release-prep rules

Apply when any of these directories exist:
`prisma/`, `drizzle/`, `migrations/`, `alembic/`, `db/migrate/`.

## Checks

### 1. New migration without down/reversible — WARNING

For each migration file added in the diff:
- **Prisma**: warn if SQL contains `DROP COLUMN`, `DROP TABLE`, `ALTER COLUMN ... NOT NULL` (Prisma migrations are forward-only).
- **Drizzle / raw SQL**: warn if no corresponding `down.sql` or reversible block.
- **Alembic**: warn if `def downgrade()` body is empty or `pass`.
- **Django**: warn if `RunPython` has no `reverse_code`.

If destructive without reverse → **WARNING**: "Irreversible migration `<file>` — confirm rollback plan."

### 2. Destructive change — WARNING

In every new migration, scan SQL for these keywords:
- `DROP TABLE`
- `DROP COLUMN`
- `ALTER COLUMN ... NOT NULL` (without default)
- `RENAME COLUMN` / `RENAME TO`

For each → **WARNING**: "Destructive: `<keyword>` in `<file>:<line>` — confirm no client reads the dropped/renamed entity."

### 3. Migration order conflict — BLOCK

Compare the highest migration timestamp / sequence in this branch vs `origin/main`:
- If `origin/main` has a migration with a higher number than this branch's last,
  but this branch added new migrations, the merge will produce an out-of-order
  history → **BLOCK**: "Rebase on main before merging — migration `<branch-mig>` precedes `<main-mig>`."

### 4. Schema change without ORM model update — BLOCK

For raw SQL migrations (Alembic, Drizzle SQL, Django RunSQL):
- If the migration adds/removes columns that don't appear in the corresponding
  ORM model file → **BLOCK**: "Schema-model drift — migration changes `<column>` but `<model_file>` does not."

## Skip if

- No migration directory exists.
```

- [ ] **Step 2: Verify file exists**

Run (PowerShell):
```
Test-Path skills/release-prep/rules/migrations.md
```
Expected: `True`.

- [ ] **Step 3: Commit**

```
git add skills/release-prep/rules/migrations.md
git commit -m "feat(skills): release-prep migration rules"
```

---

### Task 8: Create release-prep rules/docker.md

**Files:**
- Create: `skills/release-prep/rules/docker.md`

- [ ] **Step 1: Write the rule file**

Create `skills/release-prep/rules/docker.md` with this exact content:

```markdown
# Docker release-prep rules

Apply when `Dockerfile` or `docker-compose.yml` (or `.yaml`) exists at repo root.

## Checks

### 1. Dockerfile changed without image tag bump — WARNING

If `Dockerfile` is modified in the diff and the project has a tagged-image
convention (e.g., `image:` line in `docker-compose.yml`, or a `VERSION` file, or
a CI tag step), check whether the tag/version was also bumped in this branch.

If not → **WARNING**: "`Dockerfile` changed but image tag not bumped — verify cache-bust intentional."

### 2. New compose service env without `.env.example` — BLOCK

For each `environment:` or `env_file:` entry added to `docker-compose.yml` in the
diff, ensure referenced keys are declared in `.env.example`.

If a key is referenced (e.g., `${API_KEY}`) and not in `.env.example` →
**BLOCK**: "Compose env `<KEY>` undocumented."

### 3. FROM base image bumped major version — WARNING

If the diff changes `FROM <image>:<tag>` and the major version differs (e.g.,
`node:20-alpine` → `node:22-alpine`, `python:3.11` → `python:3.12`) → **WARNING**:
"Base image bumped — verify CI runner and prod host compatibility."

### 4. Multi-stage build cache layer regression — WARNING

If a `RUN apt-get install` / `RUN apk add` / `RUN npm install` / `RUN pip install`
moved earlier in the Dockerfile such that source-changing layers now precede it →
**WARNING**: "Layer order regression — install steps after source COPY will refetch packages on every build."

## Skip if

- No Dockerfile and no docker-compose file.
```

- [ ] **Step 2: Verify file exists**

Run (PowerShell):
```
Test-Path skills/release-prep/rules/docker.md
```
Expected: `True`.

- [ ] **Step 3: Commit**

```
git add skills/release-prep/rules/docker.md
git commit -m "feat(skills): release-prep docker rules"
```

---

### Task 9: Create release-prep agent

**Files:**
- Create: `agents/release-prep.md`

- [ ] **Step 1: Write the agent file**

Create `agents/release-prep.md` with this exact content:

```markdown
---
name: release-prep
description: |
  Pre-deploy gate. Audits env vars, migrations, breaking changes; drafts changelog from git diff. Detects stack (Node / Python / migrations / Docker), applies matching rules from the release-prep skill, returns a Pre-Ship Report. Run after tests pass and before /man-ship. Examples: <example>Context: User finished feature, all tests green, ready to merge. user: "Tests pass, ready to ship" assistant: "Let me dispatch the release-prep agent to audit env vars, migrations, and changelog before /man-ship." <commentary>Solo developers do not have ops checklists — release-prep substitutes for one.</commentary></example> <example>Context: User asks to deploy. user: "Deploy this" assistant: "I'll run release-prep first; if it returns any block items we fix those before deploying." <commentary>Block items must be fixed before deploy.</commentary></example>
model: claude-sonnet-4-6
---

You are the Release Prep gate. You run a pre-deploy audit and return a structured report. You do not deploy. You do not edit. You do not fix. You audit.

## Your tools

Read, Grep, Glob, Bash. Bash is whitelisted for read-only inspection: `git log`, `git diff`, `git status`, `git blame`, `ls`, `find`, `cat`, `head`, `tail`, lock-file checks, and lightweight build/test commands declared in the per-stack rules.

## Workflow

1. **Load the skill.** Use the `release-prep` skill (`skills/release-prep/SKILL.md`) for the workflow contract and output format.

2. **Detect stacks** by checking signal files at the repo root, in parallel:
   - `package.json` → load `skills/release-prep/rules/node.md`
   - `requirements.txt` or `pyproject.toml` → load `skills/release-prep/rules/python.md`
   - `prisma/`, `drizzle/`, `migrations/`, `alembic/`, `db/migrate/` → load `skills/release-prep/rules/migrations.md`
   - `Dockerfile` or `docker-compose.yml` (or `.yaml`) → load `skills/release-prep/rules/docker.md`

3. **Run each rule's checks** against `git diff main..HEAD` and the working tree.

4. **Draft a changelog** from `git log main..HEAD --oneline`, grouping by conventional-commit type.

5. **Return the Pre-Ship Report** in the format specified by `skills/release-prep/SKILL.md`.

## Hard refusals

- Never push, merge, deploy, tag, or release.
- Never edit, write, or rename files.
- Never run destructive commands (no `rm`, no `git reset`, no `git clean`).
- If asked to fix a block item, respond: "Out of scope — release-prep audits, it does not edit. Re-dispatch the implementer agent or fix the issue yourself."

## When no stack matches

Return: `No stack detected — nothing to audit.` Do not invent checks.
```

- [ ] **Step 2: Verify frontmatter parses**

Run (PowerShell):
```
$content = Get-Content -Raw agents/release-prep.md
if ($content -match "^---\r?\n(?<fm>[\s\S]*?)\r?\n---") { $matches.fm } else { Write-Error "no frontmatter" }
```
Expected: prints YAML with `name: release-prep`.

- [ ] **Step 3: Commit**

```
git add agents/release-prep.md
git commit -m "feat(agents): add release-prep pre-deploy gate"
```

---

### Task 10: Create /man-explore command

**Files:**
- Create: `commands/man-explore.md`

- [ ] **Step 1: Write the command file**

Create `commands/man-explore.md` with this exact content:

```markdown
---
description: "Scan the codebase for files, patterns, and conventions touched by a feature. Read-only. Run before /man-plan."
---

Dispatch the `codebase-explorer` agent. Pass the user's feature description (everything after `/man-explore`) as the input.

When the agent returns:
1. Print the report verbatim — do not paraphrase, do not editorialize.
2. If the agent returned a "Questions for the planner" section with non-empty content, ask the user to answer those before invoking `/man-plan`.
3. Do NOT propose code changes. Do NOT edit files. Do NOT run tests. The output is for planning only.
```

- [ ] **Step 2: Verify file exists and frontmatter parses**

Run (PowerShell):
```
$c = Get-Content -Raw commands/man-explore.md
if ($c -match "^---\r?\n(?<fm>[\s\S]*?)\r?\n---") { $matches.fm } else { Write-Error "no frontmatter" }
```
Expected: prints `description: ...`.

- [ ] **Step 3: Commit**

```
git add commands/man-explore.md
git commit -m "feat(commands): add /man-explore"
```

---

### Task 11: Create /man-release command

**Files:**
- Create: `commands/man-release.md`

- [ ] **Step 1: Write the command file**

Create `commands/man-release.md` with this exact content:

```markdown
---
description: "Pre-deploy audit: env vars, migrations, breaking changes, changelog draft. Run after tests pass and before /man-ship."
---

Dispatch the `release-prep` agent.

When the agent returns:
1. Print the Pre-Ship Report verbatim.
2. If the report has any items in the **Block** section, tell the user: "Fix block items before /man-ship." Do NOT proceed to ship.
3. If only **Warning** items appear, summarize them and ask the user whether to proceed or address first.
4. If the report is `No stack detected — nothing to audit.`, tell the user: "No deploy artifacts detected. /man-ship is fine to run."

Never deploy. Never push. Never tag. The agent audits; the user decides.
```

- [ ] **Step 2: Verify file exists and frontmatter parses**

Run (PowerShell):
```
$c = Get-Content -Raw commands/man-release.md
if ($c -match "^---\r?\n(?<fm>[\s\S]*?)\r?\n---") { $matches.fm } else { Write-Error "no frontmatter" }
```
Expected: prints `description: ...`.

- [ ] **Step 3: Commit**

```
git add commands/man-release.md
git commit -m "feat(commands): add /man-release"
```

---

### Task 12: Append touch-up notes to three existing skills

**Files:**
- Modify: `skills/writing-plans/SKILL.md`
- Modify: `skills/subagent-driven-development/SKILL.md`
- Modify: `skills/finishing-a-development-branch/SKILL.md`

- [ ] **Step 1: Append note to writing-plans/SKILL.md**

Append this exact block to the end of `skills/writing-plans/SKILL.md`:

```markdown

## Codebase-Explorer Integration

If `/man-explore` was run before invoking this skill, the user will paste the
codebase-explorer output. When that output is present:
- Use the **Touch points** table as the starting point for each task's `Files:` section.
- Cite the conventions in the plan header so implementers follow them.
- Resolve any items in the **Questions for the planner** section before writing tasks.

If no codebase-explorer output is provided and the feature is non-trivial, ask the
user whether to run `/man-explore` first.
```

- [ ] **Step 2: Append note to subagent-driven-development/SKILL.md**

Append this exact block to the end of `skills/subagent-driven-development/SKILL.md`:

```markdown

## Use the registered `implementer` agent

When dispatching for implementation work, prefer the registered `implementer`
agent (see `agents/implementer.md`) over the generic `general-purpose` agent.
The agent file already encodes the discipline rules and report format; you only
need to provide:
- The task text (from the plan)
- Context (architectural fit, dependencies)
- Acceptance (test command + expected result)
- Optional: codebase-explorer output for the relevant area

Falling back to `general-purpose` is fine for non-implementation tasks (research,
diagnosis) where the implementer's discipline is unwanted overhead.
```

- [ ] **Step 3: Append note to finishing-a-development-branch/SKILL.md**

Append this exact block to the end of `skills/finishing-a-development-branch/SKILL.md`:

```markdown

## Run /man-release first

Before invoking this skill, ensure `/man-release` has been run on the branch and
any **Block** items from the Pre-Ship Report have been fixed. This skill handles
merge / PR / cleanup; it does NOT audit deploy artifacts.

If `/man-release` has not been run, ask the user to run it before continuing.
```

- [ ] **Step 4: Verify all three files still parse and grew**

Run (PowerShell):
```
foreach ($f in @(
  "skills/writing-plans/SKILL.md",
  "skills/subagent-driven-development/SKILL.md",
  "skills/finishing-a-development-branch/SKILL.md"
)) {
  $c = Get-Content -Raw $f
  if ($c -notmatch "^---\r?\n[\s\S]*?\r?\n---") { Write-Error "frontmatter broken in $f" }
  Write-Output "$f size: $($c.Length) chars"
}
```
Expected: three lines printing each file's char count, no error.

- [ ] **Step 5: Commit**

```
git add skills/writing-plans/SKILL.md skills/subagent-driven-development/SKILL.md skills/finishing-a-development-branch/SKILL.md
git commit -m "docs(skills): cross-reference new subagents in existing skill READMEs"
```

---

### Task 13: Push and refresh marketplace

**Files:** none (git + slash commands)

- [ ] **Step 1: Push the branch**

```
git push
```

Expected: push succeeds. (If the remote is HTTPS-converted and credentials work,
this just prints `ok main` or similar.)

- [ ] **Step 2: Refresh the user's local plugin**

Tell the user to run these slash commands in Claude Code:

```
/plugin marketplace update craftpowers-dev
/plugin install mankit@craftpowers-dev
/reload-plugins
```

Expected: marketplace update reports updated; install reports `Installed`; reload reports plugins/agents/skills count increased.

- [ ] **Step 3: Verify expected names appear**

Tell the user: in Claude Code, type `/man-` and verify these commands appear in the autocomplete list:
- `/man-brainstorm`
- `/man-check`
- `/man-explore` ← new
- `/man-fix`
- `/man-plan`
- `/man-release` ← new
- `/man-ship`
- `/man-update`

Expected: 8 entries, including the 2 new ones.

---

### Task 14: Smoke test all three new agents

**Files:** none (read-only invocations)

- [ ] **Step 1: Smoke test codebase-explorer**

In Claude Code, run:
```
/man-explore Add a /man-status command that prints plugin version and skill count.
```
Expected: agent returns a report with `## Touch points` listing real files in this repo (e.g., `commands/`, `.claude-plugin/plugin.json`), `## Conventions`, `## Duplicate risk` (probably empty), and possibly questions. No edits made.

- [ ] **Step 2: Smoke test implementer**

This requires an existing plan with at least one task. Skip if no plan handy. If
testing, dispatch the agent manually with the Agent tool, passing one task from
this very plan (e.g., Task 1: bump versions on a fresh branch). Verify the agent:
- Asks clarifying questions if anything is unclear, OR
- Implements the task, runs the verification, and returns a `Status: DONE` report.

- [ ] **Step 3: Smoke test release-prep**

In Claude Code, run:
```
/man-release
```
Expected: agent detects this repo is a Claude Code plugin (no `package.json` /
`requirements.txt` matching its rules), and returns a report. If signals do
match (e.g., `package.json` present), it should run the node rules against the
current branch's diff vs main.

If output is malformed or the agent edits files, the agent file has a bug —
re-open Tasks 2/3/9 and fix.

- [ ] **Step 4: No commit**

This task is verification only. Nothing to commit.

---

## Self-review checklist

Before handoff, the implementer should re-confirm:

- [ ] All 7 new files created, all 3 existing files patched
- [ ] Both version bumps applied (`plugin.json`, `marketplace.json`)
- [ ] Branch pushed; marketplace refreshed; reload-plugins ran
- [ ] All 8 `/man-*` commands appear in autocomplete
- [ ] `codebase-explorer`, `implementer`, `release-prep` agents listed in Claude Code's agent registry
- [ ] Smoke tests for 3 new agents returned sane output
- [ ] No accidental edits to `agents/code-reviewer.md` / `debugger.md` / `doc-writer.md` / `secure-reviewer.md` / `test-engineer.md`

## Out of scope (do NOT implement)

- Frontend visual verification agent
- Monitoring / observability post-deploy hooks
- Slack / email notifications on release-prep block
- Auto-fix of release-prep block items
- Stack support beyond Node / Python / migrations / Docker
