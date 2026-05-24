# Phase 6: Advanced Patterns (P9, P12)

**Priority:** P3 — Complex patterns requiring mature infrastructure
**Status:** Not started
**Effort:** 2-3 weeks
**Depends on:** Phase 2 (multi-agent quality), Phase 5 (hook infrastructure)

## Overview

Two advanced patterns: sub-skill architecture enables nested skills with namespace routing, and GAN adversarial pattern creates generator↔evaluator loops for high-quality output. These are the most complex patterns from ECC and require the foundation from earlier phases.

## Key Insights

- Sub-skill architecture unlocks composable skill design — skills can import from each other
- GAN pattern is ECC's highest-quality-output technique — generator and evaluator iterate until threshold met
- Both patterns are infrastructure-level — they change how skills work, not just add new skills
- P9 is primarily a skill-loader change; P12 is a new skill that uses Phase 2's anti-anchoring

---

### Task 1: Sub-skill architecture (P9)

**Depends on:** none (but benefits from Phase 5 hookify for discovery)

**Files:**
- Create: `hooks/lib/skill_resolver.py`
- Modify: `skills/using-man/SKILL.md` (add sub-skill documentation)

- [ ] **Step 1: Create hooks/lib/skill_resolver.py**

```python
"""Sub-skill resolver — enables nested SKILL.md files with namespace routing.

Supports:
- parent:child namespace — e.g., man:council:skeptic resolves to
  skills/council/skeptic/SKILL.md
- Nested SKILL.md discovery — scan for SKILL.md at any depth
- Parent context injection — child skills inherit parent's context

Resolution order:
1. Exact match: skills/{name}/SKILL.md
2. Namespace match: skills/{parent}/{child}/SKILL.md
3. Deep scan: skills/{parent}/**/SKILL.md (expensive, cached)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

_cache: dict[str, str] = {}


def resolve_skill(name: str, plugin_root: str | None = None) -> str | None:
    """Resolve a skill name (possibly namespaced) to a SKILL.md path.
    
    Returns absolute path to SKILL.md or None if not found.
    """
    root = plugin_root or os.environ.get("CLAUDE_PLUGIN_ROOT", os.getcwd())
    skills_dir = Path(root) / "skills"

    if not skills_dir.is_dir():
        return None

    # Check cache
    cache_key = f"{root}:{name}"
    if cache_key in _cache:
        cached = _cache[cache_key]
        if Path(cached).exists():
            return cached
        del _cache[cache_key]

    # Split namespace
    parts = name.split(":")
    # Remove 'man' prefix if present
    if parts and parts[0] == "man":
        parts = parts[1:]

    if not parts:
        return None

    # Try exact match: skills/{name}/SKILL.md
    if len(parts) == 1:
        exact = skills_dir / parts[0] / "SKILL.md"
        if exact.exists():
            _cache[cache_key] = str(exact)
            return str(exact)

    # Try namespace match: skills/{parent}/{child}/SKILL.md
    if len(parts) >= 2:
        namespaced = skills_dir / parts[0] / parts[1] / "SKILL.md"
        if namespaced.exists():
            _cache[cache_key] = str(namespaced)
            return str(namespaced)

    # Try deep scan (expensive)
    if len(parts) >= 2:
        parent_dir = skills_dir / parts[0]
        if parent_dir.is_dir():
            child_name = parts[-1]
            for skill_file in parent_dir.rglob("SKILL.md"):
                if skill_file.parent.name == child_name:
                    _cache[cache_key] = str(skill_file)
                    return str(skill_file)

    return None


def list_sub_skills(parent: str, plugin_root: str | None = None) -> list[dict[str, Any]]:
    """List all sub-skills under a parent skill."""
    root = plugin_root or os.environ.get("CLAUDE_PLUGIN_ROOT", os.getcwd())
    skills_dir = Path(root) / "skills" / parent

    if not skills_dir.is_dir():
        return []

    sub_skills: list[dict[str, Any]] = []
    for skill_file in sorted(skills_dir.rglob("SKILL.md")):
        if skill_file.parent == skills_dir:
            continue  # Skip parent's own SKILL.md
        rel = skill_file.parent.relative_to(skills_dir)
        sub_skills.append({
            "name": f"{parent}:{rel}",
            "path": str(skill_file),
            "parent": parent,
        })

    return sub_skills


def clear_cache() -> None:
    """Clear the resolution cache. Used in tests."""
    _cache.clear()
```

- [ ] **Step 2: Add sub-skill documentation to using-man skill**

Append to `skills/using-man/SKILL.md` a section on sub-skills:

