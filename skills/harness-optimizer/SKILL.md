---
name: harness-optimizer
description: Audit Mankit harness config (hooks, skills, profiles, agents) and surface the top leverage points for improving agent completion quality. Read-only by default — propose changes, apply only when user approves.
---

# Harness Optimizer

**Announce at start:** "Đang chạy harness audit theo man:harness-optimizer."

## Usage

```
/man-harness-optimizer [--apply]
```

- Default: audit-only — score all dimensions, surface top 3 leverage points, propose changes
- `--apply`: after presenting proposals, ask user which to apply, then implement approved ones

## Protocol

### Phase 1: Baseline Scorecard

Scan these paths and score each dimension 1–5:

```
hooks/claude/        # event coverage
hooks/lib/           # gate libs
agents/              # agent quality
skills/              # skill routing
tests/               # test coverage
```

| Dimension | What to check |
|-----------|--------------|
| **Hook coverage** | Are PreToolUse, PostToolUse, Stop, StopFailure, SessionStart, SubagentStop, UserPromptSubmit, PreCompact, PostCompact all present in `hooks/claude/`? |
| **Gate completeness** | Do all hooks call `is_gate_active()` before running their gates? Check `hooks/claude/*.py` for `is_gate_active` usage. |
| **Profile fit** | Does the active profile match project needs? Run: `python -c "from hooks.lib.hook_profiles import get_active_profile, get_profile_gates; import json; print(get_active_profile()); print(json.dumps(get_profile_gates(), indent=2))"` |
| **Skill routing** | Does `skill_resolver` resolve skills correctly? Run: `python -c "from hooks.lib.skill_resolver import resolve_skill; print(resolve_skill('systematic-debugging'))"` |
| **Context injection** | Does `subagent_init.py` exist and inject context into SubagentStart? |
| **Agent quality** | Run: `grep -rL "Security Baseline" agents/` — any output = agents missing baseline |
| **Test coverage** | For each `hooks/lib/<name>.py`, check if `tests/lib/test_<name>.py` or `tests/test_<name>.py` exists |

Compute overall baseline: `sum(scores) / (5 × dimension_count) × 100` = percentage.

### Phase 2: Identify Top 3 Leverage Points

Rank dimensions by `gap × impact`:
- **gap** = 5 − current_score
- **impact**: HIGH = affects every agent run / security / correctness; MEDIUM = affects quality/observability; LOW = nice-to-have

Select top 3. For each, write:
```
## Leverage Point N: <name>
Current: X/5 | Target: Y/5
Problem: [1-2 sentences]
Proposed change: [file + what to change]
How to measure: [what improves after fix]
Reversible: yes/no
```

### Phase 3: Propose Changes (always)

Show exact diffs or code for each proposed change. User can approve/reject each one.

### Phase 4: Apply (only with --apply or user says yes)

For each approved change:
1. Apply with Edit/Write tools
2. Run affected tests: `python -m pytest tests/ -q`
3. Report pass/fail
4. If tests fail → revert immediately, report

## Output Format

End with the structured block:

```
---
HARNESS-AUDIT
BASELINE: <N>%
TOP-3-LEVERAGE:
  1. <dimension> — gap <X>, impact <HIGH|MEDIUM|LOW>
  2. <dimension> — gap <X>, impact <HIGH|MEDIUM|LOW>
  3. <dimension> — gap <X>, impact <HIGH|MEDIUM|LOW>
PROPOSED-CHANGES: <count>
VERDICT: HEALTHY (≥80%) | NEEDS-ATTENTION (<80%)
---
```

## When to use

- After adding new hooks or skills (check coverage)
- When agents produce low-quality output or lose context
- Periodic health check after major version bumps
- Before a release to catch harness regressions
