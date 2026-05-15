---
name: man-assess
description: "Use when a user is new to mankit, asks 'where do I start', 'what should I use', 'which command', 'onboarding', or seems lost among the available skills and agents."
---

# Workflow Discovery

Help your human partner find the right mankit workflows for their current situation. This is a situational recommender, not a knowledge quiz.

<HARD-GATE>
Do NOT skip rounds. Do NOT recommend workflows without completing all 3 rounds. Even if the answer seems obvious from Round 1, Rounds 2-3 refine the recommendation.
</HARD-GATE>

## Step 1 — What are you working on?

Use AskUserQuestion:

**Question** (header: "Situation", multiSelect: false):
"What best describes what you're doing right now?"
Options:
1. **"Building something new"** — New feature, new project, new component
2. **"Hunting a bug"** — Something is broken, test failing, unexpected behavior
3. **"Shipping or reviewing"** — PR, release, code review, merge prep
4. **"Exploring or refactoring"** — Understanding code, improving structure, cleaning up

Record the answer as `SITUATION`.

## Step 2 — What's blocking you?

Use AskUserQuestion, tailored to the `SITUATION` from Step 1:

**If SITUATION = "Building something new"** (header: "Blocker", multiSelect: false):
"What's the hardest part right now?"
Options:
1. **"Unclear requirements"** — Not sure exactly what to build or how it should work
2. **"Design decisions"** — Multiple approaches, unsure which architecture fits
3. **"Execution"** — I know what to build but the implementation is complex
4. **"Coordination"** — Multiple files/systems to change in parallel

**If SITUATION = "Hunting a bug"** (header: "Blocker", multiSelect: false):
"What's making this bug hard?"
Options:
1. **"Can't find the root cause"** — I see symptoms but not the source
2. **"Multiple possible causes"** — Several things could explain the behavior
3. **"Intermittent or subtle"** — Hard to reproduce or appears in specific conditions
4. **"Fix breaks other things"** — Every fix introduces a regression

**If SITUATION = "Shipping or reviewing"** (header: "Blocker", multiSelect: false):
"What do you need help with?"
Options:
1. **"Code review quality"** — Want thorough review before merge
2. **"Release checklist"** — Env vars, migrations, breaking changes, changelog
3. **"PR preparation"** — Writing description, checking for issues
4. **"Finishing touches"** — Tests passing but not sure if it's truly ready

**If SITUATION = "Exploring or refactoring"** (header: "Blocker", multiSelect: false):
"What's your goal?"
Options:
1. **"Understand unfamiliar code"** — Need to map structure and conventions
2. **"Find improvement opportunities"** — Architecture, patterns, duplication
3. **"Execute a refactor safely"** — Know what to change but worried about breaking things
4. **"Document decisions"** — Record why things are the way they are

Record the answer as `BLOCKER`.

## Step 3 — How much agent autonomy?

Use AskUserQuestion:

**Question** (header: "Autonomy", multiSelect: false):
"How do you prefer to work with AI agents?"
Options:
1. **"I drive everything"** — I want suggestions and tools, but I control each step
2. **"Parallel helpers"** — Dispatch independent subagents, review their output
3. **"Full team"** — Agent teams coordinating across tasks with a lead agent
4. **"Not sure yet"** — Show me the options and help me decide

Record the answer as `AUTONOMY`.

## Step 4 — Generate Workflow Recommendation

Based on `SITUATION` + `BLOCKER` + `AUTONOMY`, output a concrete recommendation using the mapping below.

### Building something new

| Blocker | Primary Workflow | Next Step |
|---------|-----------------|-----------|
| Unclear requirements | `/man-brainstorm` — explore intent, constraints, success criteria | Then `/man-plan` for implementation plan |
| Design decisions | `/man-brainstorm` then `man:adversarial-design` to stress-test | `subagent_type: tuan-du` for architecture review |
| Execution | `/man-plan` — break work into Task DAG with TDD steps | `man:subagent-driven-development` to dispatch per task |
| Coordination | `/man-plan` — map dependencies, then `man:agent-teams` | tam quốc agents dispatched per task type |

### Hunting a bug

