---
name: structured-refactoring
description: Create a detailed refactor plan with tiny commits via user interview, then file it as a GitHub issue. Use when user wants to plan a refactor, create a refactoring RFC, or break a refactor into safe incremental steps.
phase: MAINTAIN
---

This skill will be invoked when the user wants to create a refactor request. You should go through the steps below. You may skip steps if you don't consider them necessary.

1. Ask the user for a long, detailed description of the problem they want to solve and any potential ideas for solutions.

2. Explore the repo to verify their assertions and understand the current state of the codebase.

3. Ask whether they have considered other options, and present other options to them.

4. Interview the user about the implementation. Be extremely detailed and thorough.

5. Hammer out the exact scope of the implementation. Work out what you plan to change and what you plan not to change.

6. Look in the codebase to check for test coverage of this area of the codebase. If there is insufficient test coverage, ask the user what their plans for testing are.

7. Break the implementation into a plan of tiny commits. Remember Martin Fowler's advice to "make each refactoring step as small as possible, so that you can always see the program working."

8. Create a GitHub issue with the refactor plan using the template below.

<refactor-plan-template>

## Problem Statement

A detailed description of the problem, from both the user's and developer's perspective.

## Solution

The proposed solution and approach.

## Commits

A numbered list of tiny, atomic commits:

1. `refactor: [description]` — what changes and why
2. `refactor: [description]` — ...

Each commit should leave the codebase in a working state.

## Decision Document

Key decisions made during the interview:
- Why this approach over alternatives
- What was explicitly out of scope and why

## Testing Decisions

- Current test coverage in this area
- What new tests will be added
- What existing tests may need updating

## Out of Scope

Explicit list of things NOT being changed in this refactor.

## Further Notes

Any additional context, risks, or follow-up work.

</refactor-plan-template>
