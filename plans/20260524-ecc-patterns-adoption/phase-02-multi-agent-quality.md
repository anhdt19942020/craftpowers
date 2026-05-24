# Phase 2: Multi-Agent Quality (T4, T5, T6)

**Priority:** P1 — High-value patterns for decision quality and context accuracy
**Status:** Complete ✅
**Effort:** 1-2 days
**Depends on:** None (parallel with Phase 1)

## Overview

Three complementary patterns that improve multi-agent workflows: anti-anchoring prevents bias in deliberation, santa-method enforces binary quality gates, and iterative retrieval improves subagent context gathering.

## Key Insights

- Anti-anchoring is ECC's most sophisticated anti-bias technique — main agent writes position FIRST, subagents never see it
- Santa-method replaces advisory review with hard PASS/FAIL gate — both reviewers must agree
- Iterative retrieval solves the "agent doesn't know what context it needs" problem without vector DB
- All three are skill-only — no hook changes required

---

### Task 1: Anti-anchoring council skill

**Depends on:** none

**Files:**
- Create: `skills/council/SKILL.md`

- [x] **Step 1: Create the council skill directory**

Run: `mkdir -p skills/council`

- [x] **Step 2: Write SKILL.md**

```markdown
---
name: council
description: Anti-anchoring deliberation — main agent writes position before spawning independent reviewers. Prevents bias in multi-agent decisions.
---

# Council — Anti-Anchoring Deliberation

Multi-perspective decision-making with bias prevention. The main agent commits to a position BEFORE seeing any subagent output.

## Usage

```
/man-council <question or decision to deliberate>
```

## Protocol

### Phase 1: Position Lock (MANDATORY)

Before spawning any subagent, YOU must:

1. Write your position on the question (2-4 sentences)
2. Save it to a temp file: `plans/visuals/council-position-{timestamp}.md`
3. Include your confidence level (0-100%)
4. List assumptions you're making

**Why first:** If you read subagent opinions before forming yours, you anchor to their framing. Writing first forces independent reasoning.

### Phase 2: Spawn Perspectives (Parallel)

Spawn 3 subagents simultaneously via Agent tool. Each gets:
- The original question ONLY (not your position)
- A compact context brief (relevant file paths, not full conversation)
- A specific perspective to argue from

**Perspectives:**
1. **Skeptic** — "Find the strongest argument AGAINST this approach. What failure modes exist? What are we not seeing?"
2. **Pragmatist** — "What is the simplest approach that works? What complexity can we eliminate? What ships fastest?"
3. **Architect** — "How does this affect the system in 6 months? What constraints does this create? What does this make harder?"

**Anti-anchoring rules for subagent prompts:**
- DO NOT include your position or any hint of your preference
- DO NOT include conversation history that reveals your leaning
- DO include: the question, relevant file paths, project constraints
- Each subagent MUST end with a clear RECOMMENDATION (not just analysis)

### Phase 3: Synthesis

After all 3 subagents return:

1. Read all 3 perspectives
2. Re-read your original position
3. For each perspective that contradicts your position:
   - State the contradiction explicitly
   - Evaluate whether their evidence is stronger than your assumption
4. Write final recommendation with:
   - Decision and reasoning
   - Which perspectives influenced the decision
   - Dissenting views acknowledged
   - Confidence level (compare to your Phase 1 confidence)

### Output Format

```markdown
## Council Decision: [topic]

**My initial position:** [summary, confidence X%]

**Skeptic:** [key point]
**Pragmatist:** [key point]
**Architect:** [key point]

**Final decision:** [decision, confidence Y%]
**Changed by:** [which perspectives shifted thinking, or "none — initial position held"]
**Dissent noted:** [any unresolved disagreement]
```

## When to Use

- Architectural decisions affecting 3+ files
- Technology/library choices
- Approach selection when multiple valid options exist
- Any decision where you feel >80% confident (overconfidence risk)

## When NOT to Use

- Bug fixes with clear root cause
- Implementation of an already-decided plan
- Simple questions with one obvious answer
```