| Blocker | Primary Workflow | Next Step |
|---------|-----------------|-----------|
| Can't find root cause | `/man-fix` — systematic debugging with hypothesis tree | `subagent_type: bang-thong` for deep investigation |
| Multiple possible causes | `/man-fix` with competing-hypothesis mode | Multiple `bang-thong` agents test hypotheses in parallel |
| Intermittent or subtle | `man:debug-flight-recorder` — instrument, reproduce, collect | Then `/man-fix` once you have logs |
| Fix breaks other things | `/man-fix` then `man:hoang-trung` for test coverage review | `subagent_type: phap-chinh` to review the fix |

### Shipping or reviewing

| Blocker | Primary Workflow | Next Step |
|---------|-----------------|-----------|
| Code review quality | `man:requesting-code-review` — structured review request | `subagent_type: phap-chinh` + `tu-ma-y` for security |
| Release checklist | `/man-release` — pre-deploy gate with release-prep | `subagent_type: luu-bi` audits env vars, migrations, changelog |
| PR preparation | `man:finishing-a-development-branch` — PR checklist | `man:verification-before-completion` before submit |
| Finishing touches | `man:verification-before-completion` — final gate | `subagent_type: hoang-trung` for test coverage gaps |

### Exploring or refactoring

| Blocker | Primary Workflow | Next Step |
|---------|-----------------|-----------|
| Understand unfamiliar code | `/man-explore` — read-only codebase scout | `subagent_type: gia-cat-luong` for deep mapping |
| Find improvements | `man:architecture-decision-records` — find deepening opportunities | `subagent_type: tuan-du` for system-level analysis |
| Execute refactor safely | `man:structured-refactoring` — safe incremental changes | `man:test-driven-development` for TDD cycle |
| Document decisions | `man:architecture-decision-records` — ADR workflow | `subagent_type: ma-luong` for documentation |

### Autonomy Modifier

Adjust the recommendation wording based on `AUTONOMY`:

- **"I drive everything"** → Emphasize inline skills. Say: "These skills run in your session — you control each step."
- **"Parallel helpers"** → Add: "Use `man:dispatching-parallel-agents` to run independent tasks in parallel. Dispatch tam quốc agents by `subagent_type`."
- **"Full team"** → Add: "Use `man:agent-teams` for coordinated multi-agent execution. Start with `/man-plan` to get a Task DAG, then dispatch a team."
- **"Not sure yet"** → Say: "Start inline. If it feels slow or the work has independent tasks, run `/man-assess` again and pick 'Parallel helpers'."

### Output Format

Present the recommendation as:

```
## Your Mankit Workflow

**Situation:** [one-line summary from SITUATION + BLOCKER]

### Start Here

1. **`[primary command/skill]`** — [what it does for their specific case]
   → Type: `[exact invocation]`

2. **`[next step]`** — [when to use this]
   → Type: `[exact invocation]`

### Agent Dispatch

[If AUTONOMY is parallel/team]:
| Task Type | Agent | Dispatch |
|-----------|-------|----------|
| [type from recommendation] | [tam quốc name] | `subagent_type: [id]` |

[If AUTONOMY is inline/"not sure"]:
Skills run in your session — no subagent dispatch needed. If this feels slow, try `/man-assess` again and pick "Parallel helpers".

### Quick Reference

| When you need... | Use |
|-----------------|-----|
| [related need 1] | `[command]` |
| [related need 2] | `[command]` |
| [related need 3] | `[command]` |

### Want to explore more?

- Run `/man-assess` again anytime your situation changes
- Run `/man-check` to verify mankit is fully configured
- All commands: type `/man-` and browse the list
```

## Step 5 — Offer Follow-up

Use AskUserQuestion:

**Question** (header: "Next", multiSelect: false):
"What would you like to do?"
Options:
1. **"Start the recommended workflow"** — Run the primary command right now
2. **"Explain a recommendation"** — Tell me more about one of the suggestions
3. **"Reassess"** — My situation is different, let me retake
4. **"Done"** — I have what I need

- **"Start the recommended workflow"** → Invoke the primary skill or command from the recommendation.
- **"Explain a recommendation"** → Ask which item, then give a 3-4 sentence explanation with a concrete example of when it shines.
- **"Reassess"** → Go back to Step 1.
- **"Done"** → End with: "Run `/man-assess` anytime your situation changes."
