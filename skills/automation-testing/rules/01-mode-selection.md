---
id: MODE-SELECTION
severity: CRITICAL
applies_to: all
---

# Mode Selection

## Intent

Choosing the wrong mode wastes effort and produces unusable output. Interactive mode output can't run in CI. Generated files can't provide real-time debugging feedback. Wrong mode = wrong deliverable.

## Search patterns

- User says "generate", "write tests", "CI", "regression suite" → File Generation
- User says "test this", "verify", "check", "debug", "try" → Interactive
- User says "run tests" → Ambiguous, ask
- No explicit user preference → Default based on context:
  - Has existing `playwright.config.ts` → File Generation
  - No test infrastructure → Interactive first, then suggest file gen

## Fix

Always confirm mode before starting:

```
Mode: Interactive (MCP Playwright)
Reason: User wants to verify login flow works — one-off verification, not CI suite.
```

or

```
Mode: File Generation (.spec.ts)
Reason: User needs regression tests for CI — generating reusable test files.
```

If ambiguous, ask:
```
Two modes available:
1. Interactive — I'll test directly in the browser now (good for debugging/verification)
2. File Generation — I'll create .spec.ts files you can run in CI (good for regression)
Which do you prefer?
```
