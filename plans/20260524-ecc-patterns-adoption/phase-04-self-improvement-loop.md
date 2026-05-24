# Phase 4: Self-Improvement Loop (P8, P6)

**Priority:** P2 — Closes the feedback loop: usage → instincts → better behavior
**Status:** Complete ✅
**Effort:** 2-3 days
**Depends on:** Phase 1 (Instinct System)

## Overview

Two complementary systems: the Conversation Analyzer detects user corrections and auto-generates instinct files, and Behavioral Compliance Testing validates that agents actually follow skill instructions. Together they create a self-healing loop: user corrects → instinct generated → behavior improves → compliance verified.

## Key Insights

- ECC's most powerful meta-pattern: the system literally learns from its mistakes
- Conversation Analyzer runs post-session (at Stop hook), not real-time
- Behavioral compliance uses `claude -p` CLI for headless testing — no human needed
- P8 depends on P5 (instinct file format) being implemented first
- P6 can run independently but produces more value after P8 generates instincts to test

---

### Task 1: Conversation Analyzer (post-session instinct generator)

**Depends on:** Phase 1 Task 1 (instinct_loader.py exists)

**Files:**
- Create: `hooks/lib/conversation_analyzer.py`
- Create: `skills/conversation-analyzer/SKILL.md`
- Modify: `hooks/claude/stop.py`

- [x] **Step 1: Create hooks/lib/conversation_analyzer.py**

```python
"""Post-session conversation analyzer — detects user corrections and generates instinct candidates.

Runs at Stop hook. Scans the session transcript for correction patterns:
- "no, not that" / "don't" / "stop doing X" → negative instinct
- "yes, exactly" / "perfect" / approved unusual approach → positive instinct
- Repeated corrections on same topic → high confidence instinct

Output: instinct candidate files in {project}/.claude/instincts/candidates/
Candidates require human review before promotion to personal/.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any


CORRECTION_PATTERNS = [
    (r"\b(no[, ]+not that|don'?t do that|stop doing|wrong approach|that'?s not right)\b", "negative"),
    (r"\b(yes[, ]+exactly|perfect|that'?s right|keep doing that|exactly what I wanted)\b", "positive"),
    (r"\b(always use|never use|prefer|instead of|should have|next time)\b", "directive"),
]

CANDIDATE_DIR = ".claude/instincts/candidates"


def analyze_corrections(transcript: str) -> list[dict[str, Any]]:
    """Scan transcript for correction patterns. Returns candidate instincts."""
    candidates: list[dict[str, Any]] = []
    lines = transcript.split("\n")

    for i, line in enumerate(lines):
        for pattern, ptype in CORRECTION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                context_start = max(0, i - 3)
                context_end = min(len(lines), i + 3)
                context = "\n".join(lines[context_start:context_end])

                candidates.append({
                    "type": ptype,
                    "trigger_line": line.strip(),
                    "context": context,
                    "line_number": i + 1,
                    "confidence": 0.6 if ptype == "directive" else 0.5,
                })

    return candidates


def _slugify(text: str) -> str:
    """Convert text to a safe filename slug."""
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower().strip())
    return slug[:50].strip('-')


def write_candidate(candidate: dict[str, Any], project_root: str | None = None) -> str | None:
    """Write a candidate instinct file for human review. Returns file path or None."""
    root = project_root or os.getcwd()
    candidate_dir = Path(root) / CANDIDATE_DIR
    candidate_dir.mkdir(parents=True, exist_ok=True)

    slug = _slugify(candidate.get("trigger_line", "unknown")[:40])
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{slug}.md"
    filepath = candidate_dir / filename

    content = f"""---
id: {slug}
confidence: {candidate['confidence']}
type: candidate
source: conversation-analyzer
detected: {datetime.now().isoformat()}
---

# Candidate Instinct: {candidate['type']}

## Trigger
{candidate['trigger_line']}

## Context
```
{candidate['context']}
```

## Action
[HUMAN REVIEW REQUIRED] — Describe the behavioral rule this correction implies.

## Status
- [x] Reviewed by human
- [x] Promoted to `.claude/instincts/personal/` (raise confidence to 0.7+)
- [x] Rejected (delete this file)
"""

    try:
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)
    except Exception:
        return None


def run_analysis(transcript: str, project_root: str | None = None) -> list[str]:
    """Full analysis pipeline. Returns list of created candidate file paths."""
    candidates = analyze_corrections(transcript)
    paths: list[str] = []
    for c in candidates:
        path = write_candidate(c, project_root)
        if path:
            paths.append(path)
    return paths
```

- [x] **Step 2: Integrate into Stop hook**

Read `hooks/claude/stop.py` and add conversation analyzer call. After existing stop logic:

