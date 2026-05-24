# Phase 1: Instinct System (P5)

**Priority:** P0 — Foundation for self-improvement loop
**Status:** Complete ✅
**Effort:** 1-2 days
**Depends on:** None

## Overview

Implement a behavioral priors system: YAML/MD files with confidence scores injected into session context at SessionStart. Instincts are passive nudges learned from usage — "this project prefers integration tests" or "always grep before editing." No Mankit equivalent exists.

## Key Insights

- ECC's most novel innovation — the system literally improves itself over time
- Instincts fill the gap between rules (static, always-on) and hooks (event-driven, blocking)
- Confidence threshold (0.7) and cap (6 instincts) prevent context bloat
- Project-scoped beats global when same id exists (deduplication)
- Phase 1 is manual creation; Phase 2 (P8 Conversation Analyzer) auto-generates instincts

## Architecture

```
~/.claude/instincts/
├── personal/           # User-created, global scope
│   ├── grep-before-edit.md
│   └── prefer-functional.md
└── inherited/          # Curated/shared, global scope
    └── validate-input.md

{project}/.claude/instincts/
├── personal/           # Project-scoped
│   └── no-mock-db.md
└── inherited/          # Team-shared for this project
    └── use-pnpm.md
```

**Injection flow:**
```
SessionStart hook
  → scan 4 directories (global personal/inherited + project personal/inherited)
  → deduplicate (project wins over global for same id)
  → filter confidence >= 0.7
  → sort by confidence DESC, project-first
  → cap at 6
  → inject as "Active instincts:" block into session context
```

## Related Code Files

- Modify: `hooks/lib/session_context.py` — add instinct injection to `build_session_start_context()`
- Create: `hooks/lib/instinct_loader.py` — instinct discovery, dedup, filtering, formatting
- Create: `skills/instinct-management/SKILL.md` — `/man-instinct` skill for CRUD operations
- Modify: `hooks/lib/project_config.py` — add instinct config section to `.man.json` schema

## Implementation Steps

### Task 1: Define instinct file format and loader

**Depends on:** none

**Files:**
- Create: `hooks/lib/instinct_loader.py`

- [ ] **Step 1: Create instinct_loader.py with YAML frontmatter parser**

```python
"""Instinct loader — discovers, deduplicates, filters, and formats instincts for session injection."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

CONFIDENCE_THRESHOLD = 0.7
MAX_INJECTED = 6

def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML-like frontmatter from markdown. Returns (metadata, body)."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)', text, re.DOTALL)
    if not match:
        return {}, text
    meta_str, body = match.group(1), match.group(2)
    meta: dict[str, Any] = {}
    for line in meta_str.strip().split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            key, val = key.strip(), val.strip()
            if val.replace('.', '').isdigit():
                meta[key] = float(val) if '.' in val else int(val)
            else:
                meta[key] = val
    return meta, body.strip()


def _scan_directory(dirpath: str, scope: str) -> list[dict[str, Any]]:
    """Scan a directory for instinct .md files."""
    results = []
    p = Path(dirpath)
    if not p.is_dir():
        return results
    for f in sorted(p.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(text)
            if not meta.get("id"):
                continue
            meta["scope"] = scope
            meta["body"] = body
            meta["path"] = str(f)
            meta.setdefault("confidence", 0.5)
            results.append(meta)
        except Exception:
            continue
    return results


def discover_instincts(
    project_root: str | None = None,
    home: str | None = None,
) -> list[dict[str, Any]]:
    """Discover instincts from 4 directories, deduplicate, filter, sort, cap."""
    home = home or os.path.expanduser("~")
    cwd = project_root or os.getcwd()

    dirs = [
        (os.path.join(home, ".claude", "instincts", "personal"), "global"),
        (os.path.join(home, ".claude", "instincts", "inherited"), "global"),
        (os.path.join(cwd, ".claude", "instincts", "personal"), "project"),
        (os.path.join(cwd, ".claude", "instincts", "inherited"), "project"),
    ]

    all_instincts: list[dict[str, Any]] = []
    for dirpath, scope in dirs:
        all_instincts.extend(_scan_directory(dirpath, scope))

    # Deduplicate: project-scoped wins over global for same id
    by_id: dict[str, dict[str, Any]] = {}
    for inst in all_instincts:
        iid = inst["id"]
        if iid in by_id:
            if inst["scope"] == "project" and by_id[iid]["scope"] == "global":
                by_id[iid] = inst
        else:
            by_id[iid] = inst

    # Filter by confidence threshold
    filtered = [i for i in by_id.values() if i.get("confidence", 0) >= CONFIDENCE_THRESHOLD]

    # Sort: confidence DESC, project-first, then id for stability
    filtered.sort(key=lambda i: (-i.get("confidence", 0), 0 if i["scope"] == "project" else 1, i["id"]))

    # Cap at MAX_INJECTED
    return filtered[:MAX_INJECTED]


def format_instincts(instincts: list[dict[str, Any]]) -> str:
    """Format instincts for session context injection."""
    if not instincts:
        return ""
    lines = ["Active instincts:"]
    for inst in instincts:
        conf = int(inst.get("confidence", 0) * 100)
        scope = inst["scope"]
        iid = inst["id"]
        # Extract first meaningful line from body as summary
        body = inst.get("body", "")
        summary = ""
        for line in body.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("##"):
                summary = line
                break
        if not summary:
            summary = iid
        lines.append(f"- [{scope} {conf}%] {iid}: {summary}")
    return "\n".join(lines)
```

