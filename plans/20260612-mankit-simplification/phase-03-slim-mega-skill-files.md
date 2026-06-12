# Phase 03 — Slim Mega SKILL.md Files (ck Progressive Disclosure)

## Context Links
- Parent: [plan.md](plan.md)
- Depends: Phase 02 (don't slim files being deleted/merged)
- Pattern source: ClaudeKit skills — SKILL.md = workflow + gates only; detail in `references/*.md` loaded on demand

## Overview
- **Priority:** Medium | **Status:** ⬜ Pending | **Risk:** Medium (content moves can break internal anchors)
- Split oversized SKILL.md bodies. When a skill activates, the whole SKILL.md enters context — 28KB ≈ 7k tokens for one activation.

## Key Insights
Targets (> 10KB):

| Skill | Size | Split strategy |
|-------|------|----------------|
| `subagent-driven-development` | 28.3KB | Keep dispatch workflow + two-stage review gates; move per-scenario walkthroughs, prompt templates → `references/` |
| `agent-teams` | 27.3KB | Keep team lifecycle + roles; move templates, message protocols → `references/` |
| `writing-skills` | 22.6KB | Keep TDD-for-skills loop; move examples, anti-patterns catalog → `references/` (has `examples/` dir already) |
| `writing-plans` | 17.1KB | Keep plan structure + gates (incl. new prp-plan patterns from 6.60.3); move section templates → `references/` |
| `browser-testing-with-devtools` | 12.6KB | Move selector/CDP cookbooks → `references/` |
| `brainstorming` | 12.3KB | Keep HARD-GATE + question flow; move technique catalog → `references/` |
| `systematic-debugging` | 11.4KB | 12 companion md files exist already — push detail there |
| `frontend-ui-engineering` | 10.7KB | Move stack-specific guidance → `references/` |
| `api-and-interface-design` | 10.4KB | Move pattern catalog → `references/` |
| `dispatching-parallel-agents` | 10.2KB | Move examples → `references/` |
| `context-management` | 10.2KB | Move strategies catalog → `references/` |
| `test-driven-development` | 10.0KB | Move language-specific examples → `references/` |

## Requirements
- Body target: < 10KB each (ideal < 8KB)
- HARD-GATE / MANDATORY-GATE blocks stay in SKILL.md body (gates must always load — superpowers heritage, do not bury in references)
- Every moved chunk referenced from body: `See references/<file>.md for X`

## Related Code Files
- Modify: 12 SKILL.md files above
- Create: `references/*.md` per skill

## Implementation Steps
1. Per skill: classify sections → {workflow, gates, triggers} stay; {examples, templates, catalogs, walkthroughs} move.
2. Create `references/`, move content verbatim (no rewriting — reduces review burden).
3. Insert pointer lines in body.
4. Verify: no broken relative links (`grep -o '](\./[^)]*)'` check), size check `find skills -name SKILL.md -size +10k` → only justified exceptions.
5. Run skill evals where fixtures exist (`evals/` has brainstorming, systematic-debugging, etc.) via `/man-eval`.

## Todo List
- [ ] subagent-driven-development split
- [ ] agent-teams split
- [ ] writing-skills split
- [ ] writing-plans split
- [ ] 8 remaining 10-13KB skills
- [ ] Link integrity check
- [ ] Evals on changed skills with fixtures

## Success Criteria
- `find skills -maxdepth 2 -name SKILL.md -size +10k | wc -l` ≤ 2 (justified exceptions documented)
- Evals pass same as before split

## Risk Assessment
- Gate dilution: if a gate block accidentally moves to references it stops auto-loading → checklist: grep `HARD-GATE\|MANDATORY` in body before/after, counts must match.
- Eval regression → run evals, revert per-skill on failure.

## Security Considerations
- None.

## Next Steps
- Phase 4 cuts agents/commands referencing slimmed skills.