- [x] **Step 3: Commit**

```bash
git add skills/council/SKILL.md
git commit -m "feat(skills): add council skill with anti-anchoring deliberation protocol"
```

---

### Task 2: Santa-method binary gate skill

**Depends on:** none

**Files:**
- Create: `skills/santa-method/SKILL.md`

- [x] **Step 1: Create the santa-method skill directory**

Run: `mkdir -p skills/santa-method`

- [x] **Step 2: Write SKILL.md**

```markdown
---
name: santa-method
description: Binary quality gate — 2 independent reviewers must both PASS. Stronger than advisory review. Use for pre-merge or pre-ship validation.
---

# Santa Method — Binary Quality Gate

Two independent reviewers, identical rubric, no shared context. BOTH must pass for the output to ship. If either fails, fix and re-run BOTH (fresh context each time).

## Usage

```
/man-santa <target> [--rubric <path>]
```

Where `<target>` is a file path, directory, branch diff, or PR number.

## Protocol

### Phase 1: Prepare Rubric

If `--rubric` provided, read the rubric file. Otherwise, build a default rubric from context:

**Default rubric categories:**
1. **Correctness** — Does the code do what it claims? Are edge cases handled?
2. **Safety** — No security vulnerabilities, no data loss paths, no credential exposure
3. **Conventions** — Follows project patterns (from CLAUDE.md, existing code style)
4. **Completeness** — All acceptance criteria met, no half-finished implementations
5. **Side effects** — No regressions in adjacent code, no broken contracts

Each category: PASS or FAIL with specific evidence.

### Phase 2: Spawn Reviewers (Parallel)

Spawn 2 reviewer agents simultaneously. Each receives:
- The rubric (identical for both)
- The target files/diff to review
- Instruction: "Review independently. Return PASS or FAIL for each rubric category with specific evidence."

**Anti-anchoring:** Reviewers are spawned with `isolation: "worktree"` if available, or with minimal context (no conversation history, no prior review results).

**Each reviewer MUST return:**
```
VERDICT: PASS | FAIL
Categories:
- Correctness: PASS/FAIL — [evidence]
- Safety: PASS/FAIL — [evidence]
- Conventions: PASS/FAIL — [evidence]
- Completeness: PASS/FAIL — [evidence]
- Side effects: PASS/FAIL — [evidence]
Blocking issues: [list or "none"]
```

### Phase 3: Gate Decision

| Reviewer 1 | Reviewer 2 | Decision |
|-----------|-----------|----------|
| PASS | PASS | ✅ SHIP — output approved |
| PASS | FAIL | ❌ FIX — apply Reviewer 2's findings |
| FAIL | PASS | ❌ FIX — apply Reviewer 1's findings |
| FAIL | FAIL | ❌ FIX — merge both finding sets |

### Phase 4: Convergence Loop (if FAIL)

1. Present blocking issues to user
2. Fix issues (user or agent)
3. Re-run BOTH reviewers with FRESH context (no memory of prior run)
4. Max 3 convergence iterations
5. If still failing after 3: report BLOCKED with all unresolved issues

**Why fresh context:** Reviewers who saw the prior version may anchor to "it was mostly fine" and miss new issues introduced by the fix.

## When to Use

- Pre-merge gate for critical PRs
- Pre-ship validation (`/man-ship` pipeline)
- After major refactors
- When advisory review feels insufficient

## When NOT to Use

- Quick fixes (1-2 line changes)
- Draft/WIP code
- Exploratory prototypes
```

- [x] **Step 3: Commit**

```bash
git add skills/santa-method/SKILL.md
git commit -m "feat(skills): add santa-method binary quality gate with convergence loop"
```

---

### Task 3: Iterative retrieval skill

**Depends on:** none

**Files:**
- Create: `skills/iterative-retrieval/SKILL.md`

