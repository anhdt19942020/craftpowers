# Rename Plugin Prefix to `man` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use man:subagent-driven-development (recommended) or man:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename plugin namespace `man:`/`man:` → `man:` across manifests, skills, docs, paths, tests.

**Architecture:** Three plugin manifest edits + bulk text replace across 30 files + 2 folder renames + install path updates + reinstall + verify.

**Tech Stack:** JSON manifests, Markdown, Bash, Python (install/verify scripts).

---

### Task 1: Safety Backup

**Files:** `D:\projects\craftpowers\` (entire repo)

- [ ] **Step 1: Create backup branch**

```powershell
git checkout -b backup/pre-man-rename
git checkout main
git checkout -b feat/rename-prefix-man
```

Expected: On new branch `feat/rename-prefix-man`, backup branch exists.

---

### Task 2: Update Plugin Manifests

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.cursor-plugin/plugin.json`

- [ ] **Step 1: Edit `.claude-plugin/plugin.json`**

Use Edit. Change `"name": "craftpowers"` → `"name": "man"`.

- [ ] **Step 2: Edit `.claude-plugin/marketplace.json`**

Change `"name": "craftpowers"` (in plugins[0]) → `"name": "man"`.

- [ ] **Step 3: Edit `.cursor-plugin/plugin.json`**

Change `"name": "craftpowers"` → `"name": "man"`.
Change `"displayName": "Craftpowers"` → `"displayName": "Man"`.

- [ ] **Step 4: Verify JSON valid**

```powershell
Get-Content ".claude-plugin/plugin.json" | ConvertFrom-Json
Get-Content ".claude-plugin/marketplace.json" | ConvertFrom-Json
Get-Content ".cursor-plugin/plugin.json" | ConvertFrom-Json
```

Expected: 3 objects parsed, no errors.

---

### Task 3: Sweep `man:` → `man:` in Skills

**Files** (use Edit `replace_all: true` for each):
- Modify: `skills/requesting-code-review/SKILL.md`
- Modify: `skills/subagent-driven-development/SKILL.md`
- Modify: `skills/subagent-driven-development/code-quality-reviewer-prompt.md`
- Modify: `skills/executing-plans/SKILL.md`
- Modify: `skills/writing-plans/SKILL.md`
- Modify: `skills/writing-skills/SKILL.md`
- Modify: `skills/writing-skills/testing-skills-with-subagents.md`
- Modify: `skills/systematic-debugging/SKILL.md`

- [ ] **Step 1: Replace per file**

For each file above, run Edit with `old_string: "man:"`, `new_string: "man:"`, `replace_all: true`.

- [ ] **Step 2: Verify**

```powershell
rtk grep "man:" skills/
```

Expected: 0 matches in `skills/`.

---

### Task 4: Sweep `man:` → `man:` in Other Files

**Files:**
- Modify: `README.md`
- Modify: `hooks/session-start`
- Modify: `scripts/install.py`

- [ ] **Step 1: Edit README.md**

Edit `man:` → `man:` `replace_all: true`.

- [ ] **Step 2: Edit hooks/session-start**

Edit `man:using-man` → `man:using-man` `replace_all: true`.
Edit `You have craftpowers.` → `You have man.` (single occurrence).

- [ ] **Step 3: Edit scripts/install.py**

Edit `man:` → `man:` (only colon-suffixed forms; path/var refs handled in Task 7).

```powershell
rtk grep "man:" .
```

Expected: 0 matches.

---

### Task 5: Sweep `man:` → `man:`

