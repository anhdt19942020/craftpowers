# Phase 3: Developer Experience (T7, T9, P11)

**Priority:** P1 — Quality enforcement and plan robustness
**Status:** Complete ✅
**Effort:** 1-2 days
**Depends on:** None (parallel with Phases 1 & 2)

## Overview

Three patterns that improve the development loop: write-time quality enforcement catches issues at edit time (not commit time), blueprint cold-execution makes plans robust for fresh agents, and stack auto-detection injects project context into every session.

---

### Task 1: Write-time quality hook (Plankton pattern)

**Depends on:** none

**Files:**
- Create: `hooks/lib/write_quality.py`
- Modify: `hooks/claude/post_tool_use.py:1-51`
- Modify: `hooks/lib/project_config.py:30-43`

- [x] **Step 1: Add write_quality config to _DEFAULTS in project_config.py**

```python
_DEFAULTS: dict[str, Any] = {
    # ... existing ...
    "write_quality": {
        "enabled": False,
        "auto_format": True,
        "auto_lint": True,
        "block_config_edit": True,
    },
}
```

- [x] **Step 2: Create hooks/lib/write_quality.py**

```python
"""Write-time quality enforcement — runs formatter and linter on modified files.

PostToolUse hook on Edit/Write events. Catches issues at write time, not commit time.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from hooks.lib.project_config import get_config
from hooks.lib.project_stack import detect_stack, get_linters

# Linter config files that agents should not modify
CONFIG_FILES = {
    ".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml",
    "biome.json", "biome.jsonc",
    ".prettierrc", ".prettierrc.js", ".prettierrc.json",
    "ruff.toml", "pyproject.toml",
    ".flake8", "setup.cfg",
    ".rubocop.yml",
    "clippy.toml",
}

FORMATTER_MAP: dict[str, list[str]] = {
    "python": ["ruff", "format"],
    "typescript": ["npx", "prettier", "--write"],
    "node": ["npx", "prettier", "--write"],
    "rust": ["rustfmt"],
    "go": ["gofmt", "-w"],
}

LINTER_MAP: dict[str, list[str]] = {
    "python": ["ruff", "check", "--fix"],
    "typescript": ["npx", "eslint", "--fix"],
    "node": ["npx", "eslint", "--fix"],
    "rust": ["cargo", "clippy", "--fix", "--allow-dirty"],
}


def _is_config_file(file_path: str) -> bool:
    """Check if file is a linter/formatter config that should be protected."""
    name = Path(file_path).name
    return name in CONFIG_FILES


def _run_tool(cmd: list[str], file_path: str, timeout: int = 30) -> tuple[bool, str]:
    """Run a formatter or linter on a file. Returns (success, output)."""
    try:
        full_cmd = cmd + [file_path]
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return True, ""


def evaluate(tool_name: str, file_path: str) -> dict[str, Any]:
    """Evaluate a file write/edit for quality. Returns verdict dict."""
    result: dict[str, Any] = {"decision": "ok", "messages": []}

    cfg = get_config()
    wq_cfg = cfg.get("write_quality", {})
    if not wq_cfg.get("enabled", False):
        return result

    if not file_path:
        return result

    # Block config file edits
    if wq_cfg.get("block_config_edit", True) and _is_config_file(file_path):
        return {
            "decision": "block",
            "reason": f"[write-quality] Blocked: editing linter/formatter config '{Path(file_path).name}' is not allowed. Change code to match the config, not the other way around.",
        }

    # Detect stack for this project
    stacks = detect_stack()
    if not stacks:
        return result

    ext = Path(file_path).suffix
    stack_for_file = None
    ext_map = {".py": "python", ".ts": "typescript", ".tsx": "typescript", ".js": "node", ".jsx": "node", ".rs": "rust", ".go": "go"}
    stack_for_file = ext_map.get(ext)
    if not stack_for_file or stack_for_file not in stacks:
        return result

    messages: list[str] = []

    # Auto-format
    if wq_cfg.get("auto_format", True) and stack_for_file in FORMATTER_MAP:
        fmt_cmd = FORMATTER_MAP[stack_for_file]
        ok, output = _run_tool(fmt_cmd, file_path)
        if not ok and output:
            messages.append(f"Formatter issues: {output[:200]}")

    # Auto-lint
    if wq_cfg.get("auto_lint", True) and stack_for_file in LINTER_MAP:
        lint_cmd = LINTER_MAP[stack_for_file]
        ok, output = _run_tool(lint_cmd, file_path)
        if not ok and output:
            messages.append(f"Lint violations (unfixable): {output[:300]}")

    if messages:
        result["messages"] = messages
        result["systemMessage"] = "[write-quality] " + "; ".join(messages)

    return result
```

