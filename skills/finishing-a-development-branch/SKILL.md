---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup
phase: SHIP
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Present options → Execute choice → Clean up.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## The Process

### Step 1: Verify Tests

**Before presenting options, verify tests pass:**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**If tests fail:**
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
```

Stop. Don't proceed to Step 2.

**If tests pass:** Continue to Step 1.5.

### Step 1.5: Update Documentation

After tests pass, check if existing documentation needs updating for the work done:

1. **Scan `docs/**/*.md`** for files that document functions, components, or features you modified
2. **Update in-place** — if a function was modified, update its documentation to match the new behavior. If a function was added, add it to the relevant existing doc section.
3. **Do NOT create new doc files** for bug fixes or dated entries (no `fix-2024-05-03.md`). Only update or add to existing docs.
4. **Skip if no relevant docs exist** — if the modified area has no documentation, don't create new docs at this stage.

What to update:
- Modified function signature or behavior → update the doc that describes it
- New function/component added → add to the relevant existing doc section
- Removed function → remove from docs
- Changed API or config → update the doc that references it

What NOT to do:
- Create changelog or fix-log documents
- Create new files for small changes
- Update unrelated docs

If docs were updated, commit them together with the implementation.

### Step 2: Determine Base Branch

```bash
# Try common base branches
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main - is that correct?"

### Step 3: Present Options

Present exactly these 4 options:

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Don't add explanation** - keep options concise.

### Step 4: Execute Choice

#### Option 1: Merge Locally

```bash
# Switch to base branch
git checkout <base-branch>

# Pull latest
git pull

# Merge feature branch
git merge <feature-branch>

# Verify tests on merged result
<test command>

# If tests pass
git branch -d <feature-branch>
```

Then: Cleanup worktree (Step 5)

#### Option 2: Push and Create PR

```bash
# Push branch
git push -u origin <feature-branch>

# Create PR
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

Then: Cleanup worktree (Step 5)

#### Option 3: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't cleanup worktree.**

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation.

If confirmed:
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

Then: Cleanup worktree (Step 5)

### Step 5: Cleanup Worktree

**For Options 1, 2, 4:**

Check if in worktree:
```bash
git worktree list | grep $(git branch --show-current)
```

If yes:
```bash
git worktree remove <worktree-path>
```

**For Option 3:** Keep worktree.

### Step 6: Session Summary

**After merge/PR/cleanup is done, report a session summary.**

Run these commands and compile the results:

```bash
# 1. Files changed in this branch
git diff --stat <base-branch>..HEAD

# 2. RTK token savings (if rtk is installed)
rtk gain

# 3. Missed RTK opportunities (if rtk is installed)
rtk discover
```

For context usage, estimate from the current session transcript (same method as context-tracker hook: total chars / 4).

Present the summary in this format:

```
--- Session Summary ---

Files changed:     <N> files (+<additions> -<deletions>)
Commits:           <N> commits

Context usage:     ~<tokens> tokens (~<pct>% of 200k limit)
Context remaining: ~<remaining> tokens (~<remaining_pct>%)

RTK token savings:
<output of rtk gain — or "rtk not installed" if unavailable>

Missed RTK opportunities:
<output of rtk discover — or "rtk not installed" if unavailable>
```

If `rtk` is not installed or not in PATH, skip the RTK sections and note "RTK not installed — see https://github.com/nicholasgasior/rtk for token savings."

This step is informational only — never block merge/PR on token stats.

## Quick Reference

| Option | Merge | Push | Keep Worktree | Cleanup Branch | Summary |
|--------|-------|------|---------------|----------------|---------|
| 1. Merge locally | ✓ | - | - | ✓ | ✓ |
| 2. Create PR | - | ✓ | ✓ | - | ✓ |
| 3. Keep as-is | - | - | ✓ | - | ✓ |
| 4. Discard | - | - | - | ✓ (force) | ✓ |

## Common Mistakes

**Skipping test verification**
- **Problem:** Merge broken code, create failing PR
- **Fix:** Always verify tests before offering options

**Open-ended questions**
- **Problem:** "What should I do next?" → ambiguous
- **Fix:** Present exactly 4 structured options

**Automatic worktree cleanup**
- **Problem:** Remove worktree when might need it (Option 2, 3)
- **Fix:** Only cleanup for Options 1 and 4

**No confirmation for discard**
- **Problem:** Accidentally delete work
- **Fix:** Require typed "discard" confirmation

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without confirmation
- Force-push without explicit request

**Always:**
- Verify tests before offering options
- Present exactly 4 options
- Get typed confirmation for Option 4
- Clean up worktree for Options 1 & 4 only

## Integration

**Called by:**
- **subagent-driven-development** (Step 7) - After all tasks complete
- **executing-plans** (Step 5) - After all batches complete

**Pairs with:**
- **using-git-worktrees** - Cleans up worktree created by that skill

## Run /man-release first

Before invoking this skill, ensure `/man-release` has been run on the branch and
any **Block** items from the Pre-Ship Report have been fixed. This skill handles
merge / PR / cleanup; it does NOT audit deploy artifacts.

If `/man-release` has not been run, ask the user to run it before continuing.
