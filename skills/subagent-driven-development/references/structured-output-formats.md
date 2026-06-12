## Structured Agent Output Formats

All subagents (implementer, spec reviewer, quality reviewer, reflection) MUST return structured output. This enables reliable parsing by the controller and trend tracking across tasks.

### Implementer Report Format

```yaml
status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
confidence: 85  # 0-100, self-assessed
task: "Task 3: Add user validation"
diff:
  files_changed: 4
  insertions: 120
  deletions: 15
  files:
    - path: "src/auth/validate.ts"
      change: "+80/-5"
    - path: "src/auth/validate.test.ts"
      change: "+40/-10"
tests:
  command: "npx jest src/auth/validate.test.ts --forceExit"
  result: PASS  # PASS | FAIL
  count: "8/8"
evidence:  # grounding — every claim must cite what was actually run
  compile: "tsc --noEmit → PASS"  # exact command + result, or N/A
  tests: "npx jest src/auth/validate.test.ts --forceExit → PASS 8/8"
  lint: "eslint src/auth/ → PASS"  # or N/A if not configured
concerns:  # empty list if none
  - "validate.ts growing large (180 lines) — consider splitting in future task"
followups:  # out-of-scope items noticed
  - "Related: error messages not i18n-ready"
```

### Spec Reviewer Report Format

```yaml
verdict: PASS | FAIL
task: "Task 3: Add user validation"
requirements_checked: 5
requirements_met: 5  # or fewer if FAIL
issues:  # empty list if PASS
  - requirement: "Email format validation"
    status: MISSING | PARTIAL | WRONG
    detail: "Regex accepts invalid TLDs"
    file: "src/auth/validate.ts:45"
```

### Quality Reviewer Report Format

```yaml
verdict: APPROVE | REJECT
task: "Task 3: Add user validation"
issues:
  critical: []  # blocking
  important:    # should fix
    - "N+1 query risk in batch validation loop"
  minor: []     # optional
assessment: "Clean implementation. One important issue in batch path."
```

### Reflection Report Format

```yaml
reflection:
  task: "Task 3: Add user validation"
  scores:
    intent_alignment: 4
    integration_risk: 5
    approach_quality: 4
    knowledge_gaps: 3
    confidence: 78
  overall: PROCEED | REPLAN_TASK | REPLAN_PHASE
  findings:
    - "Validation logic tightly coupled to HTTP layer — may need extraction for CLI reuse"
  recommended_actions:
    - "none"
```

### Controller Parsing

Parse structured output by extracting the YAML block from the agent's response. Key fields for controller decisions:

- `status` / `verdict` / `overall` → determines next step in workflow
- `confidence` → tracked across tasks for trend detection
- `issues` → forwarded to implementer for fixes
- `concerns` / `findings` → accumulated for phase-level reflection

If an agent returns free-text instead of structured format, treat it as the agent's model being unable to follow the format — extract what you can and log a warning. Do not re-dispatch just for formatting.
