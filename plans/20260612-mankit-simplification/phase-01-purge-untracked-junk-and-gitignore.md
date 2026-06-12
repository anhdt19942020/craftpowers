# Phase 01 — Purge Untracked Junk + Gitignore Hardening

## Context Links
- Parent: [plan.md](plan.md)
- Audit evidence: `git ls-files skills/` = 63 dirs tracked; `ls skills/` = 187 dirs on disk

## Overview
- **Priority:** High | **Status:** ⬜ Pending | **Risk:** None — touches only untracked files
- Delete ~124 untracked junk dirs in `skills/`, 289MB `.venv`, stray files. Harden `.gitignore` so junk can't return.

## Key Insights
- Junk classes (all untracked, verified via `git ls-files`):
  1. **52 `bmad-*` stub dirs** — BMAD-method residue, no SKILL.md
  2. **~72 global-skill leftovers** (`ck-plan`, `shopify`, `threejs`, `brainstorm`, `show-off` 70MB, `sequential-thinking` 32MB, `markdown-novel-viewer` 10MB…) — copied from `~/.claude/skills` at some point, partially deleted; only `references/`/`scripts/` shells remain, no SKILL.md
  3. **`skills/.venv`** 289MB Python venv
  4. **Root strays:** `bash.exe.stackdump`, `nul`
- `_shared/` and `common/` lack SKILL.md but check git: if tracked, KEEP (shared lib for skills); if untracked, inspect before deleting.
- `.gitignore` missing: `.venv/`, `*.stackdump`, `nul`

## Requirements
- Zero tracked file touched. Verify with `git status` before+after: only untracked entries disappear.

## Related Code Files
- Delete: all untracked dirs under `skills/` (list from `git ls-files` diff), `skills/.venv/`, `bash.exe.stackdump`, `nul`
- Modify: `.gitignore`

## Implementation Steps
1. Snapshot: `git ls-files skills/ | cut -d/ -f2 | sort -u > /tmp/tracked.txt`
2. Diff against `ls skills/` → untracked list. Manually confirm `_shared`, `common` status before including.
3. Dry-run print, then delete untracked dirs + `.venv` + root strays.
4. Append to `.gitignore`: `.venv/`, `*.stackdump`, `nul`
5. `git status --short` → expect clean (only .gitignore modified).

## Todo List
- [ ] Snapshot tracked list
- [ ] Verify `_shared`/`common` tracked status
- [ ] Delete untracked skill dirs (~124)
- [ ] Delete `.venv`, stackdump, `nul`
- [ ] Update `.gitignore`
- [ ] Verify git status clean

## Success Criteria
- `ls skills/ | wc -l` = 63 (+ `_shared`/`common` if tracked)
- Disk reclaimed ≥ 400MB
- `git status` shows only `.gitignore` change

## Risk Assessment
- Mis-deleting a tracked dir → mitigated: drive deletion strictly from git-untracked diff, dry-run first. Recovery: `git checkout -- skills/<dir>`.

## Security Considerations
- None — local file deletion.

## Next Steps
- Phase 2 (dedup) operates on the clean 63-skill set.