- [x] **Step 3: Integrate into post_tool_use.py**

Add after the credential scanner block:

```python
# Write-quality enforcement (PostToolUse on Edit/Write)
try:
    from hooks.lib.write_quality import evaluate as quality_evaluate
    tool_name = data.get("tool_name", "")
    if tool_name in ("Edit", "Write"):
        qr = quality_evaluate(tool_name, file_path)
        if qr.get("decision") == "block":
            print(json.dumps({"decision": "block", "reason": qr["reason"]}))
            return 2
        if qr.get("systemMessage"):
            print(json.dumps({"systemMessage": qr["systemMessage"]}))
except Exception as exc:
    log_error("post_tool_use", exc)
```

- [x] **Step 4: Write tests**

```python
# tests/test_write_quality.py
import os
import tempfile
from unittest.mock import patch
from hooks.lib.write_quality import evaluate, _is_config_file

def test_disabled_by_default():
    result = evaluate("Write", "test.py")
    assert result["decision"] == "ok"

def test_config_file_blocked():
    with patch("hooks.lib.write_quality.get_config", return_value={
        "write_quality": {"enabled": True, "block_config_edit": True}
    }):
        result = evaluate("Write", ".eslintrc.json")
        assert result["decision"] == "block"

def test_is_config_file():
    assert _is_config_file(".eslintrc.json") is True
    assert _is_config_file("biome.json") is True
    assert _is_config_file("app.py") is False

def test_non_code_file_skipped():
    with patch("hooks.lib.write_quality.get_config", return_value={
        "write_quality": {"enabled": True}
    }):
        result = evaluate("Write", "README.md")
        assert result["decision"] == "ok"
```

- [x] **Step 5: Run tests**

Run: `python -m pytest tests/test_write_quality.py -v`
Expected: All PASS

- [x] **Step 6: Commit**

```bash
git add hooks/lib/write_quality.py hooks/claude/post_tool_use.py hooks/lib/project_config.py tests/test_write_quality.py
git commit -m "feat(hooks): add write-time quality enforcement (plankton pattern)"
```

---

### Task 2: Blueprint cold-execution constraint for writing-plans

**Depends on:** none

**Files:**
- Modify: `skills/writing-plans/SKILL.md`

- [x] **Step 1: Add cold-execution validation section to writing-plans SKILL.md**

After the "## Self-Review" section, add a new self-review check. Insert into the existing self-review checklist:

```markdown
**7. Cold-execution test:** For each task, imagine a FRESH agent that has never seen any other task in this plan. Can it execute this task using ONLY the information in the task description? Common cold-execution failures:
- Task says "update the type we defined" without showing the type definition
- Task references a function from Task 2 without repeating its signature and file path
- Task says "similar to Task 3" instead of repeating the relevant code
- Task uses a variable name introduced in another task without declaring it
- Task says "modify the file from Task 1" without stating the file path

For each failure: copy the missing context into the task. The implementer agent starts fresh — it has ZERO memory of other tasks.
```

- [x] **Step 2: Add cold-execution note to Task Structure section**

