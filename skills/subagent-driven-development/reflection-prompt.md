# Reflection Prompt Template

Use this template after a task completes the full review cycle (spec + quality approved) to evaluate whether the implementation actually achieves the task's intent — not just follows its letter.

**Purpose:** Metacognitive self-check. Catches semantic gaps that pass spec compliance but miss the real goal.

**When to use:** After every 3rd completed task, OR after any task that received 2+ review rejection cycles.

**Model:** haiku (fast, cheap — reflection is a structured checklist, not creative work)

```
Agent:
  model: haiku
  description: "Reflect on Task N implementation"
  prompt: |
    You are performing a metacognitive reflection on a completed implementation.

    ## Task That Was Completed

    [FULL TEXT of original task spec]

    ## What Was Built

    [Implementer's final report — status, diff summary, test results]

    ## Review History

    [Spec reviewer verdict + any issues found and fixed]
    [Code quality reviewer verdict + any issues found and fixed]
    [Number of review rejection cycles: N]

    ## Your Job

    You are NOT re-reviewing code quality or spec compliance — those already passed.
    You are checking whether the implementation ACTUALLY achieves what the task
    was trying to accomplish, and whether the approach will hold up.

    Evaluate these 5 dimensions. Score each 1-5:

    ### 1. Intent Alignment (did we solve the right problem?)
    - Does the implementation address the WHY behind the task, not just the WHAT?
    - Would a user/developer encountering this code understand its purpose?
    - Could the spec have been misinterpreted in a way that technically passes
      review but misses the point?

    ### 2. Integration Risk (will this break something downstream?)
    - How does this change interact with code NOT in the diff?
    - Are there implicit assumptions about caller behavior?
    - Could a future task in this plan conflict with decisions made here?

    ### 3. Approach Quality (was this the right way to solve it?)
    - Was there a simpler approach that wasn't considered?
    - Did review cycles indicate the implementer struggled with the approach?
    - If 2+ rejection cycles occurred: was the root cause the approach itself
      or just execution mistakes?

    ### 4. Knowledge Gaps (what did this task reveal?)
    - Did the implementer need context that wasn't provided?
    - Were there assumptions that turned out wrong?
    - Is there missing documentation or unclear interfaces exposed by this task?

    ### 5. Confidence Score (0-100%)
    - How confident are you that this implementation is production-ready?
    - Factor in: review cycle count, complexity, integration surface area

    ## Output Format

    ```
    reflection:
      task: [task number and name]
      scores:
        intent_alignment: [1-5]
        integration_risk: [1-5, where 5 = low risk]
        approach_quality: [1-5]
        knowledge_gaps: [1-5, where 5 = no gaps]
        confidence: [0-100]
      overall: [PROCEED | REPLAN_TASK | REPLAN_PHASE]
      findings:
        - [finding 1]
        - [finding 2]
      recommended_actions:
        - [action if any, or "none"]
    ```

    **Decision rules:**
    - All scores >= 3 AND confidence >= 70% → PROCEED
    - Any score <= 2 OR confidence < 50% → REPLAN_TASK
    - 2+ scores <= 2 AND affects other tasks in plan → REPLAN_PHASE
```

## Controller Response to Reflection

**PROCEED:** Continue to next task. Log reflection scores for trend tracking.

**REPLAN_TASK:** The current task needs rework with a different approach:
1. Read reflection findings — identify what went wrong
2. Update task spec in plan file with new approach/constraints
3. Re-dispatch implementer with updated spec + reflection findings as context
4. Reset review cycle counter

**REPLAN_PHASE:** The plan itself has issues affecting multiple tasks:
1. STOP dispatching new tasks
2. Present reflection findings to human partner
3. If human approves replan: update plan file, re-extract remaining tasks
4. Resume from the revised plan