```markdown
## Sub-Skills (Namespaced Skills)

Skills can contain nested sub-skills using namespace syntax:

```
/man-council:skeptic    # Invoke the skeptic sub-skill within council
/man-writing-plans:cold-execution  # Invoke cold-execution check within writing-plans
```

### Creating Sub-Skills

Place a `SKILL.md` inside a subdirectory of the parent skill:

```
skills/
├── council/
│   ├── SKILL.md              # Parent: /man-council
│   ├── skeptic/
│   │   └── SKILL.md          # Sub-skill: /man-council:skeptic
│   └── pragmatist/
│       └── SKILL.md          # Sub-skill: /man-council:pragmatist
```

Sub-skills inherit the parent's context and can be invoked independently.
```

- [ ] **Step 3: Write tests**

```python
# tests/test_skill_resolver.py
import os
import tempfile
from hooks.lib.skill_resolver import resolve_skill, list_sub_skills, clear_cache

def test_exact_match():
    with tempfile.TemporaryDirectory() as d:
        skill_dir = os.path.join(d, "skills", "council")
        os.makedirs(skill_dir)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        with open(skill_file, "w") as f:
            f.write("# Council")
        clear_cache()
        result = resolve_skill("council", d)
        assert result == skill_file

def test_namespace_match():
    with tempfile.TemporaryDirectory() as d:
        sub_dir = os.path.join(d, "skills", "council", "skeptic")
        os.makedirs(sub_dir)
        skill_file = os.path.join(sub_dir, "SKILL.md")
        with open(skill_file, "w") as f:
            f.write("# Skeptic")
        clear_cache()
        result = resolve_skill("council:skeptic", d)
        assert result == skill_file

def test_man_prefix_stripped():
    with tempfile.TemporaryDirectory() as d:
        skill_dir = os.path.join(d, "skills", "council")
        os.makedirs(skill_dir)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        with open(skill_file, "w") as f:
            f.write("# Council")
        clear_cache()
        result = resolve_skill("man:council", d)
        assert result == skill_file

def test_not_found():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "skills"))
        clear_cache()
        result = resolve_skill("nonexistent", d)
        assert result is None

def test_list_sub_skills():
    with tempfile.TemporaryDirectory() as d:
        parent = os.path.join(d, "skills", "council")
        os.makedirs(parent)
        with open(os.path.join(parent, "SKILL.md"), "w") as f:
            f.write("# Parent")
        sub = os.path.join(parent, "skeptic")
        os.makedirs(sub)
        with open(os.path.join(sub, "SKILL.md"), "w") as f:
            f.write("# Skeptic")
        result = list_sub_skills("council", d)
        assert len(result) == 1
        assert "skeptic" in result[0]["name"]
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_skill_resolver.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add hooks/lib/skill_resolver.py skills/using-man/SKILL.md tests/test_skill_resolver.py
git commit -m "feat(skills): add sub-skill architecture with namespace routing"
```

---

### Task 2: GAN adversarial pattern skill (P12)

**Depends on:** Phase 2 Task 1 (council/anti-anchoring), Phase 2 Task 2 (santa-method)

**Files:**
- Create: `skills/gan-adversarial/SKILL.md`

- [ ] **Step 1: Create skills/gan-adversarial/SKILL.md**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add skills/gan-adversarial/SKILL.md
git commit -m "feat(skills): add GAN adversarial pattern for iterative quality improvement"
```

---

## Success Criteria

- [ ] Sub-skill resolver handles exact, namespaced, and deep-scan resolution
- [ ] `man:parent:child` syntax routes to nested SKILL.md files
- [ ] Resolution results are cached for performance
- [ ] GAN skill defines clear Generator↔Evaluator protocol with scoring rubric
- [ ] Anti-sycophancy rules prevent score inflation
- [ ] GAN coordination file tracks rounds and scores
- [ ] Both patterns integrate with Phase 2 skills (council, santa-method)

## Risk Assessment

- **Sub-skill resolution adds latency** — mitigated by caching. Only deep-scan is expensive.
- **GAN pattern is token-expensive** — 6 agent spawns for 3 rounds. Documented cost awareness. Use selectively.
- **Score calibration** — threshold of 7.0 is arbitrary. May need tuning per project. Configurable via `--threshold`.
- **Evaluator may not be harsh enough** — anti-sycophancy rules help but LLMs tend toward positive scores. Score inflation detection forces re-evaluation.
- **Sub-skill namespace collision** — two skills with same parent:child name. Mitigated by exact-match-first resolution order.
