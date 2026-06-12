# Auto-Review Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use man:subagent-driven-development (recommended) or man:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Guarantee `phap-chinh` (code-reviewer) and conditionally `tu-ma-y` (security-reviewer) run automatically after `trieu-van` finishes — using `Stop` hook in agent frontmatter, passing only `git diff` for fresh-context review.

**Architecture:** `trieu-van`'s `Stop` hook calls `hooks/lib/review_trigger.py`, which extracts `git diff HEAD~1`, runs `security_detector.py` to check for sensitive patterns, then dispatches `phap-chinh` (always) and `tu-ma-y` (if sensitive patterns found) in parallel via subprocess. Reviewers are hard-blocked from writing files via their own `PreToolUse` hook.

**Tech Stack:** Python 3, existing `hooks/lib/` module pattern (`evaluate()` convention), Claude Code agent frontmatter YAML hooks syntax.

---

## Task 1: Create `hooks/lib/security_detector.py`

Follows same pattern as `hooks/lib/security_gate.py` — pure function, regex-based, returns `(bool, reason)`.

**Files:**
- Create: `hooks/lib/security_detector.py`
- Create: `tests/hooks/test_security_detector.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/hooks/test_security_detector.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.security_detector import evaluate

def test_detects_auth_keyword():
    diff = "+    if user.authenticate(password):\n+        return token"
    found, keywords = evaluate(diff)
    assert found is True
    assert "auth" in keywords

def test_detects_sql_keyword():
    diff = "+    query = 'SELECT * FROM users WHERE id = ' + user_id"
    found, keywords = evaluate(diff)
    assert found is True
    assert "sql" in keywords or "query" in keywords

def test_ignores_removed_lines():
    diff = "-    old_auth_code = True\n+    new_code = True"
    found, keywords = evaluate(diff)
    assert found is False  # removed line (-) must not trigger

def test_clean_diff_returns_false():
    diff = "+    result = calculate_total(items)\n+    return result"
    found, keywords = evaluate(diff)
    assert found is False
    assert keywords == []

def test_detects_jwt():
    diff = "+    token = jwt.encode(payload, secret)"
    found, keywords = evaluate(diff)
    assert found is True

def test_detects_subprocess():
    diff = "+    os.system(user_input)"
    found, keywords = evaluate(diff)
    assert found is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/hooks/test_security_detector.py -v
```

Expected: `ModuleNotFoundError` or `ImportError` — `security_detector` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
# hooks/lib/security_detector.py
"""Security pattern detector for git diffs.

evaluate(diff) -> (found: bool, matched_keywords: list[str])

Scans only added lines (+ prefix) in a unified diff for security-sensitive keywords.
Used by review_trigger.py to decide whether to dispatch tu-ma-y (secure-reviewer).
"""
from __future__ import annotations
import re

SENSITIVE_KEYWORDS = [
    "auth", "password", "passwd", "token", "secret",
    "crypto", "encrypt", "decrypt", "hash", "salt",
    "sql", "query", "execute", "cursor",
    "input", "request.body", "req.body",
    "upload", "file_path", "filepath",
    "permission", "role", "admin",
    "session", "cookie", "jwt", "oauth",
    "subprocess", "os.system", "eval(",
]

_COMPILED = [re.compile(re.escape(kw), re.IGNORECASE) for kw in SENSITIVE_KEYWORDS]


