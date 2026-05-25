---
name: quality-gate
description: Run repo-wide quality checks on changed files before committing. Catches regressions in adjacent code that code-reviewer misses.
---

# Quality Gate

Pre-commit quality gate that scans affected paths — not just the files you edited.

## Usage

```
/man-quality-gate                    # Check all git-changed files
/man-quality-gate src/auth/          # Check specific path
/man-quality-gate --strict           # Add security + type checks
```

## What it checks

| Check | Always | --strict |
|-------|--------|---------|
| Syntax / parse errors in changed files | ✅ | ✅ |
| Import consistency (no broken imports) | ✅ | ✅ |
| Test files exist for changed modules | ✅ | ✅ |
| Adjacent modules that import changed files | ✅ | ✅ |
| Security-sensitive patterns (auth, env, secrets) | ❌ | ✅ |
| Type errors in changed + adjacent files | ❌ | ✅ |
| No TODO/FIXME left in changed lines | ❌ | ✅ |

## How to invoke

When user runs `/man-quality-gate [path] [--strict]`:

### Step 1 — Identify scope

```
git diff --name-only HEAD          # changed files (staged + unstaged)
git diff --cached --name-only      # staged only
```

If path argument given → filter to that path.

### Step 2 — Find adjacent files

For each changed file, use Grep to find other files that import it:
```
grep -r "from ./<changed-file>" src/
grep -r "import.*<changed-module>" src/
```

### Step 3 — Run checks

For each file in scope (changed + adjacent):
1. Read file — check for obvious syntax issues
2. Verify imports resolve (file paths exist)
3. Check test file exists: `<module>.test.ts` or `test_<module>.py`
4. If `--strict`: scan for auth/env/secret patterns

### Step 4 — Dispatch code-reviewer

If scope ≤ 10 files → dispatch `code-reviewer` agent with:
- All changed files as context
- Explicit instruction: "Check for regressions in adjacent modules, not just new code"

If scope > 10 files → warn: "Large diff (N files). Consider running on specific path: `/man-quality-gate src/api/`"

### Step 5 — Report

```
Quality Gate Report
===================
Scope: N changed files + M adjacent files

✅ PASSED — N files checked, 0 issues
❌ FAILED — N issues found:
  src/auth/middleware.ts:45 — imports deleted function getUserById
  src/api/routes.ts — no test file found

Action required before commit: fix issues above
```

### Gate result

- **PASSED** → "Safe to commit. Run `/man-ship` to finalize."
- **FAILED** → list issues, do NOT suggest committing

## Comparison with similar skills

| Skill | Scope | When to use |
|-------|-------|------------|
| `code-reviewer` | Per-PR diff | After implementation |
| `santa-method` | 2-reviewer binary gate | Critical PRs only |
| `quality-gate` | Repo-wide pre-commit | Before every commit on non-trivial changes |
