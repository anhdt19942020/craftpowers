---
name: writing-skills
description: Use when creating new skills, editing existing skills, or verifying skills work before deployment
phase: META
---

# Writing Skills

## Overview

**Writing skills IS Test-Driven Development applied to process documentation.**

**Personal skills live in agent-specific directories (`~/.claude/skills` for Claude Code, `~/.agents/skills/` for Codex)**

You write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill (documentation), watch tests pass (agents comply), and refactor (close loopholes).

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**REQUIRED BACKGROUND:** You MUST understand man:test-driven-development before using this skill. That skill defines the fundamental RED-GREEN-REFACTOR cycle. This skill adapts TDD to documentation.

**Official guidance:** For Anthropic's official skill authoring best practices, see anthropic-best-practices.md.

## What is a Skill?

A **skill** is a reference guide for proven techniques, patterns, or tools.

**Skills are:** Reusable techniques, patterns, tools, reference guides

**Skills are NOT:** Narratives about how you solved a problem once

## TDD Mapping for Skills

| TDD Concept | Skill Creation |
|-------------|----------------|
| Test case | Pressure scenario with subagent |
| Production code | Skill document (SKILL.md) |
| Test fails (RED) | Agent violates rule without skill (baseline) |
| Test passes (GREEN) | Agent complies with skill present |
| Refactor | Close loopholes while maintaining compliance |
| Write test first | Run baseline scenario BEFORE writing skill |
| Watch it fail | Document exact rationalizations agent uses |
| Minimal code | Write skill addressing those specific violations |
| Watch it pass | Verify agent now complies |
| Refactor cycle | Find new rationalizations → plug → re-verify |

## When to Create a Skill

**Create when:** technique wasn't intuitively obvious, you'd reference it again, pattern applies broadly, others would benefit.

**Don't create for:** one-off solutions, standard practices well-documented elsewhere, project-specific conventions (put in CLAUDE.md), mechanical constraints (automate those).

## Skill Types

- **Technique** — Concrete method with steps (condition-based-waiting, root-cause-tracing)
- **Pattern** — Way of thinking about problems (flatten-with-flags, test-invariants)
- **Reference** — API docs, syntax guides, tool documentation

## Directory Structure

```
skills/
  skill-name/
    SKILL.md              # Main reference (required)
    supporting-file.*     # Only if needed
```

Flat namespace. Separate files for: heavy reference (100+ lines) or reusable tools. Keep inline: principles, code patterns < 50 lines, everything else.

## SKILL.md Structure

**Frontmatter (YAML):**
- Required: `name` (letters/numbers/hyphens only) and `description` (max 1024 chars total)
- `description`: third-person, starts "Use when…", describes triggering conditions ONLY — **NEVER summarize the skill's process or workflow** (see CSO section)

```markdown
---
name: Skill-Name-With-Hyphens
description: Use when [specific triggering conditions and symptoms]
---

# Skill Name

## Overview
## When to Use
## Core Pattern
## Quick Reference
## Implementation
## Common Mistakes
## Real-World Impact (optional)
```

## Claude Search Optimization (CSO)

**Critical for discovery.** Future Claude reads description to decide which skills to load.

### Description = When to Use, NOT What the Skill Does

**Why:** When description summarizes workflow, Claude follows the description instead of reading the full skill. Tested: description saying "code review between tasks" caused ONE review; changing to just triggering conditions caused Claude to correctly follow the two-stage flowchart.

```yaml
# ❌ BAD: summarizes workflow
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ✅ GOOD: triggering conditions only
description: Use when executing implementation plans with independent tasks in the current session
```

**Rules:** concrete triggers/symptoms, technology-agnostic unless skill is specific, third person, never summarize workflow.

### Keyword Coverage

Use words Claude would search for: error messages, symptoms (flaky, hanging, zombie), synonyms, actual tool/library names.

### Naming

Active voice, verb-first: `condition-based-waiting` not `async-test-helpers`. Gerunds work well for processes.

### Token Efficiency

- getting-started workflows: <150 words each
- Frequently-loaded skills: <200 words total
- Move details to tool `--help`; use cross-references to other skills; compress examples

### Cross-Referencing

- ✅ `**REQUIRED SUB-SKILL:** Use man:test-driven-development`
- ❌ `@skills/testing/SKILL.md` — `@` force-loads, burns context before needed

## Flowchart Usage

Use only for: non-obvious decisions, process loops where you might stop early, "A vs B" choices.

Never for: reference material (use tables), code examples (use blocks), linear instructions (use numbered lists), labels without semantic meaning.

See @graphviz-conventions.dot for style rules. Use `render-graphs.js` in this directory to render to SVG.

## Code Examples

One excellent example beats many mediocre ones. Choose most relevant language. Good example: complete, runnable, well-commented, from real scenario, ready to adapt.

Don't: implement in 5+ languages, create fill-in-the-blank templates, write contrived examples.

## The Iron Law (Same as TDD)

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

Applies to NEW skills AND edits. Write skill before testing? Delete it. Start over.

**No exceptions:** not for "simple additions", "documentation updates", "I'll test if problems emerge".

**REQUIRED BACKGROUND:** man:test-driven-development explains why this matters.

## Testing All Skill Types

- **Discipline-enforcing:** Academic + pressure scenarios with combined pressures; identify rationalizations
- **Technique:** Application scenarios, variation scenarios, missing info tests
- **Pattern:** Recognition scenarios, counter-examples
- **Reference:** Retrieval scenarios, gap testing

**Testing methodology:** See @testing-skills-with-subagents.md for pressure types (time, sunk cost, authority, exhaustion) and plugging holes systematically.

## Anti-Patterns and Bulletproofing

See `references/anti-patterns-catalog.md` for: anti-pattern examples (narrative, multi-language dilution, code in flowcharts, generic labels), bulletproofing techniques (closing loopholes, spirit vs letter, rationalization table, red flags list, CSO update), and quality rubric.

## STOP: Before Moving to Next Skill

**After writing ANY skill, STOP and complete the deployment process.**

Do NOT create multiple skills in batch without testing each. Do NOT move to next skill before current one is verified.

## Skill Creation Checklist (TDD Adapted)

**IMPORTANT: Use TodoWrite to create todos for EACH item.**

**RED Phase:**
- [ ] Create pressure scenarios (3+ combined pressures for discipline skills)
- [ ] Run WITHOUT skill — document baseline behavior verbatim
- [ ] Identify rationalization patterns

**GREEN Phase:**
- [ ] Name: letters/numbers/hyphens only
- [ ] YAML frontmatter: `name`, `description` starts "Use when…" third person (max 1024 chars; see [spec](https://agentskills.io/specification))
- [ ] Keywords throughout for search
- [ ] Address specific baseline failures
- [ ] Run WITH skill — verify agents comply

**REFACTOR Phase:**
- [ ] New rationalizations → explicit counters
- [ ] Rationalization table from all test iterations
- [ ] Red flags list
- [ ] Re-test until bulletproof

**Quality Checks:**
- [ ] Small flowchart only if decision non-obvious
- [ ] Quick reference table
- [ ] Common mistakes section
- [ ] No narrative storytelling

**Deployment:**
- [ ] Commit and push; consider contributing via PR if broadly useful

## Discovery Workflow

1. Encounters problem → finds SKILL (description matches) → scans overview → reads patterns → loads example when implementing

Optimize for this flow: put searchable terms early.

## The Bottom Line

Creating skills IS TDD for process documentation. Same Iron Law, same cycle: RED (baseline) → GREEN (write skill) → REFACTOR (close loopholes). Same benefits.
