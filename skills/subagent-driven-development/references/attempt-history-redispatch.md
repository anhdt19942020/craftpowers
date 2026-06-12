## Attempt History on Re-dispatch

When re-dispatching an implementer (after BLOCKED, NEEDS_CONTEXT, or REPLAN_TASK), the controller MUST include attempt history. The new agent has zero memory of prior attempts — without this, it will repeat the same failing approaches.

**Include in re-dispatch prompt:**

```
## Prior Attempts (DO NOT repeat these approaches)

### Attempt 1
- Approach: [what the previous agent tried]
- Result: [what happened — error message, test failure, review rejection]
- Why it failed: [root cause if known]
- Files touched: [list]

### Attempt 2
- Approach: [different approach tried]
- Result: [what happened]
- Why it failed: [root cause]
- Files touched: [list]

## What Changed Since Last Attempt
- [new context provided, model upgraded, task decomposed, etc.]

## Constraints from Prior Failures
- Do NOT [specific approach that failed]
- The error at [file:line] is caused by [root cause], not [what agent 1 assumed]
```

**Controller responsibility:** Gather this from:
1. Previous agent's structured report (status, concerns, diff)
2. Review findings that triggered the re-dispatch
3. Reflection findings if REPLAN_TASK

**Max re-dispatches per task:** 3 (across all models). After 3 attempts, escalate to human regardless of remaining model upgrades.