- [x] **Step 1: Create the iterative-retrieval skill directory**

Run: `mkdir -p skills/iterative-retrieval`

- [x] **Step 2: Write SKILL.md**

```markdown
---
name: iterative-retrieval
description: Multi-round context gathering for subagents. DISPATCH → EVALUATE → REFINE → CONVERGE loop. Solves "agent doesn't know what context it needs" problem.
---

# Iterative Retrieval — Smart Context Gathering

A structured loop for gathering the right context before dispatching implementation agents. Replaces the "hope the prompt has enough context" approach with systematic discovery.

## Usage

```
/man-retrieve <question or task description>
```

## Protocol

### Round 1: DISPATCH (Broad Search)

Spawn an Explore agent with a broad query derived from the task:

```
Agent({
  subagent_type: "Explore",
  prompt: "Find all files related to: [task description]. Search broadly — include tests, configs, types, and adjacent modules. Report: file paths, key symbols, and a 1-line summary per file.",
  description: "Broad context search"
})
```

### Round 2: EVALUATE (Score Relevance)

For each file the search returned, score relevance 0.0-1.0:

| Score | Meaning | Action |
|-------|---------|--------|
| 0.8-1.0 | Directly affected by this task | Read fully, include in context |
| 0.5-0.7 | Related but not directly changed | Read key sections, include summary |
| 0.2-0.4 | Tangentially related | Note existence, don't include |
| 0.0-0.1 | False positive | Drop |

### Round 3: REFINE (Fix Terminology)

If Round 1 missed important context (common when you don't know the codebase's terminology):

1. Identify terminology mismatches — "the codebase calls it X, I searched for Y"
2. Identify structural mismatches — "I searched in `src/`, but this project uses `lib/`"
3. Spawn a second Explore with refined queries

### Round 4: CONVERGE (Exit Criteria)

Exit the loop when:
- At least 3 high-relevance (≥0.8) files found
- All types/interfaces referenced by those files are also found
- Test files for the target area identified
- OR: 3 iterations completed (hard cap)

### Output: Context Brief

```markdown
## Context Brief for: [task]

### Core files (will be modified):
- `path/to/file.py:10-50` — [what it does, why it matters]

### Dependencies (must stay compatible):
- `path/to/dep.py` — [interface contract]

### Tests (must pass):
- `tests/test_file.py` — [what it covers]

### Conventions observed:
- [naming patterns, import style, error handling approach]

### Terminology map:
- [task term] → [codebase term]
```

## Integration

This skill's output is designed to feed directly into:
- `implementer` agent prompts
- `writing-plans` task descriptions
- `codebase-explorer` follow-up queries

## When to Use

- Before implementing a feature in an unfamiliar area
- When a subagent failed because it lacked context
- When you're unsure which files a change will touch
- Before writing a plan for a complex feature

## When NOT to Use

- You already know the exact files and interfaces
- The task is in a well-understood area with clear file paths
- Simple bug fixes with obvious location
```

- [x] **Step 3: Commit**

```bash
git add skills/iterative-retrieval/SKILL.md
git commit -m "feat(skills): add iterative-retrieval skill for smart context gathering"
```

---

## Success Criteria

- [x] `/man-council` produces anti-anchored deliberation with position-lock-first protocol
- [x] `/man-santa` runs 2 independent reviewers and enforces binary PASS/FAIL gate
- [x] `/man-retrieve` gathers progressively better context across up to 3 iterations
- [x] All three skills are self-contained markdown — no Python dependencies
- [x] Skills follow existing naming and structure conventions

## Risk Assessment

- **Anti-anchoring adds token cost** — 3 subagent spawns per deliberation. Mitigated by using only for significant decisions.
- **Santa-method convergence may loop** — capped at 3 iterations with BLOCKED exit.
- **Iterative retrieval may over-fetch** — relevance scoring and hard cap prevent context bloat.
