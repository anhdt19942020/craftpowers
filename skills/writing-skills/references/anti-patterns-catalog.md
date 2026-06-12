## Anti-Patterns

### ❌ Narrative Example

Long prose examples instead of structured reference:

```markdown
# BAD: Story-format
"Imagine you're debugging a React component. You'd start by opening DevTools..."

# GOOD: Structured reference
## Debug Steps
1. Open DevTools → Console tab
2. Filter errors by component name
3. Check prop types
```

### ❌ Multi-Language Dilution

Showing the same pattern in 5 languages instead of one excellent example:

```markdown
# BAD: Python version, Ruby version, Go version, Rust version, Java version...
# GOOD: One excellent TypeScript example with clear annotations
```

### ❌ Code in Flowcharts

Embedding actual code inside dot/mermaid diagrams makes them unreadable and unmaintainable. Keep flowcharts as flow logic only; put code in separate code blocks.

### ❌ Generic Labels

Using vague section headers like "Tips", "Notes", "Misc", "Other":

```markdown
# BAD
## Tips
- Always test your code
- Use version control

# GOOD
## Verification Checklist
- [ ] Run: `npx jest src/feature.test.ts --forceExit` → all pass
- [ ] Run: `tsc --noEmit` → no errors
```

## Bulletproofing Skills Against Rationalization

### Close Every Loophole Explicitly

After RED phase reveals rationalizations, add explicit counter-rules:

```markdown
# BAD: Leaves loophole
## When to Use
Use TDD for new features.

# GOOD: Closes loophole
## When to Use
Use TDD for ALL code changes — new features, bug fixes, refactoring.
**No exceptions for "simple" changes** — simple changes are where assumptions hide.
```

### Address "Spirit vs Letter" Arguments

When agents argue "I'm following the spirit of the rule":

```markdown
## The Iron Law
Write the test BEFORE writing the implementation code.
**"Before" means: the test file must exist and fail before you write a single line of implementation.**
Not: write test and implementation in the same commit.
Not: write test immediately after implementation.
```

### Build Rationalization Table

Document every rationalization found during RED phase:

| Rationalization | Counter-rule |
|-----------------|-------------|
| "This is too simple to need a test" | All code requires tests. Simple = faster to test. |
| "I'll add tests after I verify it works" | Tests first. Always. Non-negotiable. |
| "The existing tests cover this" | New behavior = new test. Verify explicitly. |
| "It's a one-line change" | One-line changes break systems. Test it. |

### Create Red Flags List

```markdown
## Red Flags — STOP if you think:
- "This is obvious, no test needed"
- "I'll test it manually"
- "The integration test covers this"
- "Tests would be hard to write here"
ALL of these mean: write the test first anyway.
```

### Update CSO for Violation Symptoms

Add violation symptoms to the description field so the skill is triggered when agents are about to violate it:

```yaml
description: "MUST use when writing any code. Prevents: skipping tests, writing implementation before tests, manual-only verification."
```

## Quality Rubric

A skill passes quality review when:

| Criterion | Pass condition |
|-----------|---------------|
| **Trigger accuracy** | Skill activates in the right situations, not others |
| **Loophole-free** | No rationalization survives the anti-pattern table |
| **Single example** | One complete, runnable, annotated example |
| **Token-efficient** | Under word count target for its load frequency |
| **Gate integrity** | All HARD-GATE / MANDATORY-GATE blocks survive refactor intact |
| **Tested** | Passed at least one RED-GREEN-REFACTOR cycle with a real subagent |
| **CSO-complete** | Description includes trigger keywords and violation symptoms |