```python
# Post-session conversation analysis (generates instinct candidates)
try:
    from hooks.lib.conversation_analyzer import run_analysis
    from hooks.lib.project_config import get_config

    cfg = get_config()
    if cfg.get("conversation_analyzer", {}).get("enabled", False):
        transcript = data.get("transcript", "") or data.get("conversation", "")
        if transcript and len(transcript) > 100:
            candidates = run_analysis(transcript)
            if candidates:
                import sys
                print(f"[conversation-analyzer] Generated {len(candidates)} instinct candidate(s) in .claude/instincts/candidates/", file=sys.stderr)
except Exception:
    pass  # analyzer must not break Stop hook
```

- [x] **Step 3: Add config for conversation_analyzer to _DEFAULTS**

In `hooks/lib/project_config.py`:
```python
"conversation_analyzer": {
    "enabled": False,
    "min_transcript_length": 100,
},
```

- [x] **Step 4: Create /man-analyze skill**

```markdown
# skills/conversation-analyzer/SKILL.md
---
name: conversation-analyzer
description: Manually trigger conversation analysis to detect user corrections and generate instinct candidates. Usually runs automatically at session end.
---

# Conversation Analyzer

Scans the current session for correction patterns and generates instinct candidates.

## Usage

```
/man-analyze
```

## What It Does

1. Scans conversation for user corrections ("no not that", "always use X", "stop doing Y")
2. Extracts context around each correction (±3 lines)
3. Generates candidate instinct files in `.claude/instincts/candidates/`
4. Candidates require human review before promotion

## Candidate Lifecycle

```
Detected correction → candidates/ (confidence 0.5-0.6)
  → Human review → personal/ (confidence 0.7+) → Active instinct
  → Human reject → delete candidate
```

## Manual Promotion

To promote a candidate to an active instinct:
1. Read the candidate file in `.claude/instincts/candidates/`
2. Edit: write a clear Action description
3. Raise confidence to 0.7+
4. Move to `.claude/instincts/personal/`
5. Delete the candidate file

Or use `/man-instinct create` to create the instinct directly from the candidate's context.
```

- [x] **Step 5: Write tests**

```python
# tests/test_conversation_analyzer.py
import tempfile
from hooks.lib.conversation_analyzer import analyze_corrections, write_candidate, _slugify

def test_detects_negative_correction():
    transcript = "user: fix the login\nassistant: I'll mock the DB\nuser: no, don't do that, use real DB"
    results = analyze_corrections(transcript)
    assert len(results) >= 1
    assert any(r["type"] == "negative" for r in results)

def test_detects_positive_confirmation():
    transcript = "assistant: I'll use integration tests\nuser: yes, exactly, that's what I wanted"
    results = analyze_corrections(transcript)
    assert len(results) >= 1
    assert any(r["type"] == "positive" for r in results)

def test_detects_directive():
    transcript = "user: always use pnpm instead of npm in this project"
    results = analyze_corrections(transcript)
    assert len(results) >= 1
    assert any(r["type"] == "directive" for r in results)

def test_slugify():
    assert _slugify("No, don't do that!") == "no-don-t-do-that"
    assert _slugify("") == ""

def test_write_candidate():
    with tempfile.TemporaryDirectory() as d:
        candidate = {
            "type": "negative",
            "trigger_line": "no don't mock the DB",
            "context": "some context",
            "confidence": 0.5,
        }
        path = write_candidate(candidate, project_root=d)
        assert path is not None
        assert "candidates" in path
```

- [x] **Step 6: Run tests**

Run: `python -m pytest tests/test_conversation_analyzer.py -v`
Expected: All PASS

- [x] **Step 7: Commit**

```bash
git add hooks/lib/conversation_analyzer.py hooks/claude/stop.py hooks/lib/project_config.py skills/conversation-analyzer/SKILL.md tests/test_conversation_analyzer.py
git commit -m "feat(instincts): add conversation analyzer for post-session instinct generation"
```

---

### Task 2: Behavioral compliance testing skill

**Depends on:** none (but more valuable after Task 1)

**Files:**
- Create: `skills/behavioral-compliance/SKILL.md`
- Create: `tests/behavioral/README.md`

- [x] **Step 1: Create skills/behavioral-compliance/SKILL.md**

```markdown
---
name: behavioral-compliance
description: Test whether agents follow skill instructions. Runs automated sessions via `claude -p` and checks tool traces for expected behavior patterns.
---

# Behavioral Compliance Testing

Automated verification that agents follow their skill instructions. Uses `claude -p` (headless mode) to run test scenarios, then analyzes the tool trace for compliance.

## Usage

```
/man-compliance <skill-name> [--scenario <name>]
```

## How It Works

### Step 1: Define Test Scenarios

Create test scenarios in `tests/behavioral/<skill-name>/`:

```markdown
# tests/behavioral/council/test-writes-position-first.md
---
scenario: writes-position-first
skill: council
prompt: "Should we use PostgreSQL or MongoDB for our user data?"
---

