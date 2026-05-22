---
name: scenario-saturation
description: "Systematic edge-case generation across 12 dimensions with novelty detection. Use when: writing tests, security review, API hardening, pre-launch coverage checks."
phase: THINK
---

# Scenario Saturation

Generate edge cases across 12 dimensions until novelty is exhausted.

## When to Use

- Writing tests for a new feature
- Reviewing API surface for gaps
- Security-sensitive flows
- Pre-launch hardening
- "What could go wrong?" sessions

## 12 Dimensions

| # | Dimension | Examples |
|---|-----------|----------|
| 1 | **Boundary values** | Empty, null, max int, zero, negative |
| 2 | **Timing/ordering** | Concurrent, out-of-order, timeout, retry storm |
| 3 | **State transitions** | Invalid state, stale state, partial update |
| 4 | **Permissions** | No auth, expired token, wrong role, privilege escalation |
| 5 | **Data volume** | Empty collection, single item, millions of records |
| 6 | **Network** | Timeout, partial response, DNS failure, retry storm |
| 7 | **User behavior** | Double-click, back button, tab-switch, copy-paste |
| 8 | **Integration** | Downstream service down, schema mismatch, version skew |
| 9 | **Environment** | Disk full, OOM, clock skew, different timezone |
| 10 | **Encoding** | Unicode, emoji, RTL text, null bytes, injection attempts |
| 11 | **Rollback** | Mid-transaction failure, partial rollback, idempotency |
| 12 | **Observability** | Missing logs, metric overflow, alert fatigue |

## Protocol

### One-Shot Mode (default)

Generate 3–5 scenarios per dimension. Output immediately. No iteration.

```
/man-scenario <feature description>
```

### Saturation Mode

Iterate until no new scenarios emerge across 2 consecutive rounds.

```
/man-scenario --saturate <feature description>
```

1. Generate scenarios for current dimension
2. Classify each: **New** | **Variant** | **Duplicate** | **Out-of-scope**
3. Keep only New and Variant
4. Rotate to next dimension after 3 consecutive iterations on same one
5. STOP when 2 consecutive iterations yield 0 New

### Novelty Detection

| Classification | Rule | Action |
|----------------|------|--------|
| **New** | Different trigger AND different failure mode | Keep |
| **Variant** | Same trigger, different failure mode | Keep |
| **Duplicate** | Same trigger AND same failure mode | Discard |
| **Out-of-scope** | Unrelated to feature under test | Discard |

## Output Format

```markdown
## Scenarios: {feature name}

### Dimension 1: Boundary Values
| # | Scenario | Expected Behavior | Severity |
|---|----------|-------------------|----------|
| 1 | Empty username | Validation error, not crash | Medium |
| 2 | Username = 10,000 chars | Truncate or reject with clear error | High |

### Coverage Matrix
| Dimension | Scenarios | Status |
|-----------|-----------|--------|
| Boundary | 5 | Saturated |
| Timing | 4 | Saturated |
| Permissions | 3 | More possible |
| ... | | |

### Summary
- Total scenarios: {n}
- Dimensions covered: {n}/12
- Saturated: {n}/12
```

## Modes

| Command | Behavior |
|---------|----------|
| `/man-scenario <feature>` | One-shot, 3–5 per dimension |
| `/man-scenario --saturate <feature>` | Iterate until novelty exhausted |
| `/man-scenario --dimension timing <feature>` | Deep dive one dimension only |
| `/man-scenario --for-tests <feature>` | Output as test case descriptions (copy-pasteable) |
