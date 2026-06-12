# GAN Adversarial — Generator↔Evaluator Loop

Inspired by GANs: Generator produces output, Evaluator scores against rubric, loop continues until quality threshold met.

**Usage:** `/man-gan <task description> [--threshold <score>] [--max-rounds <n>]`

Defaults: threshold = 7.0/10, max-rounds = 3

## Protocol

### Phase 0: Setup
1. Parse task description
2. Generate evaluation rubric from task (or use provided rubric)
3. Create coordination file: `plans/visuals/gan-{timestamp}.md`

### Phase 1: Generate
Spawn Generator agent (subagent_type: "implementer"). Generator writes output to files.

### Phase 2: Evaluate
Spawn Evaluator agent (INDEPENDENT — no shared context with Generator, subagent_type: "code-reviewer").

**Anti-sycophancy rules:**
- Evaluator NEVER sees Generator's reasoning
- Evaluator receives ONLY output files + rubric
- Evaluator MUST provide at least 2 specific criticisms even on high-scoring output
- If all dimensions 9+: force re-evaluation with "find 3 specific weaknesses"

### Phase 3: Iterate or Converge
- Score ≥ threshold → CONVERGE, output ships
- Score < threshold → spawn NEW Generator with original task + previous output + Evaluator feedback, then NEW Evaluator. Repeat until threshold or max-rounds.

### Phase 4: Report
```markdown
## GAN Report: [task]
| Round | Score | Key Feedback |
|-------|-------|-------------|
| 1 | 5.2 | Missing error handling, unclear API |
| 2 | 7.1 | Error handling added, API documented |
| 3 | 8.3 | Minor style issues only |
**Final score:** 8.3/10 | **Verdict:** PASS
```

## Default Rubrics

**Code:** Correctness, Readability, Safety, Completeness, Conventions (each 1-10)

**Documentation:** Accuracy, Completeness, Clarity, Examples, Structure (each 1-10)

## When to Use
- Critical deliverables (public APIs, security-sensitive code)
- When first-draft quality is consistently insufficient
- Complex refactors where side effects are likely

## When NOT to Use
- Quick fixes, exploratory prototypes, time-sensitive work
- Each round = 2 agent spawns (~20-50k tokens). 3 rounds = 6 spawns.

## Combining
- **+ Council:** council decides approach, GAN executes it
- **+ Santa-Method:** GAN for generation, santa-method for final gate
