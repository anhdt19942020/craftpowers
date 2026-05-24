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
| Agent team run completed, before reporting results to user | `final-approver` | `final-approver` |

## Dispatch Based on Context

| Trigger | Agent | `subagent_type` |
|---------|-------|----------------|
| Refactor just completed (renamed symbols, restructured modules, extracted functions) | `refactor-cleaner` | `refactor-cleaner` |
| Code with try/catch, except, rescue, error handling was written or modified | `silent-failure-hunter` | `silent-failure-hunter` |
| Complex or non-obvious logic added with no explanation comment | `comment-analyzer` | `comment-analyzer` |
| User asks about architecture, scaling, or service boundaries | `architect` | `architect` |
| User asks about harness config, hooks, or skill quality | `harness-optimizer` | `harness-optimizer` |
| Session involved substantial non-trivial work and is ending | `journal-writer` | `journal-writer` |
| New module, API endpoint, or public interface completed | `doc-writer` | `doc-writer` |
| User asks to test a UI flow, browser behavior, or E2E scenario | `automation-tester` | `automation-tester` |
| Choosing between libraries/frameworks, implementing unfamiliar protocol, need external docs | `deep-researcher` | `deep-researcher` |

## Choose the Right Fix Agent

| Scope | Agent | `subagent_type` |
|-------|-------|----------------|
| 1–2 files: typo, rename, single-function fix | `quick-fix` | `quick-fix` |
| One task from an existing plan | `implementer` | `implementer` |
| Multi-file feature from scratch | `implementer` (per task) | `implementer` |

**Rule:** Never implement code yourself when the scope is a plan task — always delegate to `implementer`. Reserve `quick-fix` for surgical edits only.

## Dispatch Order for Implementation Pipeline

When implementing a feature end-to-end, dispatch in this order:

```
1. codebase-explorer   (scout before planning)
2. deep-researcher     (if external context needed)
3. implementer         (one per plan task)
4. code-reviewer       (after each implementation batch)
5. secure-reviewer     (if security-sensitive changes detected)
6. test-engineer       (verify test coverage)
7. automation-tester   (if UI/browser behavior involved)
8. doc-writer          (if new public API or module)
9. refactor-cleaner    (if code was restructured)
10. final-approver     (if multi-agent team run)
11. release-prep       (before shipping)
```

## Anti-patterns — Do NOT wait for user to ask

- Do NOT finish implementing and stop without dispatching `code-reviewer`
- Do NOT merge security-sensitive changes without dispatching `secure-reviewer`
- Do NOT start implementing a non-trivial feature without first dispatching `codebase-explorer`
- Do NOT complete a refactor without dispatching `refactor-cleaner`
- Do NOT implement code yourself for plan tasks — delegate to `implementer`
- Do NOT implement 3+ file changes yourself — split into tasks and delegate to `implementer`
- Do NOT complete a team run without dispatching `final-approver` before reporting to user
