# PRD: Competing-Hypothesis Mode for `/man-fix`

**Date:** 2026-05-14
**Owner:** anhdt19942020
**Status:** Draft
**Target version:** 6.14.0 (minor — new behavior in existing command)

## Problem

Hard bugs today take N serial rounds of `/man-fix`:

1. User reports intermittent crash.
2. `debugger` picks hypothesis A, traces, proposes fix, runs tests.
3. Bug still occurs → user reports again.
4. `debugger` picks hypothesis B, traces, fix, tests.
5. Repeat until hit.

Each round costs ~5–10 min wall time. Worse: a single debugger has **confirmation bias** — once it picks hypothesis A, it rationalizes evidence to fit, missing the real cause.

Class of bugs this hits hardest:
- Intermittent failures (race, async timing, external state)
- Bugs spanning multiple subsystems (could be DB, could be cache, could be middleware)
- Bugs where previous fix made it worse (the prior fix targeted the wrong cause)

## Solution

When triage classifies a bug as "complex with multiple plausible causes", `/man-fix` enters **Competing-Hypothesis Mode**:

1. Lead enumerates 3 **orthogonal** hypotheses (different root-cause classes).
2. Spawn 3 `debugger` teammates in parallel, each assigned exactly one hypothesis.
3. Each hypothesis-debugger traces independently — does NOT see siblings' work.
4. **Winner-first**: the first to produce hard evidence (failing reproducer + line that causes it) reports to lead. Siblings auto-shutdown.
5. **Convergence case**: if multiple debuggers report root-cause evidence within the same coordination round, lead synthesizes — the bug may be a combination (e.g., race + retry amplification).
6. Lead spawns `code-reviewer` to review winner's fix. Standard hub-and-spoke flow from 6.12.0.

## Goals

| Metric | Today | Target |
|---|---|---|
| Wall time on hard bugs | 15–45 min serial | 5–10 min parallel |
| False-fix rate (regression within 24h) | High — single-debugger bias | Low — orthogonal hypotheses reduce class blindness |
| Token cost on hard bugs | 1x serial × N rounds | 3x parallel × 1 round (typically equal or cheaper) |
| Token cost on easy bugs | 1x | 1x — unchanged (mode does not activate) |

## Non-goals

- Not changing simple-bug path (`/man-fix` triage already handles single-file/clear-error case).
- Not implementing automatic hypothesis generation — lead's Opus judgment picks hypotheses.
- Not adding a new command. This is a mode inside `/man-fix`.

## Activation criteria

Lead triggers Competing-Hypothesis Mode when **any two** of the following signals from the bug description:

- "intermittent", "sometimes", "flaky", "race"
- "not sure why", "could be X or Y"
- "fix didn't work", "regression", "tried N things"
- Spans 3+ files or 2+ subsystems (frontend + backend, app + DB, etc.)
- Bug has been open >7 days

If only one signal: default single-debugger mode.
If five+ signals: ask human partner before spawning (escalation per `## Failure & Timeout Policy` in agent-teams).

## Workflow

### Step 1 — Triage (modified)

Existing triage adds new branch:

```
SIMPLE  → fix directly in this session
COMPLEX (single hypothesis) → existing 1×debugger + 1×code-reviewer team
COMPLEX (multi-hypothesis)  → NEW: 3×debugger + 1×code-reviewer team
```

Tell user:
> "Multiple plausible causes — spawning 3 parallel `debugger` debuggers (hypotheses: A / B / C). Winner-first; siblings shut down on confirmation."

### Step 2 — Lead enumerates hypotheses

Lead must produce **3 orthogonal hypotheses**. Orthogonality rule:

> Two hypotheses are orthogonal if confirming one does NOT increase the prior of the other.

Bad (not orthogonal): `H1 = race on cart state`, `H2 = race on checkout state`. Both are "race". One trace style.

Good (orthogonal): `H1 = race condition`, `H2 = API timeout/retry`, `H3 = DB connection pool exhaustion`. Different evidence, different traces, different fixes.

Lead writes each hypothesis as a task description with:
- Hypothesis statement
- Files to investigate
- Evidence that would confirm
- Evidence that would rule out

### Step 3 — Spawn 3 debuggers + 1 reviewer

```
TaskCreate × 3 (one per hypothesis)
TaskCreate × 1 (review winner's fix, blockedBy 3 hypotheses tasks via OR — see Open Questions)
TaskUpdate addBlockedBy as needed

Agent({ name: "hyp-A", subagent_type: "man:debugger", model: "sonnet", ... })
Agent({ name: "hyp-B", subagent_type: "man:debugger", model: "sonnet", ... })
Agent({ name: "hyp-C", subagent_type: "man:debugger", model: "sonnet", ... })
```

Each debugger gets a prompt like:

```
You are investigating ONE specific hypothesis: <H>.
Files: <list>
Evidence to confirm: <criteria>
Evidence to rule out: <criteria>

Do NOT broaden scope. If you rule out your hypothesis, SendMessage lead
"RULED OUT: <reason>" and stop. Do NOT investigate sibling hypotheses.
If you confirm: write reproducer + fix, run tests, TaskUpdate completed,
SendMessage lead "CONFIRMED: <root cause + fix summary>".
```

