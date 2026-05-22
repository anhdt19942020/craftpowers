---
name: multi-persona-predict
description: "5-persona pre-analysis before risky changes — Architect, Security, Performance, UX, Devil's Advocate. Use when: architectural decisions, risky refactors, new dependencies, security-sensitive changes."
phase: THINK
---

# Multi-Persona Predict

5 expert personas independently analyze a proposed change, surface conflicts, produce a consensus verdict.

## When to Use

- Before architectural decisions
- Before refactors touching >10 files
- Before adding a new dependency
- Before security-sensitive changes
- When team is split on approach

## Protocol

### Phase 1 — Independent Analysis

Each persona analyzes the proposed change without seeing others' verdicts.

| Persona | Focus | Key Questions |
|---------|-------|--------------|
| **Architect** | Coupling, extensibility, system fit | Does this create tech debt? Does it fit the architecture? |
| **Security** | Attack surface, data flow, auth boundaries | What can go wrong? What's the blast radius? |
| **Performance** | Latency, memory, scalability | Will this scale? What's the worst-case? |
| **UX** | Dev experience, API ergonomics | Is this intuitive? Will devs misuse it? |
| **Devil's Advocate** | Assumptions, blind spots | What if the premise is wrong? What are we not seeing? |

Each persona outputs:
```
## {Persona} Analysis
**Verdict:** GO | CAUTION | STOP
**Confidence:** 1–5
**Key concern:** {one sentence}
**Recommendation:** {one sentence}
```

### Phase 2 — Conflict Resolution

If verdicts conflict:
1. Identify the specific disagreement points
2. Each conflicting persona states WHY they disagree with the other
3. Find resolution: compromise, added constraint, or escalate to human

### Phase 3 — Final Verdict

| Consensus | Action |
|-----------|--------|
| All GO | Proceed with confidence |
| Majority GO, minority CAUTION | Proceed with noted concerns |
| Any STOP | Do NOT proceed. Address STOP concern first. |
| Mixed CAUTION | Proceed with explicit risk acceptance on record |

## Output Format

```markdown
## Predict Report: {change description}

### Verdicts
| Persona | Verdict | Confidence | Key Concern |
|---------|---------|-----------|-------------|
| Architect | GO | 4 | {concern} |
| Security | CAUTION | 3 | {concern} |
| Performance | GO | 5 | {concern} |
| UX | STOP | 4 | {concern} |
| Devil's Advocate | CAUTION | 3 | {concern} |

### Conflicts
{disagreement + resolution, or "None"}

### Final: {GO | CAUTION | STOP}
{summary recommendation}

### Conditions for GO
- [ ] {specific fix for STOP concern}
- [ ] {specific action for CAUTION concerns}
```

## Modes

| Command | Behavior |
|---------|----------|
| `/man-predict <description>` | Full 5-persona analysis |
| `/man-predict --quick <description>` | Architect + Security + Devil's Advocate only |
| `/man-predict --focus security <description>` | Deep dive on one persona |
