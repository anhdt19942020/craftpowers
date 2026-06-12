# Rename Plugin Prefix `craftpowers`/`superpowers` → `man` — Design Spec

**Date:** 2026-05-07
**Scope:** Rename plugin namespace from `man:`/`man:` to `man:` across all skill references, manifests, paths, and docs.

---

## 1. Problem Statement

Skill invocation prefix currently mixed: `man:` (active plugin name) and `man:` (legacy / parent project). User wants single short prefix `man:` matching command convention (`/man-brainstorm`, `/man-plan`, etc.).

Concretely:
- Plugin manifest `name: "craftpowers"` produces `man:<skill>` invocations
- Legacy `man:` refs scattered across docs, tests, PR template
- Folder `docs/man/` and skill `using-man` reflect old branding

---

## 2. Changes

### 2.1 Plugin Manifests

**Files:**
- `.claude-plugin/plugin.json` — `"name": "craftpowers"` → `"name": "man"`
- `.claude-plugin/marketplace.json` — `plugins[0].name: "craftpowers"` → `"man"`
- `.cursor-plugin/plugin.json` — `"name": "craftpowers"` → `"man"`, `"displayName": "Craftpowers"` → `"Man"`

Description fields keep "Craftpowers" branding text (not invocation prefix).

### 2.2 Sweep `man:` → `man:`

34 occurrences / 13 files. Replace all:
- `README.md`
- `hooks/session-start`
- `scripts/install.py`
- `skills/executing-plans/SKILL.md`
- `skills/requesting-code-review/SKILL.md`
- `skills/systematic-debugging/SKILL.md`
- `skills/subagent-driven-development/SKILL.md`
- `skills/subagent-driven-development/code-quality-reviewer-prompt.md`
- `skills/writing-plans/SKILL.md`
- `skills/using-man/references/copilot-tools.md`
- `skills/using-man/references/codex-tools.md`
- `skills/writing-skills/SKILL.md`
- `skills/writing-skills/testing-skills-with-subagents.md`

### 2.3 Sweep `man:` → `man:`

48 occurrences / 17 files. Replace all:
- `.github/PULL_REQUEST_TEMPLATE.md`
- `CLAUDE.md`
- `commands/execute-plan.md`, `commands/write-plan.md`
- `RELEASE-NOTES.md`
- `docs/plans/2025-11-22-opencode-support-design.md`
- `docs/plans/2025-11-22-opencode-support-implementation.md`
- `docs/plans/2025-11-28-skills-improvements-from-user-feedback.md`
- `docs/plans/2026-01-17-visual-brainstorming.md`
- `tests/claude-code/test-subagent-driven-development-integration.sh`
- `tests/opencode/test-tools.sh`
- `tests/opencode/test-priority.sh`
- `tests/subagent-driven-dev/svelte-todo/scaffold.sh`
- `tests/subagent-driven-dev/svelte-todo/plan.md`
- `tests/subagent-driven-dev/go-fractals/scaffold.sh`
- `tests/subagent-driven-dev/go-fractals/plan.md`
- `tests/subagent-driven-dev/run-test.sh`

### 2.4 Rename Skill Folder

`skills/using-man/` → `skills/using-man/`

Skill name = folder name. Update internal frontmatter `name: using-man` → `name: using-man`. Update self-references.

### 2.5 Rename Docs Folder

`docs/man/` → `docs/man/`

Subfolders preserved: `docs/man/plans/`, `docs/man/specs/`.

Refs to update: any doc/code mentioning `docs/man/` path.

### 2.6 Install Junction

`scripts/install.py` creates junction `~/.claude/plugins/man/`. After rename, plugin name = `man` → junction target = `~/.claude/plugins/man/`.

`scripts/verify.py` and `/man-check` paths also update.

### 2.7 NOT Changed

- GitHub repo name `craftpowers` (URL stable)
- Repo root folder `D:\projects\craftpowers` (working dir)
- "Craftpowers" branding strings in description/displayName fields
- Author / homepage / repository URLs

---

## 3. Out of Scope

- Renaming `man-*` slash commands (already prefixed, unchanged)
- GitHub repo rename
- Memory/user-side CLAUDE.md edits (user's private)
- Bump major version (rename = breaking install, but user is sole consumer)

---

## 4. Implementation Order

1. Update 3 plugin manifests (`name` field)
2. Bulk replace `man:` → `man:` (34 refs)
3. Bulk replace `man:` → `man:` (48 refs)
4. Rename `skills/using-man/` → `skills/using-man/`, fix internal refs
5. Rename `docs/man/` → `docs/man/`, fix path refs
6. Update `scripts/install.py` junction target
7. Update `scripts/verify.py` paths
8. Bump version `5.0.7` → `6.0.0` (breaking)
9. Reinstall: `python scripts/install.py`
10. Verify: `/man-check`

---

## 5. Risk Assessment

- **Breaking change:** Existing `~/.claude/plugins/man/` junction stale. User must reinstall.
- **Test fail risk:** Tests in `tests/` reference `man:` — sweep may break test fixtures. Verify each test still passes intent.
- **Plugin namespace conflict:** `man` short, may collide with future Anthropic plugins. Accept risk (user's personal fork).
- **Rollback:** Git revert; re-run install.

---

## 6. Verification

- `grep -r "man:" .` → 0 hits
- `grep -r "man:" .` → 0 hits (except branding text in descriptions)
- Plugin reload: skill invocation `man:brainstorming` works
- `/man-check` passes
