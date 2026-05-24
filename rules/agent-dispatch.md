# Proactive Agent Dispatch Rules

Dispatch these agents **without waiting for the user to ask**. The trigger conditions below are the signal — act on them immediately.

## Always Dispatch (no user prompt needed)

| Trigger | Agent | `subagent_type` |
|---------|-------|----------------|
| Any implementation task completed | `code-reviewer` | `code-reviewer` |
| Implementation touches auth, sessions, tokens, passwords, permissions, file uploads, user input, external APIs | `secure-reviewer` | `secure-reviewer` |
| New feature or bug fix implemented | `test-engineer` | `test-engineer` |
| User reports a bug or unexpected behavior | `debugger` | `debugger` |
| Non-trivial feature request received, before planning | `codebase-explorer` | `codebase-explorer` |
| About to ship / deploy / merge to main | `release-prep` | `release-prep` |

## Dispatch Based on Context

| Trigger | Agent | `subagent_type` |
|---------|-------|----------------|
| Refactor just completed (renamed symbols, restructured modules, extracted functions) | `refactor-cleaner` | `refactor-cleaner` |
| Code with try/catch, except, rescue, error handling was written or modified | `silent-failure-hunter` | `silent-failure-hunter` |
| Complex or non-obvious logic added with no explanation comment | `comment-analyzer` | `comment-analyzer` |
| User asks about architecture, scaling, or service boundaries | `architect` | `architect` |
| User asks about harness config, hooks, or skill quality | `harness-optimizer` | `harness-optimizer` |
| Session involved substantial non-trivial work and is ending | `journal-writer` | `journal-writer` |

## Dispatch Order for Implementation Pipeline

When implementing a feature end-to-end, dispatch in this order:

```
1. codebase-explorer   (scout before planning)
2. implementer         (implement tasks)
3. code-reviewer       (review after each implementation batch)
4. secure-reviewer     (if security-sensitive changes detected)
5. test-engineer       (verify test coverage)
6. release-prep        (before shipping)
```

## Anti-patterns — Do NOT wait for user to ask

- Do NOT finish implementing and stop without dispatching `code-reviewer`
- Do NOT merge security-sensitive changes without dispatching `secure-reviewer`
- Do NOT start implementing a non-trivial feature without first dispatching `codebase-explorer`
- Do NOT complete a refactor without dispatching `refactor-cleaner`
