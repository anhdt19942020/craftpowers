# Phase 04 — Rationalize Agents (18→~10) and Commands (23→~14)

## Context Links
- Parent: [plan.md](plan.md)
- Depends: Phase 02 (skill cuts settle which wrappers die)

## Overview
- **Priority:** Medium | **Status:** ⬜ Pending | **Risk:** Medium (dispatch rules rewire)
- Agent sprawl: 18 agents, all wired into proactive auto-dispatch (commit 6.58.0) — heavy trigger surface. Command sprawl: 23 commands, several are thin "invokes skill X" wrappers duplicating what skill auto-discovery already does.

## Key Insights

**Agents — merge candidates (18 → ~10):**

| Cut/merge | Into | Why |
|-----------|------|-----|
| `comment-analyzer` | `code-reviewer` (review dimension) | Single-purpose lens, not a persona |
| `silent-failure-hunter` | `code-reviewer` (review dimension) | Same |
| `refactor-cleaner` | `implementer` or quality-gate flow | Post-edit cleanup = implementation concern |
| `secure-reviewer` | keep OR fold into `code-reviewer --security` | Distinct OWASP depth — owner call |
| `final-approver` | `code-reviewer` final pass | Approval = review output, not separate agent |
| `harness-optimizer` | keep as skill only, drop agent twin | Skill exists (`harness-optimizer/SKILL.md`) — duplicate surface |
| `deep-researcher` | keep | Distinct capability |
| `architect`, `debugger`, `codebase-explorer`, `test-engineer`, `release-prep`, `doc-writer`, `journal-writer`, `implementer`, `quick-fix`, `automation-tester` | keep | Core, distinct roles |

**Commands — thin wrappers to cut (skill auto-discovery covers them):**
- `man-brainstorm` (→ brainstorming skill), `man-plan` (→ writing-plans), `man-ship` (→ finishing-a-development-branch): keep ONLY if they add args/gates beyond invoke; else delete, document trigger phrases in using-man.
- `man-assess` → merged into using-man (Phase 2).
- `man-generate-codex` → cut if Codex CLI unused (unresolved Q1).
- `man-loop-start`/`man-loop-status` → consider merging into one `man-loop` with subcommands.
- Keep: `man-cook`, `man-check`, `man-debug`, `man-quick`, `man-quality-gate`, `man-release`, `man-eval`, `man-stats`, `man-journal`, `man-hook-profile`, `man-model-route`, `man-routines`, `man-explore`, `man-level`.

**ck pattern adopted:** description format "MUST BE USED when / DO NOT USE when" — already on `journal-writer`, `quick-fix`; extend to all surviving agents (most currently use multiline `description: |` without trigger guidance visible in first line).

## Requirements
- `hooks/auto-dispatch-rules.json` + `rules/agent-dispatch.md` + `agents/roles.json` updated atomically with agent cuts.
- Review-dimension merges preserve the cut agents' checklists (move content into code-reviewer references, not delete).

## Related Code Files
- Modify: `agents/code-reviewer.md`, `agents/roles.json`, `hooks/auto-dispatch-rules.json`, `rules/agent-dispatch.md`, `commands/*` survivors
- Delete: merged agent files, cut command files

## Implementation Steps
1. Inventory wrapper commands: diff each command body vs its skill — wrapper = body adds nothing.
2. Owner confirms cut lists (agents + commands).
3. Merge agent checklists into code-reviewer references; delete agent files.
4. Rewrite auto-dispatch-rules.json for surviving set; run hook tests (`tests/` has hook tests since 6.54.0).
5. Normalize all agent descriptions to MUST/DO-NOT-USE format.
6. Delete cut commands; update README + using-man.

## Todo List
- [ ] Wrapper diff audit
- [ ] Owner confirmation
- [ ] Agent merges + deletions
- [ ] Dispatch rules rewrite + hook tests green
- [ ] Description normalization
- [ ] Command deletions

## Success Criteria
- ≤ 11 agents, ≤ 15 commands
- `man-check` passes; hook tests green; no dispatch rule references a deleted agent

## Risk Assessment
- Auto-dispatch regression (agent named in rules but deleted) → hook tests + man-check gate.
- Lost checklist knowledge from merged agents → verbatim moves into references.

## Security Considerations
- Keep OWASP checklist content regardless of secure-reviewer merge decision.

## Next Steps
- Phase 5 hooks diet.