After the existing task structure template, add:

```markdown
**Cold-Execution Rule:** Every task MUST be self-contained. A fresh agent with zero context from other tasks must be able to execute it. This means:
- Repeat type definitions, function signatures, and file paths — even if defined in an earlier task
- Never say "similar to Task N" — repeat the code
- Include the full import path for any symbol from another file
- If a task modifies a file created in a prior task, include the relevant sections of that file as context
```

- [x] **Step 3: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat(skills): add cold-execution constraint to writing-plans"
```

---

### Task 3: Stack auto-detection injection at SessionStart

**Depends on:** none

**Files:**
- Modify: `hooks/lib/session_context.py:27-76`

- [x] **Step 1: Import project_stack in session_context.py**

Add import at top:
```python
try:
    from lib.project_stack import detect_stack, format_stack_context
except ImportError:
    detect_stack = None
    format_stack_context = None
```

- [x] **Step 2: Add stack detection block to build_session_start_context()**

After the `error_ctx_block` section (around line 64), add:

```python
    stack_block = ""
    try:
        if detect_stack and format_stack_context:
            stacks = detect_stack(os.getcwd())
            if stacks:
                stack_ctx = format_stack_context(stacks)
                stack_block = f"\n\n{stack_ctx}"
    except Exception:
        pass  # stack detection must not break session context
```

Then include `{stack_block}` in the return string before `</EXTREMELY_IMPORTANT>`.

The return statement becomes:
```python
    return (
        "<EXTREMELY_IMPORTANT>\n"
        "You have man.\n\n"
        "**Below is the full content of your 'man:using-man' skill - your introduction to using "
        "skills. For all other skills, use the 'Skill' tool:**\n\n"
        f"{using_man}\n\n"
        f"{warning}"
        f"{workflow_line}"
        f"{error_ctx_block}"
        f"{stack_block}\n"
        "</EXTREMELY_IMPORTANT>"
    )
```

- [x] **Step 3: Write tests**

```python
# tests/test_stack_injection.py
from unittest.mock import patch
from hooks.lib.session_context import build_session_start_context

def test_stack_context_included(tmp_path):
    """Verify stack detection output appears in session context."""
    # Create a Python project marker
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n")
    
    with patch("lib.project_stack.detect_stack", return_value=["python"]):
        with patch("lib.project_stack.format_stack_context", return_value="[project-stack: python]"):
            ctx = build_session_start_context(str(tmp_path))
            assert "project-stack" in ctx

def test_no_stack_no_crash(tmp_path):
    """Empty dir should not crash stack detection."""
    ctx = build_session_start_context(str(tmp_path))
    assert "EXTREMELY_IMPORTANT" in ctx
```

- [x] **Step 4: Run tests**

Run: `python -m pytest tests/test_stack_injection.py -v`
Expected: All PASS

- [x] **Step 5: Commit**

```bash
git add hooks/lib/session_context.py tests/test_stack_injection.py
git commit -m "feat(hooks): inject detected project stack into SessionStart context"
```

---

## Success Criteria

- [x] Write-time quality hook runs formatter + linter on Edit/Write events when enabled
- [x] Config file protection blocks agents from editing linter configs
- [x] writing-plans skill enforces cold-execution constraint in self-review
- [x] Stack detection context appears in every SessionStart injection
- [x] All features are fail-safe — errors don't break existing functionality
- [x] `.man.json` can enable/disable write-quality and configure thresholds

## Risk Assessment

- **Write-quality adds latency to every edit** — mitigated by opt-in (`enabled: false` default) and 30s timeout
- **Formatter may not be installed** — `FileNotFoundError` is caught, silently skipped
- **Cold-execution makes plans longer** — intentional trade-off: longer plans but each task works independently
- **Stack detection may false-positive** — e.g. `pyproject.toml` exists but project is primarily TypeScript. Mitigated by detecting ALL stacks, not picking one.
