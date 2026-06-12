# Intent-Driven Development (IDD) — ck + craftpowers glue

Capture WHY / DONE-WHEN / CONSTRAINTS before planning. Intent trumps spec: when implementation details conflict with stated intent, stop and surface the conflict — do not silently follow the spec.

## Tier routing (before /ck:plan)

| Tier | When | What to do |
|------|------|------------|
| **0 — skip** | Bugfix (`/ck:fix`), executing existing plan (`/ck:cook <path>`), trivial/mechanical change | No intent step. Go straight to the ck skill. |
| **1 — inline (default)** | Normal feature work via `/ck:plan` | The first 3 validation questions of `/ck:plan` MUST cover: (1) WHY — problem/value, (2) DONE-WHEN — observable success criteria, (3) CONSTRAINTS — what must not change. Write answers as an `## Intent` section at the top of `plan.md`. No extra round-trip. |
| **2 — full** | Ambiguous goal, large/multi-phase work, or user explicitly asks to brainstorm | Run the `brainstorming` skill (socratic interview) first. Save outcome as `intent-statement.md` in the plan directory, then `/ck:plan` referencing it. |

During implementation and review, check changes against the `## Intent` section (or `intent-statement.md`). Deviation → surface to user, never auto-resolve.

## ck / craftpowers arbitration

ClaudeKit (`/ck:*`) is the PRIMARY pipeline. Craftpowers skills are auxiliary — they never replace a pipeline step.

| Step | Winner | Auxiliary (when) |
|------|--------|------------------|
| Plan | `/ck:plan` | `brainstorming` — Tier 2 only, BEFORE plan |
| Implement | `/ck:cook` | `test-driven-development` — only when user explicitly requests TDD |
| Test | `/ck:test` | — |
| Review | `/ck:code-review` | `adversarial-design` — only when user says "grill me" / asks to stress-test a design |
| Ship / commit | `/ck:ship` | `verification-before-completion` — always allowed as a final evidence check before claiming done |
| Debug | `/ck:debug`, `/ck:fix` | — |

Never run two skills covering the same step in one pass. If unsure which system owns a step, ck wins.