def evaluate(diff: str) -> tuple[bool, list[str]]:
    """Scan added lines in diff for sensitive keywords.

    Returns (True, [matched_keywords]) if any sensitive pattern found on added lines.
    Returns (False, []) if diff is clean or has no added lines.
    """
    added_lines = [
        line[1:]  # strip leading +
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    if not added_lines:
        return False, []

    content = "\n".join(added_lines)
    matched = []
    for kw, pat in zip(SENSITIVE_KEYWORDS, _COMPILED):
        if pat.search(content):
            matched.append(kw)

    return bool(matched), matched
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/hooks/test_security_detector.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add hooks/lib/security_detector.py tests/hooks/test_security_detector.py
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat(hooks): add security_detector for diff keyword scanning"
```

---

## Task 2: Create `hooks/lib/review_trigger.py`

Called by `trieu-van`'s `Stop` hook. Extracts diff, dispatches reviewers, writes handoff files to `.claude/`.

**Files:**
- Create: `hooks/lib/review_trigger.py`
- Create: `tests/hooks/test_review_trigger.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/hooks/test_review_trigger.py
import sys, os, json, tempfile, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from unittest.mock import patch, MagicMock
from lib.review_trigger import get_diff, write_handoff, should_trigger_security

def test_get_diff_returns_string(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # init a bare git repo with one commit so diff works
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
    (tmp_path / "a.txt").write_text("hello")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)
    result = get_diff(cwd=str(tmp_path))
    assert isinstance(result, str)

def test_get_diff_empty_when_no_commits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    result = get_diff(cwd=str(tmp_path))
    assert result == ""

def test_write_handoff_creates_file(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    write_handoff(diff="+ auth code", metadata={"agent": "trieu-van"}, out_dir=str(claude_dir))
    handoff = claude_dir / "review-handoff.md"
    assert handoff.exists()
    content = handoff.read_text()
    assert "+ auth code" in content
    assert "trieu-van" in content

def test_should_trigger_security_true_for_sensitive_diff():
    diff = "+    token = jwt.encode(payload, secret)"
    assert should_trigger_security(diff) is True

def test_should_trigger_security_false_for_clean_diff():
    diff = "+    total = sum(items)"
    assert should_trigger_security(diff) is False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/hooks/test_review_trigger.py -v
```

Expected: `ImportError` — `review_trigger` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
# hooks/lib/review_trigger.py
"""Review trigger — called by trieu-van's Stop hook.

Workflow:
1. Extract git diff HEAD~1
2. Write .claude/review-handoff.md
3. Detect security patterns
4. Print dispatch instructions for the orchestrator
   (actual agent dispatch happens in the hook command, not here —
    Claude Code hooks cannot spawn Claude agents directly;
    instead we write a trigger file the orchestrator reads)
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from lib.security_detector import evaluate as detect_security


def get_diff(cwd: str | None = None) -> str:
    """Return unified diff of last commit vs its parent. Empty string if unavailable."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD"],
            capture_output=True, text=True, cwd=cwd
        )
        if result.returncode != 0:
            # Fallback: diff of staged vs HEAD (pre-commit scenario)
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                capture_output=True, text=True, cwd=cwd
            )
        return result.stdout.strip()
    except Exception:
        return ""


def write_handoff(diff: str, metadata: dict, out_dir: str) -> Path:
    """Write review handoff file. Returns path written."""
    out = Path(out_dir) / "review-handoff.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Review Handoff — {timestamp}",
        "",
        "## Metadata",
        "",
        "```json",
        json.dumps(metadata, indent=2),
        "```",
        "",
        "## Diff",
        "",
        "```diff",
        diff if diff else "(no changes detected)",
        "```",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def should_trigger_security(diff: str) -> bool:
    found, _ = detect_security(diff)
    return found


def main() -> None:
    cwd = os.getcwd()
    claude_dir = Path(cwd) / ".claude"
    claude_dir.mkdir(exist_ok=True)

    diff = get_diff(cwd=cwd)

    metadata = {
        "agent": "trieu-van",
        "timestamp": datetime.now().isoformat(),
        "security_triggered": should_trigger_security(diff),
        "diff_lines": len(diff.splitlines()) if diff else 0,
    }

    handoff_path = write_handoff(diff=diff, metadata=metadata, out_dir=str(claude_dir))

    # Write trigger file — orchestrator reads this to know what to dispatch
    trigger = {
        "dispatch_phap_chinh": True,
        "dispatch_tu_ma_y": metadata["security_triggered"],
        "handoff_file": str(handoff_path),
        "diff_preview": diff[:500] if diff else "",
    }
    trigger_path = claude_dir / "review-trigger.json"
    trigger_path.write_text(json.dumps(trigger, indent=2), encoding="utf-8")

    if not diff:
        print("[review_trigger] No diff detected — skipping review dispatch.")
        sys.exit(0)

    print(f"[review_trigger] Handoff written: {handoff_path}")
    print(f"[review_trigger] Security triggered: {metadata['security_triggered']}")
    print(f"[review_trigger] Trigger file: {trigger_path}")
    print("[review_trigger] Orchestrator should read .claude/review-trigger.json and dispatch reviewers.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/hooks/test_review_trigger.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add hooks/lib/review_trigger.py tests/hooks/test_review_trigger.py
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat(hooks): add review_trigger for post-implement review dispatch"
```

---

## Task 3: Update `agents/trieu-van.md` — add Stop hook

Adds `hooks` block to frontmatter. Does NOT change agent body or existing fields.

**Files:**
- Modify: `agents/trieu-van.md` (frontmatter only)

- [ ] **Step 1: Read current frontmatter**

```bash
head -12 agents/trieu-van.md
```

Verify current fields: `name`, `aliases`, `description`, `model`, `skills`, `permissionMode`, `maxTurns`.

- [ ] **Step 2: Add hooks block to frontmatter**

In `agents/trieu-van.md`, replace the closing `---` of the frontmatter with:

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "python hooks/security_gate.py"
  Stop:
    - matcher: ""
      hooks:
        - type: command
          command: "python hooks/lib/review_trigger.py"
---
```

Full frontmatter after edit:
```yaml
---
name: trieu-van
aliases: [implementer]
description: |
  Implements ONE task from a plan. ...
model: claude-sonnet-4-6
skills: [test-driven-development, executing-plans]
permissionMode: acceptEdits
maxTurns: 50
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "python hooks/security_gate.py"
  Stop:
    - matcher: ""
      hooks:
        - type: command
          command: "python hooks/lib/review_trigger.py"
---
```

- [ ] **Step 3: Verify YAML is valid**

```bash
python -c "import yaml; yaml.safe_load(open('agents/trieu-van.md').read().split('---')[1]); print('YAML OK')"
```

Expected: `YAML OK`

- [ ] **Step 4: Commit**

```bash
git add agents/trieu-van.md
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat(agents): add Stop hook to trieu-van for auto review trigger"
```

---

## Task 4: Update `agents/phap-chinh.md` — add tools + read-only hook

Restricts `phap-chinh` to read-only tools and hard-blocks any Write/Edit attempt.

**Files:**
- Modify: `agents/phap-chinh.md` (frontmatter only)

- [ ] **Step 1: Add `tools` and `hooks` to frontmatter**

In `agents/phap-chinh.md`, add after `maxTurns: 30`:

```yaml
tools: Read, Grep, Glob, Bash
hooks:
  PreToolUse:
    - matcher: "Write|Edit|NotebookEdit"
      hooks:
        - type: command
          command: "echo 'phap-chinh is read-only — Write/Edit blocked' >&2 && exit 2"
```

Full frontmatter after edit:
```yaml
---
name: phap-chinh
aliases: [code-reviewer]
description: |
  Use this agent when a major project step has been completed...
model: claude-sonnet-4-6
skills: [requesting-code-review]
permissionMode: plan
maxTurns: 30
tools: Read, Grep, Glob, Bash
hooks:
  PreToolUse:
    - matcher: "Write|Edit|NotebookEdit"
      hooks:
        - type: command
          command: "echo 'phap-chinh is read-only — Write/Edit blocked' >&2 && exit 2"
---
```

- [ ] **Step 2: Verify YAML is valid**

```bash
python -c "import yaml; yaml.safe_load(open('agents/phap-chinh.md').read().split('---')[1]); print('YAML OK')"
```

Expected: `YAML OK`

- [ ] **Step 3: Commit**

```bash
git add agents/phap-chinh.md
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat(agents): enforce read-only on phap-chinh via PreToolUse hook"
```

---

## Task 5: Update `agents/tu-ma-y.md` — add tools + read-only hook

Same pattern as Task 4. `tu-ma-y` is security reviewer — also read-only.

**Files:**
- Modify: `agents/tu-ma-y.md` (frontmatter only)

- [ ] **Step 1: Add `tools` and `hooks` to frontmatter**

In `agents/tu-ma-y.md`, add after `maxTurns: 30`:

```yaml
tools: Read, Grep, Glob, Bash
hooks:
  PreToolUse:
    - matcher: "Write|Edit|NotebookEdit"
      hooks:
        - type: command
          command: "echo 'tu-ma-y is read-only — Write/Edit blocked' >&2 && exit 2"
```

Full frontmatter after edit:
```yaml
---
name: tu-ma-y
aliases: [secure-reviewer]
description: |
  Use this agent to perform a security-focused code review...
model: claude-sonnet-4-6
skills: [requesting-code-review]
permissionMode: plan
maxTurns: 30
tools: Read, Grep, Glob, Bash
hooks:
  PreToolUse:
    - matcher: "Write|Edit|NotebookEdit"
      hooks:
        - type: command
          command: "echo 'tu-ma-y is read-only — Write/Edit blocked' >&2 && exit 2"
---
```

- [ ] **Step 2: Verify YAML is valid**

```bash
python -c "import yaml; yaml.safe_load(open('agents/tu-ma-y.md').read().split('---')[1]); print('YAML OK')"
```

Expected: `YAML OK`

- [ ] **Step 3: Commit**

```bash
git add agents/tu-ma-y.md
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat(agents): enforce read-only on tu-ma-y via PreToolUse hook"
```

---

## Spec Coverage Check

| Spec requirement | Task |
|-----------------|------|
| `review_trigger.py` extracts git diff | Task 2 |
| `security_detector.py` scans added lines only | Task 1 |
| Security keywords list | Task 1 |
| Write `.claude/review-handoff.md` | Task 2 |
| Write `.claude/review-trigger.json` | Task 2 |
| Skip if no diff | Task 2 (main()) |
| `trieu-van` Stop hook → review_trigger.py | Task 3 |
| `phap-chinh` tools: Read, Grep, Glob, Bash | Task 4 |
| `phap-chinh` hard-block Write/Edit | Task 4 |
| `tu-ma-y` tools: Read, Grep, Glob, Bash | Task 5 |
| `tu-ma-y` hard-block Write/Edit | Task 5 |
| Existing structure not broken | All tasks — frontmatter-only edits, new files only |
