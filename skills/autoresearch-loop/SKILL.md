---
name: autoresearch-loop
description: "Atomic edit-verify-keep/revert iteration loop with metrics tracking. Use when: iterative optimization, test-pass grinding, metric improvement, Karpathy-style autoresearch."
phase: IMPLEMENT
---

# Autoresearch Loop

Atomic commit iteration: make one change, measure, keep or revert.

## When to Use

- Iterative test-pass improvement
- Performance metric optimization
- Score grinding (coverage %, passing count, timing)
- Any loop where "did it help?" has a numeric answer

## Setup

Before first iteration, establish:

1. **Baseline**: Run verify command, record the number
2. **Verify command**: Must output a single number (see examples)
3. **Goal direction**: higher-is-better or lower-is-better
4. **Max iterations**: Default 20

```bash
# Good verify commands
pytest tests/ -q --tb=no 2>&1 | grep passed | grep -o '[0-9]*' | head -1
cargo test 2>&1 | grep -c "test result: ok"
npx jest --no-coverage 2>&1 | grep -o '[0-9]* passed' | grep -o '[0-9]*'
wc -l < src/big_file.py  # minimize
```

## Iteration Protocol

Each iteration follows this exact sequence:

### 1. EDIT
One logical change only. Must be independently revertable.
- Extract a helper function
- Inline a constant
- Rename for clarity
- Fix one failing assertion

NOT allowed in single iteration:
- Multi-file refactors
- Behavior + style changes together
- Two unrelated fixes

### 2. VERIFY
Run the verify command. Record the number.

Safety checks — block these:
- Commands with `rm`, `curl`, `wget`, `http`
- Commands without bounded output
- Commands that modify state

Timeout: 30s max.

### 3. DECIDE

```
if metric improved OR within 1% of baseline:
    KEEP → git add <files> && git commit -m "loop({n}): {desc} [{before}→{after}]"
else:
    REVERT → git checkout -- <files>
    LOG: REVERTED — {desc} [{before}→{after}]
```

### 4. LOG

Append to `.claude/loop-log.tsv`:
```
{n}\t{timestamp}\t{KEEP|REVERT}\t{description}\t{before}\t{after}\t{files}
```

## Stuck Detection

- 5 consecutive REVERTs: pause, analyze what pattern is failing, try a different approach
- 10 consecutive REVERTs: STOP — report "stuck" with pattern analysis

## Modes

| Command | Behavior |
|---------|----------|
| `/man-loop optimize <cmd>` | Maximize metric |
| `/man-loop minimize <cmd>` | Minimize metric |
| `/man-loop fix <test-cmd>` | Iterate until all tests pass |

## Example Session

```
Baseline: 43 tests passing

Iteration 1: extract validation helper → 45 passing → KEEP
  loop(1): extract validate_email helper [43→45]

Iteration 2: inline DEBUG constant → 44 passing → REVERT
  REVERTED: inline DEBUG constant [45→44]

Iteration 3: remove dead branch → 45 passing (within 1%) → KEEP
  loop(3): remove dead branch in parser [45→45]
```

## Output Format

```markdown
## Loop Summary

- Baseline: {n}
- Final: {n}
- Improvement: {delta} ({direction})
- Iterations: {total} ({kept} kept, {reverted} reverted)
- Status: DONE | STUCK at iteration {n}

### Kept Changes
| # | Description | Before | After |
|---|-------------|--------|-------|
| 1 | ... | 43 | 45 |

### Reverted
| # | Description | Before | After |
|---|-------------|--------|-------|
| 2 | ... | 45 | 44 |
```
