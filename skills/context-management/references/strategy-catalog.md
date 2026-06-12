## Context Management Strategy Catalog

### 4-Bucket Strategy (detailed)

#### 1. WRITE (Scratchpad)
Use `/btw` for lightweight inline notes that don't need permanent storage:
```
/btw Task 3 complete. Next: Task 4 (auth middleware). Branch: feature/auth. Key decision: use interface X not Y per reviewer.
```
Survives compact if included in compact prompt. Zero-cost to write.

#### 2. SELECT (Retrieval)
Re-read source files after compact instead of keeping them in context:
```bash
# After compact, re-read what matters:
cat plans/feature-plan.md          # source of truth for tasks
git log --oneline base..HEAD       # what was already done
git diff HEAD~3 -- src/auth/       # recent changes to relevant area
```
Source files are always fresh; context copies go stale.

#### 3. COMPRESS (Summarization)
Before compacting, write a dense summary note:
```
/compact Keep: executing plan at plans/auth-plan.md via subagent-driven-development.
Tasks 1-3 complete (validate.ts, rate-limit.ts, audit.ts). Next: Task 4 (JWT refresh).
Branch: feature/auth. Worktree: .worktrees/auth-refactor.
Key decisions: use RefreshToken interface (not string), 15min access / 7day refresh TTL.
Reviewer approved tasks 1-3 with no critical issues.
```

#### 4. ISOLATE (Sub-agents)
Route large-output work to subagents so raw bytes never enter controller context:
```
# ❌ Read 500-line log into context
cat build.log  # → 500 lines in your context

# ✅ Delegate analysis to subagent
Agent(description="Analyze build log", prompt="Read build.log and report: error count, root cause of first error, files involved. Return a 5-line summary.")
# → 5 lines in your context
```

### Proactive Context Hygiene Techniques

**Technique 1: File-reference over file-inclusion**
Instead of pasting file content, reference it and re-read on demand:
```
# ❌ Paste 200 lines of config
Here's the full webpack config: [200 lines]

# ✅ Reference path, read when needed
Config is at webpack.config.ts. I'll read it when relevant.
```

**Technique 2: Diff over full file**
When reviewing changes, use git diff rather than reading entire files:
```bash
# Focused: only changed lines
git diff HEAD~1 -- src/auth/validate.ts

# Not: re-read entire 300-line file to see a 10-line change
```

**Technique 3: Targeted reads with offset/limit**
```bash
# Read only the relevant section
head -n 80 src/auth/validate.ts | tail -n 40  # lines 40-80
```

**Technique 4: Summarize before continuing**
When a long review loop produces many findings, compress before next dispatch:
```
# After 3 rounds of review findings, write summary:
/btw Review loop summary: 3 issues found and fixed in validate.ts (N+1 query, missing null check, wrong HTTP status). All resolved. Quality reviewer approved.
# Then dispatch next task with only the summary
```

### Decision: Compact vs Subagent vs Continue

| Situation | Action | Why |
|-----------|--------|-----|
| Context 40-60%, steady work ahead | Continue, add `/btw` notes | Not urgent yet |
| Context 60-75%, tasks remaining | Controlled compact with summary | Buy room before it's forced |
| Context 75%+, critical work | Compact NOW with full state note | Auto-compact loses more |
| Single large-output task (logs, diffs) | Subagent for that task | Keep raw bytes out |
| Repeated file reads for same file | Stop re-reading; use reference | Each read costs |
| Post-compact: lost task state | Re-read plan file from disk | Source of truth |

### Uncommitted Code at Critical Threshold

If context hits 85%+ with uncommitted work:

```bash
# 1. Commit current state immediately
git add -A
git commit -m "wip: context threshold — saving state before compact"

# 2. Note what was in progress
/btw WIP commit at [sha]. Was implementing: [task description]. Next step: [specific action].

# 3. Compact with that context
/compact Keep: WIP on [task]. Committed at [sha]. Next: [specific action]. Plan: [path].

# 4. After compact, verify state
git log --oneline -5
git status
```

Never let unsaved work get lost to auto-compact.

### Workflow-Specific Additions

**subagent-driven-development:** Compact after every 3 tasks. Include: plan path, completed task numbers, next task number, key reviewer decisions.

**agent-teams:** Compact when lead context hits 60%. Include: team name, plan-state.yaml path, each teammate's last known status.

**long research sessions:** Write incremental `/btw` notes after each source. Compact after 5-6 sources with a synthesis note.