### Step 4 — Lead monitors, declares winner

Per `## Lead Loop` from agent-teams 6.12.0:

- Read incoming messages each round.
- **First CONFIRMED with reproducer wins**. Lead immediately:
  - `SendMessage` shutdown to losers
  - Spawn `code-reviewer` to review winner's fix
- If all 3 report RULED OUT: hypotheses were wrong. Ask human partner. Do NOT silently spawn more.
- If 2+ report CONFIRMED in same round: synthesize — the bug is multi-cause. Lead writes a combined task description, may spawn `code-reviewer` to review both fixes.
- Coordination round cap = 10. If no winner by then: escalate.

### Step 5 — Review + DoD + shutdown

Standard 6.12.0 flow. Reviewer APPROVE → bump → commit.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| 3 debuggers all wrong (hypothesis blind spot) | If all RULED OUT, escalate to human — do NOT auto-spawn more |
| Token cost when bug was actually simple | Activation criteria (2-signal threshold) prevents accidental trigger |
| Debuggers contaminate each other (peer DMs) | Hub-and-spoke enforced per agent-teams 6.12.0; debuggers know not to peer-DM |
| Winner's fix has bug from rushing | `code-reviewer` review gate (DoD requires APPROVE) |
| Hypothesis selection bias by lead | Lead must enumerate **before** seeing repro logs; document hypotheses in TaskList |
| Convergent-evidence case (2 confirmed) missed | Lead waits one extra coordination round after first CONFIRMED before shutting down siblings |

## Open questions

1. **Wait window after first CONFIRMED**: should lead immediately shutdown siblings, or wait 1 round in case of convergent evidence? Default: wait 1 round. Tradeoff: latency vs. catching multi-cause bugs.

2. **Hypothesis count**: always 3, or adapt? Default: 3. Two is too few for orthogonality; four+ has diminishing returns and 4x cost.

3. **Model selection**: all 3 `debugger` on Sonnet (default), or Opus for one as "tiebreaker"? Default: all Sonnet. Lead Opus does synthesis.

4. **Task blockedBy graph**: review task should unblock when ANY hypothesis completes, not ALL. Current TaskUpdate `addBlockedBy` is AND semantics. Workaround: lead creates review task AFTER winner declared, not upfront. Implementation: review task created in Step 4, not Step 3.

5. **Activation prompt**: should `/man-fix` ask the user "I see N signals of complex bug — want me to spawn 3 parallel debuggers?" or auto-trigger? Default: ask if signals=2; auto if signals=3+. Tunable.

## Implementation plan

### Phase 1: Edit `commands/man-fix.md`

1. Expand Step 1 (Triage) — add SIMPLE / COMPLEX-single / COMPLEX-multi branches with signal criteria.
2. New Step 2a (only in COMPLEX-multi path) — hypothesis enumeration template.
3. Modify Step 3 — spawn 3 debuggers; specify orthogonality rule.
4. Modify Step 4 — winner-first protocol; wait-window for convergent evidence; spawn reviewer on winner declared.
5. Step 5 unchanged.

Estimated diff: +60 lines to man-fix.md.

### Phase 2: Update `agents/debugger.md` Team Mode

Add a "Hypothesis mode" sub-section to Team Mode block:

> If your task description states a specific hypothesis to investigate:
> - Investigate ONLY that hypothesis
> - Do NOT broaden scope
> - SendMessage lead "RULED OUT: <reason>" or "CONFIRMED: <evidence>"
> - Do NOT peer-DM other debuggers

Estimated diff: +12 lines to debugger.md.

### Phase 3: Update `skills/agent-teams/SKILL.md` Coordination Patterns

The existing "Competing-Hypothesis Debug" example (lines around 257–269) gets:
- Winner-first protocol spelled out
- Wait-window rule
- Cross-reference to `/man-fix` command

Estimated diff: +25 lines.

### Phase 4: Tests

mankit doesn't have agent-behavior tests today. Verification = **2 real bugs**:
- Reproduce a known historical intermittent bug (find one in git log) — run new `/man-fix` mode against it, measure wall time vs. estimated serial time
- Inject a synthetic race-condition bug into a test repo, run `/man-fix`, verify hypothesis enumeration is orthogonal

Document results in `docs/journal/2026-05-XX-competing-hypothesis-eval.md`.

### Phase 5: Documentation

Update `README.md`, `RELEASE-NOTES.md`. Skip CLAUDE.md (already references man-fix).

## Success criteria

- 3 parallel `debugger` spawn on a 2-signal bug, all with orthogonal hypotheses
- Winner-first works: losers shutdown within 1 round of CONFIRMED
- Convergent-evidence case detected when 2 debuggers CONFIRM in same round
- DoD gate from 6.12.0 still enforced (reviewer APPROVE required)
- Single-debugger path unchanged on simple bugs (no regression)
- Wall time on the eval bug ≤ 1/2 the serial baseline

## Out of scope (future)

- Auto-hypothesis generation (LLM-suggested orthogonal classes)
- More than 3 hypotheses (4-fan, 5-fan)
- Replay of historical bug fixes to data-driven select hypotheses
- Integration with hook auto-dispatch (PostToolUse on test fail → competing-hypothesis mode)
