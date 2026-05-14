---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
phase: PLAN
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `docs/mankit/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)
- Do NOT commit plan files to git — they are working documents for implementation, not permanent project documentation

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## Existing Documentation Scan

Before defining tasks, scan `docs/**/*.md` for documentation relevant to the feature area:

- **Existing specs/designs** — decisions already made, constraints already established
- **Architecture notes** — current structure, patterns, conventions
- **Feature docs** — functions, components, and logic already documented with file locations

If docs describe functions or components you'll be modifying, reference them in the relevant task's **Files** section so the implementer has full context. If docs map out file locations, use those as the starting point for your file structure.

If no docs exist for the area, note this — it means this is either a new feature or a legacy area without documentation.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use man:subagent-driven-development (recommended) or man:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Test-Update Tasks Need Extra Detail

When a task is "update tests" or "fix tests" that depends on changes from prior tasks, the plan MUST include:

1. **Exact test file paths** — not "update the tests", but `tests/socket.service.test.ts`
2. **What changed that breaks tests** — "Task 2 made `emitNextTeam` async, so callers need `await`"
3. **Specific mock/assertion changes** — show the before→after for each test change
4. **Targeted test command** — `npx jest socket.service.test --no-coverage --forceExit`, never the full suite
5. **Expected test count** — "Expected: 12/12 PASS"

A vague test task ("update tests") is the #1 cause of implementer thrashing. The implementer has no context from prior tasks — if the plan doesn't spell out exactly what changed and how tests should adapt, the agent will run the full suite, see failures it doesn't understand, and loop for 20+ minutes.

**Bad:** `Task 5: Update tests for the new ranking feature`

**Good:**
```markdown
Task 5: Update socket.service.test.ts for async emitNextTeam

Files:
- Modify: `tests/socket.service.test.ts`

Context: Tasks 2-3 changed `emitNextTeam` from sync to async and added
`ranking` parameter. Tests that call `emitNextTeam` need `await` and
mock for `buildRanking`.

- [ ] Step 1: Add `buildRanking` mock
  ```ts
  jest.spyOn(rankingService, 'buildRanking').mockResolvedValue(mockRanking);
  ```

- [ ] Step 2: Update emitNextTeam call sites to use await
  ```ts
  // Before:
  service.emitNextTeam(gameId);
  // After:
  await service.emitNextTeam(gameId);
  ```

- [ ] Step 3: Run targeted test
  Run: `npx jest socket.service.test --no-coverage --forceExit`
  Expected: 12/12 PASS
```

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Remember
- Exact file paths always
- Complete code in every step — if a step changes code, show the code
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/mankit/plans/<filename>.md`. Three execution options:**

**1. Team Agents (recommended)** - Dispatch tam quốc agents (triệu-vân, bàng-thống, pháp-chính, etc.) per task, each agent specialized for its role

**2. Subagent-Driven** - Dispatch fresh generic subagent per task, review between tasks, fast iteration

**3. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?"**

**If Team Agents chosen:**

You are the **team lead**. Follow this exact sequence:

1. **Create shared task list** (`Ctrl+T`) — convert every plan task to a checklist item with owner:
   ```
   [ ] trieu-van: <task name> — Files: <files>
   [ ] hoang-trung: Write tests for <task name>
   [ ] phap-chinh: Review <task name>
   ```

2. **Spawn teammates** based on task types present in the plan:
   - Has implementation tasks → spawn `trieu-van` teammate
   - Has test tasks → spawn `hoang-trung` teammate
   - Has debug tasks → spawn `bang-thong` teammate
   - Always spawn `phap-chinh` for final review

   Spawn prompt template:
   ```
   You are <agent-name>, a specialist teammate. Check the shared task list (Ctrl+T).
   Pick up tasks assigned to you in order. For each task:
   1. Read the plan task spec carefully
   2. Complete the work
   3. Mark your task DONE with a brief summary
   Do NOT touch tasks assigned to other teammates.
   ```

3. **Monitor** — watch task list, nudge stuck teammates, resolve blockers
4. **Coordinate** — if phap-chinh finds issues, message the implementer to revise
5. **Wrap up** — when all tasks DONE, synthesize, run tests, ask user to commit

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use man:subagent-driven-development
- Fresh subagent per task + two-stage review

**If Inline Execution chosen:**
- **REQUIRED SUB-SKILL:** Use man:executing-plans
- Batch execution with checkpoints for review

## Codebase-Explorer Integration

If `/man-explore` was run before invoking this skill, the user will paste the
codebase-explorer output. When that output is present:
- Use the **Touch points** table as the starting point for each task's `Files:` section.
- Cite the conventions in the plan header so implementers follow them.
- Resolve any items in the **Questions for the planner** section before writing tasks.

If no codebase-explorer output is provided and the feature is non-trivial, ask the
user whether to run `/man-explore` first.
