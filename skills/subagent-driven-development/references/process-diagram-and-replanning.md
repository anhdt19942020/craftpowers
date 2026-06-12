# Process Diagram and Replanning Details

## Full Process Diagram

```dot
digraph process {
    rankdir=TB;

    subgraph cluster_per_task {
        label="Per Task";
        "Dispatch implementer subagent (./implementer-prompt.md)" [shape=box];
        "Implementer subagent asks questions?" [shape=diamond];
        "Answer questions, provide context" [shape=box];
        "Implementer subagent implements, tests, commits, self-reviews" [shape=box];
        "Dispatch spec reviewer subagent (./spec-reviewer-prompt.md)" [shape=box];
        "Spec reviewer subagent confirms code matches spec?" [shape=diamond];
        "Implementer subagent fixes spec gaps" [shape=box];
        "Dispatch code quality reviewer subagent (./code-quality-reviewer-prompt.md)" [shape=box];
        "Code quality reviewer subagent approves?" [shape=diamond];
        "Implementer subagent fixes quality issues" [shape=box];
        "Reflection checkpoint? (./reflection-prompt.md)" [shape=diamond style=filled fillcolor=lightyellow];
        "Dispatch reflection subagent" [shape=box];
        "Reflection verdict?" [shape=diamond style=filled fillcolor=lightyellow];
        "Replan task (update spec, re-dispatch)" [shape=box style=filled fillcolor=lightsalmon];
        "Replan phase (stop, present to human)" [shape=box style=filled fillcolor=lightsalmon];
        "Mark task complete in TodoWrite" [shape=box];
    }

    "Read plan, extract all tasks with full text, note context, create TodoWrite" [shape=box];
    "More tasks remain?" [shape=diamond];
    "Dispatch final code reviewer subagent for entire implementation" [shape=box];
    "Use man:finishing-a-development-branch" [shape=box style=filled fillcolor=lightgreen];

    "Read plan, extract all tasks with full text, note context, create TodoWrite" -> "Dispatch implementer subagent (./implementer-prompt.md)";
    "Dispatch implementer subagent (./implementer-prompt.md)" -> "Implementer subagent asks questions?";
    "Implementer subagent asks questions?" -> "Answer questions, provide context" [label="yes"];
    "Answer questions, provide context" -> "Dispatch implementer subagent (./implementer-prompt.md)";
    "Implementer subagent asks questions?" -> "Implementer subagent implements, tests, commits, self-reviews" [label="no"];
    "Implementer subagent implements, tests, commits, self-reviews" -> "Dispatch spec reviewer subagent (./spec-reviewer-prompt.md)";
    "Dispatch spec reviewer subagent (./spec-reviewer-prompt.md)" -> "Spec reviewer subagent confirms code matches spec?";
    "Spec reviewer subagent confirms code matches spec?" -> "Implementer subagent fixes spec gaps" [label="no"];
    "Implementer subagent fixes spec gaps" -> "Dispatch spec reviewer subagent (./spec-reviewer-prompt.md)" [label="re-review"];
    "Spec reviewer subagent confirms code matches spec?" -> "Dispatch code quality reviewer subagent (./code-quality-reviewer-prompt.md)" [label="yes"];
    "Dispatch code quality reviewer subagent (./code-quality-reviewer-prompt.md)" -> "Code quality reviewer subagent approves?";
    "Code quality reviewer subagent approves?" -> "Implementer subagent fixes quality issues" [label="no"];
    "Implementer subagent fixes quality issues" -> "Dispatch code quality reviewer subagent (./code-quality-reviewer-prompt.md)" [label="re-review"];
    "Code quality reviewer subagent approves?" -> "Reflection checkpoint? (./reflection-prompt.md)";
    "Reflection checkpoint? (./reflection-prompt.md)" -> "Mark task complete in TodoWrite" [label="skip (not due)"];
    "Reflection checkpoint? (./reflection-prompt.md)" -> "Dispatch reflection subagent" [label="due (every 3rd task or 2+ rejections)"];
    "Dispatch reflection subagent" -> "Reflection verdict?";
    "Reflection verdict?" -> "Mark task complete in TodoWrite" [label="PROCEED"];
    "Reflection verdict?" -> "Replan task (update spec, re-dispatch)" [label="REPLAN_TASK"];
    "Reflection verdict?" -> "Replan phase (stop, present to human)" [label="REPLAN_PHASE"];
    "Replan task (update spec, re-dispatch)" -> "Dispatch implementer subagent (./implementer-prompt.md)";
    "Mark task complete in TodoWrite" -> "More tasks remain?";
    "More tasks remain?" -> "Dispatch implementer subagent (./implementer-prompt.md)" [label="yes"];
    "More tasks remain?" -> "Dispatch final code reviewer subagent for entire implementation" [label="no"];
    "Dispatch final code reviewer subagent for entire implementation" -> "Use man:finishing-a-development-branch";
}
```

## Replanning on Failure

Replanning activates when reflection returns `REPLAN_TASK` or `REPLAN_PHASE`, or when the same task fails review 3+ times.

### Task-Level Replan (REPLAN_TASK)

1. Read reflection findings — identify root cause (wrong approach, missing context, bad assumptions)
2. Update the task spec in the plan file:
   - Add a `## Revised Approach` section with new constraints from reflection
   - Preserve original spec for traceability — don't delete, add revision below
3. Re-dispatch implementer with: updated spec + reflection findings + prior attempt's diff summary
4. Reset review cycle counter to 0

**Max replans per task:** 2. If a task triggers REPLAN_TASK twice, escalate to human.

### Phase-Level Replan (REPLAN_PHASE)

1. **STOP** dispatching new tasks immediately
2. Compile all reflection findings into a summary
3. Present summary to human partner with options: revise remaining tasks / re-decompose / abort
4. Wait for human decision. Resume only after plan file is updated.

### Failure-Triggered Replan (no reflection needed)

If a task enters its 3rd review rejection cycle (spec or quality):
1. STOP the review loop
2. Run reflection regardless of whether it was due
3. Follow REPLAN_TASK or REPLAN_PHASE based on reflection verdict
4. If reflection says PROCEED despite 3 rejections: escalate to human
