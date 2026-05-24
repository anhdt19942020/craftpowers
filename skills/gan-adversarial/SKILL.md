---
name: gan-adversarial
description: Generator↔Evaluator adversarial loop for high-quality output. Iterates until quality threshold met. Use for critical deliverables where advisory review is insufficient.
---

# GAN Adversarial — Generator↔Evaluator Loop

Inspired by GANs (Generative Adversarial Networks): a Generator produces output, an Evaluator scores it against a rubric, and the loop continues until quality threshold is met.

## Usage

```
/man-gan <task description> [--threshold <score>] [--max-rounds <n>]
```

Defaults: threshold = 7.0/10, max-rounds = 3

## Protocol

### Phase 0: Setup

1. Parse the task description
2. Generate evaluation rubric from task (or use provided rubric)
3. Create coordination file: `plans/visuals/gan-{timestamp}.md`

### Phase 1: Generate (Round 1)

Spawn a Generator agent:

```
Agent({
  subagent_type: "implementer",
  prompt: "[task description]\n\nProduce the highest quality output you can. This will be evaluated by an independent reviewer.",
  description: "GAN Generator R1"
})
```

The Generator writes its output to files (code, docs, config — whatever the task requires).

### Phase 2: Evaluate

Spawn an Evaluator agent (INDEPENDENT — no shared context with Generator):

```
Agent({
  subagent_type: "code-reviewer",
  prompt: "Evaluate the following output against this rubric. Score each dimension 1-10. Be harsh — this is adversarial review, not encouragement.\n\nRubric:\n[rubric]\n\nFiles to review:\n[file list]\n\nReturn:\n- Per-dimension scores\n- Overall score (average)\n- Specific, actionable feedback for each dimension scoring below 7\n- VERDICT: PASS (≥threshold) or FAIL",
  description: "GAN Evaluator R1"
})
```

**Anti-sycophancy rules for Evaluator:**
- Evaluator NEVER sees Generator's reasoning or self-assessment
- Evaluator receives ONLY the output files and the rubric
- Evaluator MUST provide at least 2 specific criticisms even on high-scoring output
- Score inflation detection: if all dimensions are 9+, force re-evaluation with "find 3 specific weaknesses"

### Phase 3: Iterate or Converge

**If Evaluator score ≥ threshold:** CONVERGE — output ships.

**If Evaluator score < threshold:**
1. Extract Evaluator's actionable feedback
2. Spawn a NEW Generator with:
   - Original task
   - Previous output (as reference, not as starting point)
   - Evaluator's specific feedback
   - Instruction: "Improve the output based on this feedback. Do NOT simply patch — re-approach the weak areas."
3. Spawn a NEW Evaluator (fresh context)
4. Repeat until threshold met or max-rounds reached

### Phase 4: Report

Write to coordination file:

```markdown
## GAN Report: [task]

| Round | Score | Key Feedback |
|-------|-------|-------------|
| 1 | 5.2 | Missing error handling, unclear API |
| 2 | 7.1 | Error handling added, API documented |
| 3 | 8.3 | Minor style issues only |

**Final score:** 8.3/10
**Rounds:** 3
**Verdict:** PASS
```

## Rubric Template

If no custom rubric provided, generate from task type:

### Code Output Rubric
1. **Correctness** (1-10): Does it work? Edge cases handled?
2. **Readability** (1-10): Clear naming, structure, comments where needed?
3. **Safety** (1-10): No security issues, no data loss paths?
4. **Completeness** (1-10): All requirements met? Nothing half-done?
5. **Conventions** (1-10): Follows project patterns?

### Documentation Rubric
1. **Accuracy** (1-10): Matches actual behavior?
2. **Completeness** (1-10): All features documented?
3. **Clarity** (1-10): Clear for target audience?
4. **Examples** (1-10): Working examples for key features?
5. **Structure** (1-10): Logical organization, easy to navigate?

## Combining with Other Patterns

- **+ Council:** Use council to decide the approach, then GAN to execute it
- **+ Santa-Method:** Use GAN for generation, santa-method for final gate
- **+ Iterative Retrieval:** Use retrieval to gather context, then GAN to produce output

## When to Use

- Critical deliverables (public APIs, documentation, security-sensitive code)
- When first-draft quality is consistently insufficient
- When you want measurable quality improvement across iterations
- Complex refactors where side effects are likely

## When NOT to Use

- Quick fixes or small changes
- Exploratory prototypes
- Tasks where "good enough" is acceptable
- Time-sensitive work (each round costs ~2-5 minutes)

## Cost Awareness

Each round spawns 2 agents (generator + evaluator). A 3-round session = 6 agent spawns.
Typical token cost: 20-50k tokens per round depending on output size.
Use judiciously — this is the premium quality option.
