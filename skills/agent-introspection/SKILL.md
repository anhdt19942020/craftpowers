---
name: agent-introspection
description: Use when an agent misbehaves — looping, hallucinating, ignoring instructions, drifting off-task, or rationalizing failure instead of recovering
phase: INVESTIGATE
---

# Agent Introspection

## Overview

Agent misbehavior is not a code bug. It's a reasoning failure. Standard debugging (breakpoints, logs, traces) cannot diagnose why an agent loops, hallucinates, or ignores its instructions.

**Core principle:** Treat agent misbehavior as a system failure with identifiable patterns and recoverable states. Do not retry blindly — diagnose first.

## When to Use

**Primary invocation:** Human partner says "use agent-introspection" when they observe misbehavior. **Secondary:** Agent self-invokes when noticing its own pattern (rare but valuable — naming the pattern breaks the cycle).

Use when an agent (including yourself):
- **Loops** — repeats the same action without progress
- **Hallucinates** — references files, functions, APIs, or state that don't exist
- **Ignores instructions** — has a skill/plan but doesn't follow it
- **Drifts** — starts correctly then gradually deviates from the task
- **Rationalizes** — explains away failure instead of admitting it's stuck
- **False-completes** — claims done when evidence shows otherwise

**Do NOT use when:**
- The problem is a code bug → use `systematic-debugging`
- The agent lost context after compaction → use `session-recovery`
- Context window is filling up → use `context-management`
- Agent reported false success → use `verification-before-completion` (catch) then this skill (diagnose)

## The Four Phases

Complete each phase before proceeding to the next.

---

### Phase 1: Detect — Name the Pattern

Before diagnosing, identify WHICH misbehavior pattern is occurring.

| Pattern | Signal |
|---------|--------|
| Loop | Same tool call repeated 3+ times with same/similar args |
| Hallucination | References to paths/symbols that grep/glob cannot find |
| Instruction ignore | Skill/plan loaded but actions contradict it |
| Drift | Early actions align with task, later actions diverge |
| Rationalization | Long explanations for why something "should work" without evidence |
| False-completion | "Done" claim but deliverable missing, tests not run, or requirements unmet |

**Note:** Patterns overlap — a looping agent often rationalizes, and drift can manifest as repetition. Pick the PRIMARY pattern (the one that started first), not all symptoms.

**Action:** State the pattern explicitly. "I am looping" or "The agent is hallucinating." Naming it breaks the cycle.

---

### Phase 2: Diagnose — Find Root Cause

Each pattern has characteristic root causes:

**Loop causes:**
- Identical error repeating → missing context about WHY it fails
- Trying variations of same approach → no alternative strategy available
- Waiting for state that won't change → incorrect assumption about environment

**Hallucination causes:**
- Operating from training data instead of current codebase state
- Assumed file/API exists based on naming conventions without verifying
- Carried forward a reference from earlier context that was removed/renamed

**Instruction ignore causes:**
- Skill loaded but not re-read at decision point (context decayed)
- Ambiguous instruction — agent chose plausible but wrong interpretation
- Conflicting instructions from multiple sources (CLAUDE.md vs skill vs user)

**Drift causes:**
- Subtask expanded beyond original scope (yak-shaving)
- Interesting tangent pulled attention from primary goal
- Lost track of original objective after deep nesting

**Rationalization causes:**
- Sunk cost — already invested effort in wrong approach
- No clear escalation path — doesn't know it can ask for help
- Optimism bias — "one more try" when approach is fundamentally wrong

**Action:** Identify the specific cause. Be precise — "I hallucinated the function name because I assumed the convention without grepping" not "I made an error."

---

### Phase 3: Recover — Contained Correction

Recovery must be targeted. Do not restart from scratch unless all else fails.

**For loops:**
1. Stop the current approach entirely
2. List what you've tried and why each failed
3. Identify what's DIFFERENT about alternatives you haven't tried
4. If no alternatives exist → escalate to human partner

**For hallucinations:**
1. Identify every claim made without primary-source verification
2. Verify each against actual codebase state (grep, glob, read)
3. Retract incorrect claims explicitly
4. Rebuild only from verified facts

**For instruction ignore:**
1. Re-read the relevant skill/plan RIGHT NOW (not from memory)
2. Identify the specific point where you diverged
3. State what the instruction says vs what you did
4. Resume from the divergence point, not from the beginning

**For drift:**
1. State the original task in one sentence
2. Identify where you branched off
3. Assess: is the branch necessary for the original task?
4. If no → abandon branch, return to task
5. If yes → complete branch minimally, then return

**For rationalization:**
1. State the core assumption that isn't working
2. Acknowledge: "This approach is not converging"
3. Ask: what would I do if I had to start fresh with a different strategy?
4. Escalate to human partner if no alternative strategy exists

---

### Phase 4: Report — Introspection Log

After recovery, produce a brief introspection record. Append to `docs/mankit/journal/YYYY-MM-DD.md` (via journal-writer) or output directly in transcript if no journal is configured:

```
## Introspection: [timestamp]
- **Pattern:** [loop | hallucination | instruction-ignore | drift | rationalization | false-completion]
- **Trigger:** What I was doing when it started
- **Root cause:** Why it happened (one sentence)
- **Recovery:** What I did to fix it
- **Prevention:** What would prevent this next time
```

This log serves two purposes:
1. Human partner understands what happened without needing to read full transcript
2. Pattern recognition — recurring introspections reveal systemic issues

---

## Escalation Rules

Escalate to human partner immediately when:
- Same pattern detected 2+ times in one session
- Recovery didn't work on first attempt
- Root cause is ambiguous instructions from human partner
- No alternative strategy exists

Escalation format:
> I'm stuck. **Pattern:** [name]. **What I tried:** [list]. **Why it failed:** [cause]. **What I need:** [specific ask].

---

## Anti-Patterns

| Don't | Do instead |
|-------|-----------|
| Retry same approach "one more time" | Stop after 2 failures of same strategy |
| Apologize without diagnosing | Name the pattern and cause |
| Restart from scratch | Recover from divergence point |
| Hide the failure in verbose output | State it plainly in 1-2 sentences |
| Blame external factors | Own the reasoning failure |
| Skip Phase 1 (detection) | Always name the pattern first — it breaks the cycle |
