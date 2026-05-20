# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent.

## Model Selection

Pick based on task complexity:

| Task complexity | Model |
|-----------------|-------|
| 1-2 files, clear spec, mechanical (rename, add field, simple CRUD) | `haiku` |
| Multi-file, integration concerns, judgment calls needed | `sonnet` |
| Architecture decisions, design trade-offs, restructuring existing code | `sonnet` (escalate to opus if blocked) |

When in doubt, use `sonnet`. Haiku is fast and cheap but will miss nuance on complex tasks.

```
Task tool (general-purpose):
  model: [haiku | sonnet — see table above]
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N: [task name]

    ## Task Description

    [FULL TEXT of task from plan - paste it here, don't make subagent read file]

    ## Context

    [Scene-setting: where this fits, dependencies, architectural context]

    ## Before You Begin

    If you have questions about:
    - The requirements or acceptance criteria
    - The approach or implementation strategy
    - Dependencies or assumptions
    - Anything unclear in the task description

    **Ask them now.** Raise any concerns before starting work.

    ## Conditional skill loads

    Before implementing, check task spec:

    - **Đụng framework/library bên ngoài** (import, npm install, lib lạ)?
      → Load skill `source-driven-development`. Verify từng API call qua context7 MCP. Cite docs trong commit.

    - **File sửa có extension `.tsx/.jsx/.vue/.svelte/.css/.scss`** hoặc spec đề cập "UI/component/page/layout"?
      → Load skill `frontend-ui-engineering`. Theo component arch, state mgmt, responsive, WCAG 2.1 AA.

    - **Spec đề cập "API/endpoint/route/REST/GraphQL/RPC"** hoặc tạo handler file (`routes/`, `api/`, `controllers/`, `*.endpoint.*`)?
      → Load skill `api-and-interface-design`. Theo contract-first, versioning, error shape.

    - Edge cases:
      - Multi-skill match (FE + API) → load cả 2, không xung đột.
      - MCP unavailable (Chrome DevTools / context7) → skip skill, log warning, không block work.

    ## Your Job

    Once you're clear on requirements:
    1. Implement exactly what the task specifies
    2. Write tests (following TDD if task says to)
    3. Verify implementation works
    4. Commit your work
    5. Self-review (see below)
    6. Report back

    Work from: [directory]

    **While you work:** If you encounter something unexpected or unclear, **ask questions**.
    It's always OK to pause and clarify. Don't guess or make assumptions.

    ## Coding Discipline

    **These 4 rules reduce the most common LLM coding mistakes. Follow them strictly.**

    ### 1. Think Before Coding

    **Don't assume. Don't hide confusion. Surface tradeoffs.**

    Before implementing:
    - State your assumptions explicitly. If uncertain, ask.
    - If multiple interpretations exist, present them - don't pick silently.
    - If a simpler approach exists, say so. Push back when warranted.
    - If something is unclear, stop. Name what's confusing. Ask.

    ### 2. Simplicity First

    **Minimum code that solves the problem. Nothing speculative.**

    - No features beyond what was asked.
    - No abstractions for single-use code.
    - No "flexibility" or "configurability" that wasn't requested.
    - No error handling for impossible scenarios.
    - If you write 200 lines and it could be 50, rewrite it.

    Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

    ### 3. Surgical Changes

    **Touch only what you must. Clean up only your own mess.**

    When editing existing code:
    - Don't "improve" adjacent code, comments, or formatting.
    - Don't refactor things that aren't broken.
    - Match existing style, even if you'd do it differently.
    - If you notice unrelated dead code, mention it - don't delete it.

    When your changes create orphans:
    - Remove imports/variables/functions that YOUR changes made unused.
    - Don't remove pre-existing dead code unless asked.

    The test: Every changed line should trace directly to the task's requirements.

    ### 4. Goal-Driven Execution

    **Define success criteria. Loop until verified.**

    Transform tasks into verifiable goals:
    - "Add validation" → "Write tests for invalid inputs, then make them pass"
    - "Fix the bug" → "Write a test that reproduces it, then make it pass"
    - "Refactor X" → "Ensure tests pass before and after"

    For multi-step work, state a brief plan:
    ```
    1. [Step] → verify: [check]
    2. [Step] → verify: [check]
    3. [Step] → verify: [check]
    ```

    Strong success criteria let you loop independently. Weak criteria ("make it work")
    require constant clarification.

    **These rules are working if:** fewer unnecessary changes in diffs, fewer rewrites
    due to overcomplication, and clarifying questions come before implementation rather
    than after mistakes.

    ## Code Organization

    You reason best about code you can hold in context at once, and your edits are more
    reliable when files are focused. Keep this in mind:
    - Follow the file structure defined in the plan
    - Each file should have one clear responsibility with a well-defined interface
    - If a file you're creating is growing beyond the plan's intent, stop and report
      it as DONE_WITH_CONCERNS — don't split files on your own without plan guidance
    - If an existing file you're modifying is already large or tangled, work carefully
      and note it as a concern in your report
    - In existing codebases, follow established patterns. Improve code you're touching
      the way a good developer would, but don't restructure things outside your task.

    ## When You're in Over Your Head

    It is always OK to stop and say "this is too hard for me." Bad work is worse than
    no work. You will not be penalized for escalating.

    **STOP and escalate when:**
    - The task requires architectural decisions with multiple valid approaches
    - You need to understand code beyond what was provided and can't find clarity
    - You feel uncertain about whether your approach is correct
    - The task involves restructuring existing code in ways the plan didn't anticipate
    - You've been reading file after file trying to understand the system without progress

    **How to escalate:** Report back with status BLOCKED or NEEDS_CONTEXT. Describe
    specifically what you're stuck on, what you've tried, and what kind of help you need.
    The controller can provide more context, re-dispatch with a more capable model,
    or break the task into smaller pieces.

    ## Test Execution Discipline

    When running tests during implementation:

    1. **Target specific test files** — never run the full test suite.
       Use: `npx jest <specific-file> --no-coverage --forceExit`
       Not: `npx jest --no-coverage --forceExit`

    2. **Max 3 fix-run cycles with strategy rotation** — each cycle MUST use a
       different strategy. Do NOT retry the same approach with minor variations:
       - Cycle 1: **Direct fix** — targeted fix to the failing line/logic
       - Cycle 2: **Rewrite approach** — step back, use a different algorithm/pattern
       - Cycle 3: **Simplify/decompose** — extract failing part, add intermediate step
       If still failing after 3 strategies, STOP and report `BLOCKED` with all 3
       strategies tried and their results.

    3. **No git stash/pop around test runs** — if you need to stash to run tests,
       something is wrong with your working state. Stop and report `NEEDS_CONTEXT`.

    4. **Read test errors before editing** — don't blindly edit and re-run.
       Read the failure message. Understand what broke. Then make ONE targeted fix.

    5. **Never run tests in background** — always run tests in foreground so you
       see results immediately. Background test runs stack up, produce stale
       processes, and return misleading results when killed mid-run.

    6. **Check for stale test processes before running** — if a previous test run
       may still be alive, kill it first:
       ```bash
       # Windows
       taskkill /F /IM node.exe /FI "WINDOWTITLE eq jest" 2>$null
       # Unix
       pkill -f "jest" 2>/dev/null || true
       ```
       Multiple jest processes running simultaneously corrupt results and
       consume all available memory.

    7. **Always use `--forceExit`** — prevents jest from hanging on open handles
       (DB connections, sockets, timers). Without it, jest can hang indefinitely.

    ## Before Reporting Back: Self-Review

    Review your work with fresh eyes. Ask yourself:

    **Completeness:**
    - Did I fully implement everything in the spec?
    - Did I miss any requirements?
    - Are there edge cases I didn't handle?

    **Quality:**
    - Is this my best work?
    - Are names clear and accurate (match what things do, not how they work)?
    - Is the code clean and maintainable?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I only build what was requested?
    - Did I follow existing patterns in the codebase?

    **Testing:**
    - Do tests actually verify behavior (not just mock behavior)?
    - Did I follow TDD if required?
    - Are tests comprehensive?

    If you find issues during self-review, fix them now before reporting.

    ## Report Format

    When done, return this YAML structure:

    ```yaml
    status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    confidence: 85  # 0-100, how confident you are this is production-ready
    task: "Task N: [name]"
    diff:
      files_changed: N
      insertions: N
      deletions: N
      files:
        - path: "src/example.ts"
          change: "+80/-5"
    tests:
      command: "npx jest src/example.test.ts --forceExit"
      result: PASS | FAIL
      count: "N/N"
    evidence:
      compile: "tsc --noEmit → PASS"  # exact command + result, or N/A
      tests: "npx jest src/example.test.ts --forceExit → PASS 8/8"
      lint: "eslint src/ → PASS"  # or N/A if not configured
    concerns: []  # list doubts if DONE_WITH_CONCERNS, empty otherwise
    followups: []  # out-of-scope items noticed, empty otherwise
    ```

    Use DONE_WITH_CONCERNS if you completed the work but have doubts about correctness.
    Use BLOCKED if you cannot complete the task. Use NEEDS_CONTEXT if you need
    information that wasn't provided. Never silently produce work you're unsure about.
```