## Expected Behavior
1. Agent writes its own position BEFORE spawning any subagent
2. At least 2 subagents spawned after position is written
3. Subagent prompts do NOT contain the main agent's position

## Compliance Checks
- [x] Write/Edit tool called before any Agent tool call
- [x] Agent tool called at least 2 times
- [x] Agent tool prompts do not contain phrases from the Write output
```

### Step 2: Run Scenario

```bash
claude -p "You have the council skill. Use it to answer: Should we use PostgreSQL or MongoDB for our user data?" --output-format json 2>trace.json
```

### Step 3: Analyze Tool Trace

Parse the JSON trace and check each compliance criterion:

```python
# Pseudocode for trace analysis
trace = load_trace("trace.json")
tool_calls = extract_tool_calls(trace)

# Check: Write before Agent
write_index = first_index(tool_calls, "Write")
agent_index = first_index(tool_calls, "Agent")
assert write_index < agent_index, "Position must be written before spawning agents"

# Check: Agent spawned 2+ times
agent_count = count(tool_calls, "Agent")
assert agent_count >= 2, "Must spawn at least 2 perspectives"
```

### Step 4: Report

```markdown
## Compliance Report: council/writes-position-first

| Check | Status | Evidence |
|-------|--------|----------|
| Write before Agent | ✅ PASS | Write at call #3, Agent at call #5 |
| 2+ agents spawned | ✅ PASS | 3 Agent calls found |
| No position leak | ❌ FAIL | Agent #2 prompt contains "PostgreSQL is better" |

**Overall: FAIL** — 1 compliance violation detected
```

## Creating Test Scenarios

### File Structure
```
tests/behavioral/
├── README.md
├── council/
│   ├── test-writes-position-first.md
│   └── test-no-position-leak.md
├── santa-method/
│   ├── test-two-reviewers.md
│   └── test-fresh-context-on-retry.md
└── writing-plans/
    ├── test-cold-execution.md
    └── test-no-placeholders.md
```

### Scenario Template
```markdown
---
scenario: <kebab-case-name>
skill: <skill-name>
prompt: "<the prompt to send to claude -p>"
timeout: 120
---

## Expected Behavior
[describe what SHOULD happen]

## Compliance Checks
- [x] [specific, observable check on tool trace]
- [x] [another check]
```

## Limitations

- Requires `claude` CLI with `-p` flag (piped mode)
- Each test scenario costs API tokens
- Cannot test interactive flows (AskUserQuestion)
- Tool trace format may change between Claude Code versions

## When to Use

- After modifying a skill's instructions
- Before shipping a new skill
- Periodic regression testing
- After reports of agents not following instructions
```

- [x] **Step 2: Create tests/behavioral/README.md**

```markdown
# Behavioral Compliance Tests

Automated tests that verify agents follow skill instructions.

## Running

```bash
/man-compliance <skill-name>         # Run all scenarios for a skill
/man-compliance <skill-name> --scenario <name>  # Run one scenario
```

## Adding Tests

1. Create `tests/behavioral/<skill-name>/test-<scenario>.md`
2. Define the prompt, expected behavior, and compliance checks
3. Run `/man-compliance <skill-name>` to verify

## Philosophy

Unit tests verify code correctness. Behavioral tests verify agent compliance.
A skill can have perfect code but agents may still not follow its instructions.
These tests close that gap.
```

- [x] **Step 3: Commit**

```bash
git add skills/behavioral-compliance/SKILL.md tests/behavioral/README.md
git commit -m "feat(skills): add behavioral compliance testing framework"
```

---

## Success Criteria

- [x] Conversation analyzer detects correction patterns in transcripts
- [x] Candidate instinct files are generated in `.claude/instincts/candidates/`
- [x] Candidates have clear lifecycle: candidate → review → promote/reject
- [x] Behavioral compliance skill defines test scenario format
- [x] Compliance checks can verify tool trace ordering and content
- [x] Both features are fail-safe and opt-in via `.man.json`

## Risk Assessment

- **Conversation analyzer is heuristic** — regex patterns may false-positive or miss corrections. Mitigated by candidate review step (human in the loop).
- **Transcript may not be available at Stop** — depends on what data Claude Code passes. Fall back gracefully.
- **Behavioral tests cost tokens** — each `claude -p` run is an API call. Run selectively, not as CI on every commit.
- **Tool trace format may change** — compliance checks may break on Claude Code updates. Keep checks simple and version-aware.
