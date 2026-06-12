## Coordination Patterns

### Cross-Layer Feature (frontend + backend + tests) — spawn on unblock

```
TeamCreate({ team_name: "feature-X" })

# Create tasks with dependencies
TaskCreate({ subject: "Define API contract" })           # Task 1
TaskCreate({ subject: "Implement backend endpoints" })    # Task 2
TaskCreate({ subject: "Implement frontend components" })  # Task 3
TaskCreate({ subject: "Write integration tests" })        # Task 4
TaskUpdate({ taskId: "2", addBlockedBy: ["1"] })
TaskUpdate({ taskId: "3", addBlockedBy: ["1"] })
TaskUpdate({ taskId: "4", addBlockedBy: ["2", "3"] })

# Lead handles Task 1 itself (API contract — needs judgment)
# After Task 1 completed: Tasks 2 and 3 are unblocked → spawn backend + frontend
Agent({ team_name: "feature-X", name: "backend",  subagent_type: "man:implementer", ... })
Agent({ team_name: "feature-X", name: "frontend", subagent_type: "man:implementer", ... })

# After Tasks 2 + 3 completed: Task 4 unblocked → spawn tester
Agent({ team_name: "feature-X", name: "tester", subagent_type: "man:test-engineer", ... })
```

Spawning blocked teammates upfront wastes a session slot and clutters TaskList ownership. Spawn on unblock — see Lead Loop step 2.

### Multi-Perspective Review

```
TeamCreate({ team_name: "review-PR-42" })

TaskCreate({ subject: "Security review" })
TaskCreate({ subject: "Performance review" })
TaskCreate({ subject: "Coverage review" })

Agent({ team_name: "review-PR-42", name: "security", subagent_type: "man:secure-reviewer", ... })
Agent({ team_name: "review-PR-42", name: "perf", subagent_type: "man:code-reviewer", ... })
Agent({ team_name: "review-PR-42", name: "coverage", subagent_type: "man:test-engineer", ... })
```

### Competing-Hypothesis Debug

Built into `/man-debug` as a triage branch (2+ multi-cause signals trigger it). Full spec: `commands/man-debug.md`. Summary:

```
TeamCreate({ team_name: "debug-checkout" })

# 3 ORTHOGONAL hypotheses — confirming one must NOT raise the prior of another
TaskCreate({ subject: "Hypothesis A: race condition in cart state",
             description: "Confirm if: <criteria>\nRule out if: <criteria>" })
TaskCreate({ subject: "Hypothesis B: API timeout/retry behavior",
             description: "Confirm if: <criteria>\nRule out if: <criteria>" })
TaskCreate({ subject: "Hypothesis C: DB connection pool exhaustion",
             description: "Confirm if: <criteria>\nRule out if: <criteria>" })

# Spawn all 3 in parallel — hypotheses are independent
Agent({ team_name: "debug-checkout", name: "hyp-A", subagent_type: "man:debugger", ... })
Agent({ team_name: "debug-checkout", name: "hyp-B", subagent_type: "man:debugger", ... })
Agent({ team_name: "debug-checkout", name: "hyp-C", subagent_type: "man:debugger", ... })

# Reviewer NOT spawned upfront — created in Step 4 after winner declared.
# TaskUpdate has AND-semantics blockedBy, so there is no clean way to express
# "review is blocked until ANY of the 3 hypothesis tasks completes".
```

**Winner-first protocol:**

1. Each debugger reports `RULED OUT` or `CONFIRMED` via SendMessage to lead — hub-and-spoke.
2. On first `CONFIRMED`: wait ONE more coordination round before shutting down siblings. Catches convergent-evidence cases where the bug is multi-cause (e.g., race + retry amplification).
3. After wait:
   - Single winner → SendMessage `shutdown_request` to losers, spawn `code-reviewer` to review winner's fix.
   - Multiple winners (convergent) → keep both, write synthesis task, then review.
4. All 3 `RULED OUT` → hypotheses were wrong. Stop. Ask human for new hypothesis set; do NOT auto-spawn replacements (escalation per `## Failure & Timeout Policy`).
5. Coordination round cap = 10. No winner by round 10: escalate.

Orthogonality rule for the lead: do NOT pick 3 variants of the same class (e.g., "race in cart" + "race in checkout" + "race in queue"). One trace style means three blind spots, not three.