**Files:**
- Modify: `.github/PULL_REQUEST_TEMPLATE.md`
- Modify: `CLAUDE.md`
- Modify: `commands/execute-plan.md`
- Modify: `commands/write-plan.md`
- Modify: `RELEASE-NOTES.md`
- Modify: `docs/plans/2025-11-22-opencode-support-design.md`
- Modify: `docs/plans/2025-11-22-opencode-support-implementation.md`
- Modify: `docs/plans/2025-11-28-skills-improvements-from-user-feedback.md`
- Modify: `docs/plans/2026-01-17-visual-brainstorming.md`
- Modify: `tests/claude-code/test-subagent-driven-development-integration.sh`
- Modify: `tests/opencode/test-tools.sh`
- Modify: `tests/opencode/test-priority.sh`
- Modify: `tests/subagent-driven-dev/svelte-todo/scaffold.sh`
- Modify: `tests/subagent-driven-dev/svelte-todo/plan.md`
- Modify: `tests/subagent-driven-dev/go-fractals/scaffold.sh`
- Modify: `tests/subagent-driven-dev/go-fractals/plan.md`
- Modify: `tests/subagent-driven-dev/run-test.sh`

- [ ] **Step 1: Replace per file**

For each file: Edit `old_string: "man:"`, `new_string: "man:"`, `replace_all: true`.

- [ ] **Step 2: Verify**

```powershell
rtk grep "man:" .
```

Expected: 0 matches.

---

### Task 6: Rename Skill `using-man` → `using-man`

**Files:**
- Rename: `skills/using-man/` → `skills/using-man/`
- Modify: `skills/using-man/SKILL.md` (frontmatter)
- Modify: `hooks/session-start` (refs to folder + var name)

- [ ] **Step 1: Rename folder**

```powershell
Rename-Item "skills/using-man" "using-man"
```

- [ ] **Step 2: Update SKILL.md frontmatter**

Edit `skills/using-man/SKILL.md`:
- `name: using-man` → `name: using-man`

- [ ] **Step 3: Update hook refs**

Edit `hooks/session-start`:
- `skills/using-man/SKILL.md` → `skills/using-man/SKILL.md`
- `using_superpowers_content` → `using_man_content` (replace_all)
- `using_superpowers_escaped` → `using_man_escaped` (replace_all)

- [ ] **Step 4: Sweep remaining `using-man` refs**

```powershell
rtk grep "using-man" .
```

For each hit (excluding tests/historical docs already swept), Edit → `using-man`.

Expected files to fix: `README.md`, `GEMINI.md`, `docs/README.codex.md`.

- [ ] **Step 5: Verify**

```powershell
rtk grep "using-man" skills/ hooks/ scripts/ commands/
```

Expected: 0 matches in active code.

---

### Task 7: Rename `docs/man/` → `docs/man/`

**Files:**
- Rename: `docs/man/` → `docs/man/`
- Modify path refs

- [ ] **Step 1: Rename folder**

```powershell
Rename-Item "docs/craftpowers" "man"
```

This moves: `docs/man/plans/` → `docs/man/plans/`, `docs/man/specs/` → `docs/man/specs/`.

- [ ] **Step 2: Update path refs**

Files referencing `docs/man/`:
- `scripts/install.py`
- `skills/writing-plans/SKILL.md`
- `skills/requesting-code-review/SKILL.md`
- `skills/subagent-driven-development/SKILL.md`
- `skills/brainstorming/SKILL.md`
- `skills/brainstorming/spec-document-reviewer-prompt.md`
- `.gitignore`

For each: Edit `docs/man/` → `docs/man/` `replace_all: true`.

- [ ] **Step 3: Verify**

```powershell
rtk grep "docs/craftpowers" .
```

Expected: 0 matches.

---

### Task 8: Update Install Junction Path

**Files:**
- Modify: `scripts/install.py`
- Modify: `scripts/verify.py`
- Modify: `commands/man-check.md`
- Modify: `commands/man-update.md`
- Modify: `README.md`

Plugin name = `man` → junction target = `~/.claude/plugins/man/`.

- [ ] **Step 1: Update install.py junction logic**

Edit `scripts/install.py`: replace `~/.claude/plugins/man` → `~/.claude/plugins/man` `replace_all: true`.
Also edit `craftpowers_root` variable name → `man_root` if appears.

- [ ] **Step 2: Update verify.py paths**

Edit `scripts/verify.py`: same replace.

- [ ] **Step 3: Update command docs**

