---
name: coding-level
description: "Set response detail level (0-5). Adjusts explanation depth for the session."
phase: META
---

# Coding Level

Set the response detail level for this session. Controls how much explanation, context, and scaffolding the agent provides.

## Usage

```
/coding-level <0-5>
/coding-level        # show help
```

## Level Table

| Level | Name | Description |
|-------|------|-------------|
| 0 | ELI5 | Explain like I'm 5. Pure analogies, zero jargon, step-by-step with no skipped steps |
| 1 | Beginner | Define all terms on first use, walk through each step, no assumed knowledge |
| 2 | Intermediate | Standard explanations, some assumed knowledge, define uncommon terms |
| 3 | Advanced | Concise, assumes strong fundamentals, skip basics, focus on what's non-obvious |
| 4 | Expert | Terse, domain shorthand OK, code-heavy, minimal prose |
| 5 | God Mode | Minimal prose, code-only answers, fragments OK, no hand-holding |

## Instructions

Parse `$ARGUMENTS` as an integer 0–5.

**If a valid level is given:**

1. Acknowledge: state the level name and one-line description.
2. Apply immediately — adjust ALL subsequent responses in this session to match the level:
   - **Level 0:** Use analogies and everyday language. Never use technical terms without a plain-English explanation. Walk through every step. Assume the reader has never coded before.
   - **Level 1:** Define terms on first use. Numbered steps. No assumed background. Gentle pace.
   - **Level 2:** Normal explanations. Skip trivial basics. Define uncommon terms inline. Balanced code-to-prose ratio.
   - **Level 3:** Skip basics. No definition of common terms. Focus on subtleties, edge cases, non-obvious behavior. Tighter prose.
   - **Level 4:** Near-expert shorthand. Code with minimal comment. Prose only for decisions and trade-offs.
   - **Level 5:** Code first, prose last or omitted. Fragments acceptable. No scaffolding, no re-stating the question.

3. Confirm: "Level set to `<N> — <Name>`. Applies for the rest of this session."

**If no argument or invalid argument:**

Show this help message:

```
Usage: /coding-level <0-5>

  0  ELI5         Analogies, no jargon, step-by-step
  1  Beginner     Define all terms, walk through steps
  2  Intermediate Standard explanations, some assumed knowledge
  3  Advanced     Concise, skip basics, focus on non-obvious
  4  Expert       Terse, domain shorthand, code-heavy
  5  God Mode     Code only, fragments OK, no hand-holding

Current level: <current level or "not set (default: 2)">
```

## Persistence

The level persists for the entire session. It can be changed at any time by invoking `/coding-level <N>` again. Default behavior (if never set) is equivalent to level 2.
