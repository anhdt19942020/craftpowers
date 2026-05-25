# ECC 5 Features — Mankit Implementation

**Goal:** Add 5 ECC-inspired features to mankit: instinct evolution, hook profile skill, model routing, quality gate, loop checkpoint.

**Version:** 6.58.0 → 6.59.0 (one bump at end)

**Tech stack:** Python (hooks), Markdown (skills/commands)

## Phases (all independent, can run parallel)

| Phase | Feature | Files | Status |
|-------|---------|-------|--------|
| 1 | Instinct Evolution | `skills/instinct-management/SKILL.md` (extend) | [ ] |
| 2 | Hook Profile Skill | `skills/hook-profile/SKILL.md`, `commands/man-hook-profile.md` | [ ] |
| 3 | Model Route | `skills/model-route/SKILL.md`, `commands/man-model-route.md` | [ ] |
| 4 | Quality Gate | `skills/quality-gate/SKILL.md`, `commands/man-quality-gate.md` | [ ] |
| 5 | Loop Checkpoint | `hooks/lib/loop_checkpoint.py`, `skills/loop-checkpoint/SKILL.md`, `commands/man-loop-start.md`, `commands/man-loop-status.md` | [ ] |
| 6 | Version bump | `package.json`, plugin configs | [ ] |

## Detailed phase files

- [Phase 1: Instinct Evolution](phase-01-instinct-evolution.md)
- [Phase 2: Hook Profile Skill](phase-02-hook-profile-skill.md)
- [Phase 3: Model Route](phase-03-model-route.md)
- [Phase 4: Quality Gate](phase-04-quality-gate.md)
- [Phase 5: Loop Checkpoint](phase-05-loop-checkpoint.md)
