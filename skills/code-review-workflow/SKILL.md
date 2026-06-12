---
name: code-review-workflow
description: How to request and receive code reviews. Use when requesting review, receiving review feedback, or reviewing automation/testing code.
phase: REVIEW
---

# Code Review Workflow

## Requesting Review

Dispatch man:code-reviewer subagent to catch issues before they cascade. Reviewer gets precisely crafted context — never your session history.

**When mandatory:**
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**When optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

**How to request:**

```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

Dispatch man:code-reviewer subagent with:
- `{WHAT_WAS_IMPLEMENTED}` — what you just built
- `{PLAN_OR_REQUIREMENTS}` — what it should do
- `{BASE_SHA}` / `{HEAD_SHA}` — commit range
- `{DESCRIPTION}` — brief summary

**Act on feedback:**
- Fix Critical immediately
- Fix Important before proceeding
- Note Minor for later
- Push back if reviewer is wrong (with reasoning)

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues

See template at: `skills/subagent-driven-development/code-quality-reviewer-prompt.md`

---

## Receiving Review

Technical evaluation, not emotional performance. Verify before implementing. Ask before assuming.

**Response pattern:**
1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each

**Forbidden responses:**
- "You're absolutely right!" / "Great point!" / "Excellent feedback!" — performative
- "Let me implement that now" — before verification

**Instead:** restate the technical requirement, ask clarifying questions, push back with technical reasoning if wrong, or just start working (actions > words).

**Handling unclear feedback:** If ANY item is unclear, STOP — do not implement anything yet. Ask for clarification. Items may be related; partial understanding = wrong implementation.

**YAGNI check for "professional" features:**
```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage
  IF unused: "This isn't called. Remove it (YAGNI)?"
  IF used: Then implement properly
```

**When to push back:** suggestion breaks functionality, reviewer lacks full context, violates YAGNI, technically incorrect for this stack, legacy/compatibility reasons exist.

**Acknowledging correct feedback:**
```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
❌ "Thanks for catching that!" / any gratitude
```

**Common mistakes:**

| Mistake | Fix |
|---------|-----|
| Performative agreement | State requirement or just act |
| Blind implementation | Verify against codebase first |
| Batch without testing | One at a time, test each |
| Avoiding pushback | Technical correctness > comfort |

---

## Reviewing Automation Code

For browser automation, payment automation, or testing scripts — apply the automation rule checklist.

See `references/automation-rules/` for 18 rules by severity (CRITICAL → LOW).

**Hard refusal:** this skill reports only — it does not edit. Dispatch implementer for fixes.
