---
name: instinct-management
description: Manage behavioral instincts — create, list, edit, delete, promote, demote. Instincts are confidence-weighted behavioral priors injected into every session.
---

# Instinct Management

CRUD operations for behavioral instincts. Instincts are confidence-weighted priors that shape agent behavior at SessionStart.

## Usage

```
/man-instinct list              # Show all instincts across 4 directories
/man-instinct create <id>       # Interactively create a new instinct
/man-instinct edit <id>         # Modify an existing instinct
/man-instinct delete <id>       # Remove an instinct file
/man-instinct promote <id>      # Move project-scoped instinct to global
/man-instinct demote <id>       # Move global instinct to project scope
/man-instinct evolve            # Cluster related instincts into proposed skills
/man-instinct prune             # Delete instincts older than 30 days below threshold
/man-instinct learn-eval <id>   # Evaluate a candidate instinct before committing
```

## Instinct File Format

```markdown
---
id: prefer-integration-tests
confidence: 0.85
scope: project
trigger: "when writing test files"
---

# Prefer Integration Tests

## Action
Use real database connections in tests, never mock the DB layer.

## Evidence
- User corrected mock-based tests 3 times on 2026-05-20
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique kebab-case identifier |
| `confidence` | Yes | 0.0-1.0 — only instincts ≥0.7 are injected |
| `scope` | No | Auto-set by location (project/global) |
| `trigger` | No | Human-readable description of when this applies |

## Directory Structure

```
~/.claude/instincts/
├── personal/           # Your global instincts
└── inherited/          # Shared/curated global instincts

{project}/.claude/instincts/
├── personal/           # Project-specific instincts
└── inherited/          # Team-shared project instincts
```

**Deduplication rule:** If the same `id` exists in both project and global scope, the project-scoped version wins.

**Injection cap:** Maximum 6 instincts per session (sorted by confidence, project-first).

## Commands

### `list`

Shows all instincts across all 4 directories.

Use `discover_instincts()` from `hooks/lib/instinct_loader.py` to scan directories.

Display format:
```
Active instincts (N injected, M total):
  [project 85%] prefer-integration-tests — Use real DB in tests
  [global  80%] grep-before-edit — Always grep codebase before editing
  [project 70%] use-pnpm — Use pnpm, not npm
  ...
All instincts (including below threshold):
  [global  30%] check-logs — (below threshold, not injected)
```

### `create <id>`

Interactive creation via AskUserQuestion:

1. Ask: **Confidence** — 0.7 (low), 0.8 (medium), 0.9 (high), 1.0 (always)
2. Ask: **Scope** — project (this repo only) or global (~/.claude)
3. Ask: **Trigger** — "when writing tests", "always", "when editing Python", etc.
4. Ask: **Action** — the behavioral rule in plain English

Write to `{scope_dir}/personal/{id}.md` with proper frontmatter.

After creating, remind user: "This instinct will be active in the **next** session (not this one, since SessionStart already ran)."

### `edit <id>`

1. Find the instinct file (search all 4 directories)
2. Read current content
3. Use AskUserQuestion to ask what to change (confidence, trigger, action, or all)
4. Write updated file

### `delete <id>`

1. Find the instinct file
2. Confirm with user: "Delete `{id}` from {path}? This cannot be undone."
3. Remove file if confirmed

### `promote <id>`

Move a project-scoped instinct to global scope:

1. Find `{project}/.claude/instincts/personal/{id}.md`
2. Copy to `~/.claude/instincts/personal/{id}.md`
3. Delete original (or ask user whether to keep project copy)

Useful for instincts that proved valuable on this project and should apply everywhere.

### `demote <id>`

Move a global instinct to project scope:

1. Find `~/.claude/instincts/personal/{id}.md`
2. Copy to `{project}/.claude/instincts/personal/{id}.md`
3. Optionally update to project-specific version

Useful when a global instinct needs project-specific overrides.

### `evolve`

Scan all instincts and identify clusters of related patterns that could be consolidated into a skill.

**Algorithm:**
1. Load all instincts via `discover_instincts()` from `hooks/lib/instinct_loader.py`
2. Group instincts by semantic similarity of their `trigger` field (manual grouping — look for shared verbs: "when writing", "before editing", "when testing", etc.)
3. For each group of 2+ instincts with combined confidence ≥ 1.5, propose a skill:
   - Show: instinct IDs in cluster, triggers, actions
   - Ask user: "Convert these N instincts into a skill named `<suggested-name>`?"
4. If user confirms → output a complete SKILL.md template populated with the merged behavior (do NOT write the file — user pastes into `man-cook`)
5. If no clusters found → report "No clusters found. Add more instincts first."

**Output format for confirmed cluster:**
```
Proposed skill: skills/<name>/SKILL.md
---
name: <name>
description: <merged description>
---

# <Name>

<merged action combining all instinct actions>
```

---

### `prune`

Delete stale instincts that have low confidence and are old.

**Prune criteria:** instinct file `mtime` older than 30 days AND confidence < 0.7.

**Steps:**
1. Load all instincts from all 4 directories
2. Check file modification time (use `os.path.getmtime()`) and frontmatter `confidence`
3. List instincts matching prune criteria
4. If none found: "No expired instincts. All instincts are recent or above threshold."
5. If found: show list, ask user "Delete N expired instincts?" (yes/no)
6. If confirmed: delete files and report "Pruned: <list of deleted IDs>"

---

### `learn-eval <id>`

Evaluate a candidate instinct against existing ones before committing it.

**Steps:**
1. Find the instinct file by `<id>` (search all 4 directories)
2. Load all OTHER instincts
3. Check for:
   - **Duplicate:** does another instinct have same/similar `trigger`? Flag if overlap > 60%
   - **Conflict:** does the action contradict another instinct's action?
   - **Confidence calibration:** if confidence ≥ 0.9 but no Evidence section, warn "High confidence without evidence — consider starting at 0.7-0.8"
4. Output evaluation report:
   ```
   learn-eval: <id>
   ✅ No duplicates found
   ⚠️  Possible conflict with: grep-before-edit (both trigger on "before editing")
   ℹ️  Confidence 0.9 set without Evidence block — consider 0.8 until more data
   Recommendation: SAVE | REVISE | DUPLICATE (pick one)
   ```

---

## Confidence Guidelines

| Confidence | Meaning | When to use |
|-----------|---------|-------------|
| 0.7 | Weak prior | Observed once, uncertain |
| 0.8 | Moderate | Observed 2-3 times, fairly confident |
| 0.9 | Strong | Consistent pattern, high confidence |
| 1.0 | Absolute | Always true for this project/user |

Instincts below 0.7 are stored but not injected. Raise confidence as evidence accumulates.

## Example Instincts

**No mock DB** (project-scoped, 0.85):
```markdown
---
id: no-mock-db
confidence: 0.85
trigger: "when writing tests"
---
# No Mock DB
## Action
Use real database connections in tests. Never mock the DB layer.
## Evidence
- User corrected mock-based approach 3 times
```

**Grep before edit** (global, 0.8):
```markdown
---
id: grep-before-edit
confidence: 0.8
trigger: "before editing any file"
---
# Grep Before Edit
## Action
Always grep the codebase for the symbol/pattern before editing. Verify you have the right file.
```
