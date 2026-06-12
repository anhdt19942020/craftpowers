# Phase 02 — Dedup Overlapping Skills

## Context Links
- Parent: [plan.md](plan.md)
- Depends: Phase 01 (clean 63-skill set)

## Overview
- **Priority:** High | **Status:** ⬜ Pending | **Risk:** Low (git-tracked, revertible)
- Collapse overlap clusters inside mankit's 63 tracked skills. Target ≤ 50 skills. Every catalog entry costs tokens each session (ck lean-catalog principle).

## Key Insights
Overlap clusters found:

| Cluster | Skills | Action |
|---------|--------|--------|
| Review (5) | `automation-review`, `receiving-code-review`, `requesting-code-review`, `quality-gate`, `security-review` | Keep `security-review` (distinct domain, 17+ rule files). Merge `receiving`+`requesting` → one `code-review-workflow`. Keep `quality-gate` (repo-wide gate ≠ diff review). Fold `automation-review` rule files into review references. |
| Debug (2) | `systematic-debugging`, `debug-flight-recorder` | Keep both BUT flight-recorder becomes `references/` extension of systematic-debugging if it's only a logging addon — inspect first. |
| Adversarial/predict (3) | `gan-adversarial`, `multi-persona-predict`, `adversarial-design` | Overlapping personas-attack pattern. Merge into one `adversarial-review` with modes, or keep `adversarial-design` (design-time) + fold gan into it. |
| Planning (3) | `writing-plans`, `executing-plans`, `subagent-driven-development` | Keep all 3 (distinct lifecycle stages) but slim in Phase 3. |
| Meta/self (4) | `agent-introspection`, `instinct-management`, `behavioral-compliance`, `conversation-analyzer` | Niche meta-skills, rarely fire. Candidate cuts — check `man-stats` telemetry for usage; cut never-used. |
| Routing (2) | `using-man`, `man-assess` | ck pattern: one routing map. Merge man-assess quiz INTO using-man as a section. |
| Misc twins vs ck | `cook` (mankit) vs ck `cook`; `research-playbook` vs ck `research`; `scenario-saturation` vs ck `ck-scenario`; `autoresearch-loop` vs ck `ck-autoresearch` | mankit = standalone plugin → KEEP mankit originals (they ship with plugin). No cut, but rename ambiguous `cook` → consider `man-cook` skill id to avoid catalog collision when both installed. |

## Requirements
- Decisions on "Misc twins" cluster depend on unresolved Q2 (standalone publish vs personal kit) — confirm with owner before cutting.
- Telemetry check (`/man-stats`) before cutting meta-skills.

## Related Code Files
- Modify/merge: skills listed above; `skills/using-man/SKILL.md`
- Update: `rules/agent-dispatch.md`, `hooks/auto-dispatch-rules.json` (references to merged skills)
- Delete: merged-away skill dirs

## Implementation Steps
1. Run `/man-stats` → usage telemetry; mark never-used skills.
2. Confirm cluster decisions with owner (esp. meta-skills + twins).
3. Merge review cluster: create `code-review-workflow`, move rule files to `references/`.
4. Merge man-assess → using-man.
5. Grep all skills/commands/agents/hooks for renamed/deleted skill ids; fix references.
6. Bump plugin version, update README skill table.

## Todo List
- [ ] Telemetry check
- [ ] Owner confirms cut list
- [ ] Review cluster merge
- [ ] Adversarial cluster merge
- [ ] Routing merge (man-assess → using-man)
- [ ] Meta-skill cuts
- [ ] Reference integrity grep
- [ ] Version bump

## Success Criteria
- ≤ 50 tracked skills, zero dangling references (`grep -r` for deleted ids = 0 hits in skills/commands/agents/hooks/rules)
- Plugin loads clean: `claude plugin validate` or man-check passes

## Risk Assessment
- Dangling skill references in hooks/dispatch rules → step 5 grep sweep mandatory.
- Cutting a skill user actually uses → telemetry + owner confirmation gates.

## Security Considerations
- None.

## Next Steps
- Phase 3 slims survivors.
