# Phase 05 — Hooks Diet: Default Minimal Profile, Consolidate Scripts

## Context Links
- Parent: [plan.md](plan.md)
- Depends: Phase 04 (dispatch rules settled)
- Lesson source: global ~/.claude cleanup 2026-06-12 — per-event hook spawns on Windows added latency to EVERY Edit/Write/Read; cutting them was the single biggest UX win

## Overview
- **Priority:** Medium | **Status:** ⬜ Pending | **Risk:** Medium (quality gates loosened)
- ~20 Python hook scripts (auto-dispatch, cost-tracker, context-tracker, security-gate, credential-scanner, permission-request-gate, config-change-gate, stop-failure, session-summary, compact-hooks, subagent-init…) + 3 profiles (minimal/standard/strict). README claims "4 hooks". Each PreToolUse Python spawn on Windows ≈ 100-300ms tax per tool call.

## Key Insights
- Profile system already exists (`man-hook-profile`) — leverage it instead of deleting scripts.
- Keep always-on (cheap, safety-critical): `credential-scanner` (PreToolUse on Write/Bash), `security-gate`.
- Move to standard/strict only: `cost-tracker`, `context-tracker`, `session-summary`, `auto-dispatch` (proactive dispatch of 10+ agents is strict-tier behavior), `permission-request-gate`, `config-change-gate`.
- `stop-failure`, `compact-hooks`, `session-start`: evaluate per-event cost; SessionStart-only hooks are cheap (once per session) — keep.
- Consolidation: merge single-purpose PreToolUse scripts into one dispatcher script with internal routing (one process spawn instead of N per event). `hooks/run-hook.cmd` + `hooks.json` already centralize entry — extend.

## Requirements
- Default profile = **minimal**: SessionStart hooks + credential-scanner + security-gate only.
- No safety regression: credential/security gates never disabled in any profile.
- Hook tests (added 6.54.0) stay green across all 3 profiles.

## Related Code Files
- Modify: `hooks/hooks.json`, profile definitions, possibly merge `hooks/*.py` into dispatcher
- Test: existing hook tests + `man-check` smoke tests

## Implementation Steps
1. Measure baseline: time a no-op Edit with current default profile (hook latency budget).
2. Re-tier hooks per Key Insights table; set default profile minimal.
3. Consolidate PreToolUse scripts behind single dispatcher entry (one spawn/event).
4. Run hook tests per profile; run `man-check`.
5. Re-measure latency; document delta in README.

## Todo List
- [ ] Baseline latency measurement
- [ ] Re-tier profiles
- [ ] Default → minimal
- [ ] Dispatcher consolidation
- [ ] Tests green ×3 profiles
- [ ] Latency delta documented

## Success Criteria
- Default-profile PreToolUse spawns ≤ 2 scripts per event (was: up to 5+)
- Measured latency reduction documented
- credential-scanner + security-gate active in all profiles

## Risk Assessment
- Users relying on strict-tier gates silently lose them on default → man-check prints active profile + what's off.
- Dispatcher consolidation bug disables a gate → hook tests cover each gate individually.

## Security Considerations
- credential-scanner and security-gate are non-negotiable in every profile — explicit assertion in hook tests.

## Next Steps
- Phase 6 docs sync reflects final hook story.
