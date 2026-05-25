---
name: model-route
description: Route a task to the right Claude model (Haiku/Sonnet/Opus) based on complexity and cost. Prevents over-spending on simple tasks or under-powering complex ones.
---

# Model Route

Classify task complexity, then recommend the right model and agent role.

## Usage

```
/man-model-route <task description>
```

## Complexity Classification

| Complexity | Characteristics | Model | Roles |
|------------|----------------|-------|-------|
| **Simple** | Typo fix, rename, single-function tweak, doc update, format change | Haiku | quick-fix, doc-writer, journal-writer |
| **Medium** | Feature impl, bug fix, test writing, code review, refactor, research | Sonnet | implementer, test-engineer, codebase-explorer, refactor-cleaner |
| **Complex** | Architecture design, security audit, root-cause debug, final approval, multi-system change | Opus | architect, debugger, code-reviewer, secure-reviewer, final-approver |

## Classification Rules

**→ Simple (Haiku)** when task:
- Touches 1-2 files
- Has obvious, mechanical solution
- Requires no codebase exploration
- Is documentation or formatting only

**→ Medium (Sonnet)** when task:
- Touches 3-10 files
- Requires understanding existing code
- Needs testing or verification
- Is a bug fix with known location

**→ Complex (Opus)** when task:
- Touches 10+ files or unknown scope
- Requires architectural judgment
- Involves security, auth, or payments
- Has tried simpler approaches and failed
- Is a pre-ship quality gate

## How to invoke

When user runs `/man-model-route <task>`:

1. Read the task description
2. Apply classification rules above
3. Output:

```
Task: <task description>

Complexity: Simple | Medium | Complex
Recommended model: claude-haiku-4-5 | claude-sonnet-4-6 | claude-opus-4-7
Recommended role: <role-name>
Invoke with: /<man-command> <task>

Rationale: <1 sentence why this complexity>
Est. cost: Haiku ≈ 10x cheaper than Sonnet, Sonnet ≈ 5x cheaper than Opus
```

4. Suggest the right `/man-*` command:
   - Simple → `/man-quick`
   - Medium → `/man-cook` or `/man-debug`
   - Complex → `/man-cook --parallel` or `/man-plan` first