Edit `commands/man-check.md` and `commands/man-update.md`: replace `~/.claude/plugins/man` → `~/.claude/plugins/man`.

- [ ] **Step 4: Update README install snippet**

Edit `README.md`:
- `git clone https://github.com/anhdt19942020/craftpowers ~/.claude/plugins/man` → `git clone https://github.com/anhdt19942020/craftpowers ~/.claude/plugins/man`
- `python ~/.claude/plugins/man/scripts/install.py` → `python ~/.claude/plugins/man/scripts/install.py`

- [ ] **Step 5: Verify**

```powershell
rtk grep "plugins/man" .
```

Expected: 0 matches.

---

### Task 9: Bump Version

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.cursor-plugin/plugin.json`

- [ ] **Step 1: Bump version 5.0.7 → 6.0.0 (breaking)**

For each manifest: Edit `"version": "5.0.7"` → `"version": "6.0.0"`.

---

### Task 10: Move This Plan + Spec to New Path

**Files:**
- Move: `docs/man/specs/2026-05-07-rename-prefix-to-man-design.md` (already moved by Task 7 folder rename)
- Move: `docs/man/plans/2026-05-07-rename-prefix-to-man.md` (already moved by Task 7)

- [ ] **Step 1: Verify file location**

```powershell
Test-Path "docs/man/plans/2026-05-07-rename-prefix-to-man.md"
Test-Path "docs/man/specs/2026-05-07-rename-prefix-to-man-design.md"
```

Expected: Both `True`.

---

### Task 11: Reinstall Plugin

**Files:** None (runtime side effects)

- [ ] **Step 1: Remove old junction**

```powershell
Remove-Item "$env:USERPROFILE\.claude\plugins\craftpowers" -Recurse -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 2: Run install.py**

```powershell
python scripts/install.py
```

Expected: Install succeeds. New junction `~/.claude/plugins/man` created.

- [ ] **Step 3: Verify junction**

```powershell
Test-Path "$env:USERPROFILE\.claude\plugins\man"
```

Expected: `True`.

---

### Task 12: Run Health Check

- [ ] **Step 1: Run verify.py**

```powershell
python scripts/verify.py
```

Expected: All 22 checks PASS.

- [ ] **Step 2: Final grep verification**

```powershell
rtk grep "man:" .
rtk grep "man:" .
rtk grep "plugins/man" .
rtk grep "docs/craftpowers" .
rtk grep "using-man" .
```

Expected: 0 matches in all 5 (branding strings in descriptions OK if any remain; verify case-by-case).

- [ ] **Step 3: Commit**

```powershell
git add -A
git commit -m "feat!: rename plugin namespace craftpowers/superpowers -> man

BREAKING CHANGE: Plugin name changed from 'craftpowers' to 'man'.
Skill invocations now use man: prefix (e.g., man:brainstorming).
Junction path: ~/.claude/plugins/man (was ~/.claude/plugins/man).
Docs moved: docs/man/ -> docs/man/.
Skill renamed: using-man -> using-man.

Reinstall required: python scripts/install.py"
```

Expected: Commit succeeds.

---

## Self-Review Notes

- **Spec coverage:** §2.1 manifests = Task 2; §2.2 craftpowers sweep = Tasks 3-4; §2.3 superpowers sweep = Task 5; §2.4 skill rename = Task 6; §2.5 docs rename = Task 7; §2.6 install paths = Task 8; §2.7 not changed (repo URL) — preserved.
- **Order:** manifests first (Task 2), text sweeps before folder renames (Tasks 3-5 before 6-7), install path update last (Task 8) — folder rename invalidates path refs first.
- **Risk Task 5:** Tests reference `man:` in test fixtures. After replace, tests may fail if they exercise legacy compat. Run tests post-rename; expected behavior: tests still validate `man:` prefix (rename = consistent).
- **Task 4 install.py edit:** `man:` colon-suffixed forms only. `craftpowers` plain (e.g. variable names, comments) handled in Task 8 via path replace.
