# Multi-Persona Predict

5 expert personas independently analyze a proposed change, surface conflicts, produce consensus verdict.

**Usage:** `/man-predict <description>` | `--quick` (3 personas) | `--focus <persona>`

## When to Use
- Before architectural decisions or refactors touching >10 files
- Before adding a new dependency
- Before security-sensitive changes
- When team is split on approach

## Protocol

### Phase 1 — Independent Analysis (no cross-visibility)

| Persona | Focus | Key Questions |
|---------|-------|--------------|
| **Architect** | Coupling, extensibility | Creates tech debt? Fits architecture? |
| **Security** | Attack surface, auth | What can go wrong? Blast radius? |
| **Performance** | Latency, memory | Will this scale? Worst-case? |
| **UX** | Dev experience, API ergonomics | Intuitive? Will devs misuse it? |
| **Devil's Advocate** | Assumptions, blind spots | What if premise is wrong? |

Each persona outputs:
```
## {Persona} Analysis
**Verdict:** GO | CAUTION | STOP
**Confidence:** 1–5
**Key concern:** {one sentence}
**Recommendation:** {one sentence}
```

### Phase 2 — Conflict Resolution
If verdicts conflict: each conflicting persona states WHY they disagree → find resolution or escalate to human.

### Phase 3 — Final Verdict

| Consensus | Action |
|-----------|--------|
| All GO | Proceed with confidence |
| Majority GO, minority CAUTION | Proceed with noted concerns |
| Any STOP | Do NOT proceed. Address STOP first. |
| Mixed CAUTION | Proceed with explicit risk acceptance |

## Output Format

```markdown
## Predict Report: {change description}
| Persona | Verdict | Confidence | Key Concern |
|---------|---------|-----------|-------------|
| Architect | GO | 4 | {concern} |
| Security | CAUTION | 3 | {concern} |
...

### Final: {GO | CAUTION | STOP}
{summary recommendation}

### Conditions for GO
- [ ] {specific fix for STOP concern}
```