- [ ] **Step 2: Write tests for instinct_loader**

```python
# tests/test_instinct_loader.py
import os
import tempfile
from hooks.lib.instinct_loader import (
    _parse_frontmatter, _scan_directory, discover_instincts, format_instincts,
    CONFIDENCE_THRESHOLD, MAX_INJECTED,
)

def test_parse_frontmatter():
    text = "---\nid: test\nconfidence: 0.85\n---\nSome body text"
    meta, body = _parse_frontmatter(text)
    assert meta["id"] == "test"
    assert meta["confidence"] == 0.85
    assert body == "Some body text"

def test_parse_frontmatter_no_frontmatter():
    meta, body = _parse_frontmatter("Just plain text")
    assert meta == {}
    assert body == "Just plain text"

def test_scan_empty_dir():
    with tempfile.TemporaryDirectory() as d:
        assert _scan_directory(d, "global") == []

def test_scan_with_instinct():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "test.md")
        with open(p, "w") as f:
            f.write("---\nid: test-instinct\nconfidence: 0.9\n---\nAlways test first")
        result = _scan_directory(d, "project")
        assert len(result) == 1
        assert result[0]["id"] == "test-instinct"
        assert result[0]["confidence"] == 0.9
        assert result[0]["scope"] == "project"

def test_discover_dedup_project_wins():
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as proj:
        gp = os.path.join(home, ".claude", "instincts", "personal")
        pp = os.path.join(proj, ".claude", "instincts", "personal")
        os.makedirs(gp); os.makedirs(pp)
        with open(os.path.join(gp, "x.md"), "w") as f:
            f.write("---\nid: same\nconfidence: 0.8\n---\nGlobal version")
        with open(os.path.join(pp, "x.md"), "w") as f:
            f.write("---\nid: same\nconfidence: 0.75\n---\nProject version")
        result = discover_instincts(project_root=proj, home=home)
        assert len(result) == 1
        assert result[0]["scope"] == "project"

def test_discover_filters_low_confidence():
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as proj:
        gp = os.path.join(home, ".claude", "instincts", "personal")
        os.makedirs(gp)
        with open(os.path.join(gp, "low.md"), "w") as f:
            f.write("---\nid: low-conf\nconfidence: 0.3\n---\nLow confidence")
        result = discover_instincts(project_root=proj, home=home)
        assert len(result) == 0

def test_format_instincts():
    instincts = [
        {"id": "test", "confidence": 0.85, "scope": "project", "body": "Always test first"},
    ]
    output = format_instincts(instincts)
    assert "[project 85%]" in output
    assert "test:" in output
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_instinct_loader.py -v`
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add hooks/lib/instinct_loader.py tests/test_instinct_loader.py
git commit -m "feat(instincts): add instinct loader with discovery, dedup, and formatting"
```

---

### Task 2: Integrate instinct injection into SessionStart

**Depends on:** Task 1

**Files:**
- Modify: `hooks/lib/session_context.py:27-76`

- [ ] **Step 1: Import instinct loader in session_context.py**

Add import at top of `session_context.py`:
```python
try:
    from hooks.lib.instinct_loader import discover_instincts, format_instincts
except ImportError:
    discover_instincts = None
    format_instincts = None
```

- [ ] **Step 2: Add instinct block to build_session_start_context()**

After the `error_ctx_block` section (around line 66), add:
```python
    instinct_block = ""
    try:
        if discover_instincts and format_instincts:
            instincts = discover_instincts(project_root=os.getcwd(), home=home)
            formatted = format_instincts(instincts)
            if formatted:
                instinct_block = f"\n\n{formatted}"
    except Exception:
        pass  # instinct injection must not break session context
```

Then include `{instinct_block}` in the return string before `</EXTREMELY_IMPORTANT>`.

- [ ] **Step 3: Run existing tests + manual verify**

Run: `python -m pytest tests/ -v -k "session"`
Expected: Existing tests still pass, instinct block appears when instinct files exist

- [ ] **Step 4: Commit**

```bash
git add hooks/lib/session_context.py
git commit -m "feat(instincts): inject active instincts into session context at SessionStart"
```

---

### Task 3: Create /man-instinct management skill

**Depends on:** Task 1

**Files:**
- Create: `skills/instinct-management/SKILL.md`

- [ ] **Step 1: Write the skill SKILL.md**

The skill should support:
- `list` — show all active instincts (all 4 dirs) with confidence, scope, status
- `create <id>` — interactive create with AskUserQuestion for confidence, scope, trigger, action
- `edit <id>` — modify existing instinct
- `delete <id>` — remove instinct file
- `promote <id>` — copy project-scoped instinct to global scope
- `demote <id>` — copy global instinct to project scope

File format reference:
```markdown
---
id: prefer-integration-tests
confidence: 0.85
scope: project
trigger: "when writing test files"
---

# Prefer Integration Tests

## Action
Use real database connections in tests, never mock the DB layer.

## Evidence
- User corrected mock-based tests 3 times on 2026-05-20
```

- [ ] **Step 2: Register skill name in SKILL.md frontmatter**

```yaml
---
name: instinct-management
description: Manage behavioral instincts — create, list, edit, delete, promote, demote. Instincts are confidence-weighted behavioral priors injected into every session.
---
```

- [ ] **Step 3: Test manually**

Invoke `/man-instinct list` — should show empty or existing instincts.
Create a test instinct, verify it appears in next session's context.

- [ ] **Step 4: Commit**

```bash
git add skills/instinct-management/SKILL.md
git commit -m "feat(instincts): add /man-instinct skill for instinct CRUD management"
```

---

### Task 4: Add instinct config to .man.json schema

**Depends on:** Task 1

**Files:**
- Modify: `hooks/lib/project_config.py:30-43`

- [ ] **Step 1: Add instinct defaults to _DEFAULTS**

```python
_DEFAULTS: dict[str, Any] = {
    # ... existing ...
    "instincts": {
        "enabled": True,
        "confidence_threshold": 0.7,
        "max_injected": 6,
    },
}
```

- [ ] **Step 2: Update instinct_loader.py to read config**

```python
from hooks.lib.project_config import get_config

def discover_instincts(...) -> list[dict[str, Any]]:
    cfg = get_config()
    inst_cfg = cfg.get("instincts", {})
    if not inst_cfg.get("enabled", True):
        return []
    threshold = inst_cfg.get("confidence_threshold", CONFIDENCE_THRESHOLD)
    max_count = inst_cfg.get("max_injected", MAX_INJECTED)
    # ... use threshold and max_count instead of constants ...
```

- [ ] **Step 3: Commit**

```bash
git add hooks/lib/project_config.py hooks/lib/instinct_loader.py
git commit -m "feat(instincts): add instinct config to .man.json schema"
```

---

## Success Criteria

- [ ] Instinct files in `~/.claude/instincts/personal/` are discovered and injected at SessionStart
- [ ] Project-scoped instincts override global instincts with same id
- [ ] Confidence filtering (≥0.7) and cap (6) work correctly
- [ ] `/man-instinct list` shows all instincts across 4 directories
- [ ] `/man-instinct create` interactively creates instinct file
- [ ] Instinct injection is fail-safe — errors don't break SessionStart
- [ ] `.man.json` can disable instincts or adjust thresholds

## Risk Assessment

- **Instinct injection adds context tokens** — mitigated by cap at 6, each ~50 tokens max
- **Stale instincts** — mitigated by confidence decay in future phases (P8)
- **Frontmatter parser is simple** — doesn't handle all YAML edge cases. Sufficient for instinct files which have simple key-value metadata.
