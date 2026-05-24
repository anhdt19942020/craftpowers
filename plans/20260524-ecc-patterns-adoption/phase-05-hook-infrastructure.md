# Phase 5: Hook Infrastructure (P7, P10, T8)

**Priority:** P2 — Performance and ergonomics for the hook system
**Status:** Not started
**Effort:** 3-5 days
**Depends on:** None (parallel with other phases)

## Overview

Three infrastructure improvements: consolidate N hook processes into 1 dispatcher per event, add profile system (minimal/standard/strict) for hook sets, and create a declarative markdown-based hook authoring format (Hookify).

## Key Insights

- Current architecture spawns separate Python process per hook per event — adds latency
- Profile system solves "too many hooks for quick tasks" — switch to minimal for exploration
- Hookify is ECC's most user-friendly innovation — markdown rules instead of JSON config
- All three are internal refactors — no skill changes, no user-facing behavior change (except profiles)

---

### Task 1: Hook dispatcher consolidation (P7)

**Depends on:** none

**Files:**
- Create: `hooks/lib/dispatcher.py`
- Modify: `hooks/claude/pre_tool_use.py`
- Modify: `hooks/claude/post_tool_use.py`
- Modify: `hooks/claude/session_start.py`

- [ ] **Step 1: Create hooks/lib/dispatcher.py**

```python
"""Consolidated hook dispatcher — runs all gates for an event in a single process.

Instead of spawning N Python processes per event, this module runs all
registered evaluators in-process and returns the combined result.
"""
from __future__ import annotations

import sys
from typing import Any, Callable

EvalFn = Callable[..., dict[str, Any]]


class HookDispatcher:
    """Dispatch multiple hook evaluators for a single event."""

    def __init__(self, event_name: str):
        self.event_name = event_name
        self._gates: list[tuple[str, EvalFn, dict[str, str]]] = []

    def register(self, name: str, evaluate_fn: EvalFn, *, arg_map: dict[str, str] | None = None) -> "HookDispatcher":
        """Register an evaluator function.
        
        arg_map maps dispatcher context keys to function parameter names.
        Example: {"tool_name": "tool_name", "file_path": "file_path"}
        """
        self._gates.append((name, evaluate_fn, arg_map or {}))
        return self

    def run(self, context: dict[str, Any], *, logger: Any = None) -> dict[str, Any]:
        """Run all registered gates in order. First block wins."""
        messages: list[str] = []

        for name, fn, arg_map in self._gates:
            try:
                # Build kwargs from context using arg_map
                kwargs = {}
                for ctx_key, param_name in arg_map.items():
                    if ctx_key in context:
                        kwargs[param_name] = context[ctx_key]

                result = fn(**kwargs) if kwargs else fn()

                # Handle different result formats
                if isinstance(result, dict):
                    if result.get("decision") == "block":
                        if logger:
                            logger(self.event_name, "block", result.get("reason", name))
                        return result
                    if result.get("systemMessage"):
                        messages.append(result["systemMessage"])
                elif isinstance(result, tuple):
                    ok, reason = result
                    if not ok:
                        if logger:
                            logger(self.event_name, "block", reason)
                        return {"decision": "block", "reason": reason}
                elif isinstance(result, str) and result:
                    print(result, file=sys.stderr)
            except Exception as exc:
                if logger:
                    try:
                        from hooks.lib.hook_logger import log_error
                        log_error(self.event_name, exc)
                    except Exception:
                        pass

        result: dict[str, Any] = {"decision": "ok"}
        if messages:
            result["systemMessage"] = "\n".join(messages)
        return result
```

- [ ] **Step 2: Refactor pre_tool_use.py to use dispatcher**

```python
"""Claude PreToolUse entry — consolidated dispatcher."""
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = (
    os.environ.get("CLAUDE_PLUGIN_ROOT")
    or os.environ.get("CURSOR_PLUGIN_ROOT")
    or os.path.abspath(os.path.join(_here, "..", ".."))
)
if _root not in sys.path:
    sys.path.insert(0, _root)

from hooks.lib.dispatcher import HookDispatcher
from hooks.lib.hook_logger import log_hook, log_error
from hooks.lib.security_gate import evaluate as security_evaluate
from hooks.lib.privacy_gate import evaluate as privacy_evaluate
from hooks.lib.naming_gate import evaluate as naming_evaluate
from hooks.lib.suggest_compact import evaluate as compact_evaluate


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = data.get("tool_name", "") or ""
    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    file_path = tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""

    dispatcher = HookDispatcher("pre_tool_use")
    dispatcher.register("privacy", privacy_evaluate, arg_map={"tool_name": "tool_name", "file_path": "file_path"})
    dispatcher.register("naming", naming_evaluate, arg_map={"tool_name": "tool_name", "file_path": "file_path"})

    context = {"tool_name": tool_name, "file_path": file_path, "command": command}
    result = dispatcher.run(context, logger=log_hook)

    if result.get("decision") == "block":
        print(json.dumps(result))
        return 2

    # Security gate has different signature (returns tuple)
    try:
        ok, reason = security_evaluate(command)
        if not ok:
            log_hook("pre_tool_use", "block", reason)
            print(json.dumps({
                "decision": "block",
                "reason": f"[craftpowers/security-gate] Blocked: {reason}\nCommand: {command[:300]}",
            }))
            return 2
        log_hook("pre_tool_use", "ok")
    except Exception as exc:
        log_error("pre_tool_use", exc)

    # Compact suggestion (non-blocking)
    try:
        compact_msg = compact_evaluate()
        if compact_msg:
            print(compact_msg, file=sys.stderr)
    except Exception as exc:
        log_error("pre_tool_use", exc)

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Write tests**

```python
# tests/test_dispatcher.py
from hooks.lib.dispatcher import HookDispatcher

def test_all_pass():
    d = HookDispatcher("test")
    d.register("a", lambda: {"decision": "ok"})
    d.register("b", lambda: {"decision": "ok"})
    assert d.run({})["decision"] == "ok"

def test_first_block_wins():
    d = HookDispatcher("test")
    d.register("a", lambda: {"decision": "block", "reason": "blocked by a"})
    d.register("b", lambda: {"decision": "ok"})
    result = d.run({})
    assert result["decision"] == "block"
    assert "blocked by a" in result["reason"]

def test_arg_mapping():
    def check(tool_name: str, file_path: str):
        if file_path.endswith(".env"):
            return {"decision": "block", "reason": "sensitive file"}
        return {"decision": "ok"}

    d = HookDispatcher("test")
    d.register("privacy", check, arg_map={"tool_name": "tool_name", "file_path": "file_path"})
    
    assert d.run({"tool_name": "Read", "file_path": "config.py"})["decision"] == "ok"
    assert d.run({"tool_name": "Read", "file_path": ".env"})["decision"] == "block"

def test_exception_doesnt_crash():
    def bad_gate():
        raise ValueError("boom")

    d = HookDispatcher("test")
    d.register("bad", bad_gate)
    d.register("good", lambda: {"decision": "ok"})
    assert d.run({})["decision"] == "ok"

def test_system_messages_collected():
    d = HookDispatcher("test")
    d.register("a", lambda: {"decision": "ok", "systemMessage": "msg1"})
    d.register("b", lambda: {"decision": "ok", "systemMessage": "msg2"})
    result = d.run({})
    assert "msg1" in result.get("systemMessage", "")
    assert "msg2" in result.get("systemMessage", "")
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_dispatcher.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add hooks/lib/dispatcher.py hooks/claude/pre_tool_use.py tests/test_dispatcher.py
git commit -m "feat(hooks): add consolidated dispatcher, refactor pre_tool_use"
```

---

### Task 2: Hook profile system (P10)

**Depends on:** Task 1 (dispatcher)

**Files:**
- Create: `hooks/lib/hook_profiles.py`
- Modify: `hooks/lib/project_config.py:30-43`

- [ ] **Step 1: Create hooks/lib/hook_profiles.py**

```python
"""Hook profile system — minimal/standard/strict gate sets.

Profiles control which hooks are active. Selected via:
1. MAN_HOOK_PROFILE env var
2. .man.json "hook_profile" key
3. Default: "standard"
"""
from __future__ import annotations

import os
from typing import Any

from hooks.lib.project_config import get_config

PROFILES: dict[str, dict[str, bool]] = {
    "minimal": {
        "security_gate": True,
        "privacy_gate": True,
        "naming_gate": False,
        "simplify_gate": False,
        "write_quality": False,
        "suggest_compact": False,
        "credential_scanner": True,
        "cost_tracker": False,
    },
    "standard": {
        "security_gate": True,
        "privacy_gate": True,
        "naming_gate": True,
        "simplify_gate": True,
        "write_quality": False,
        "suggest_compact": True,
        "credential_scanner": True,
        "cost_tracker": True,
    },
    "strict": {
        "security_gate": True,
        "privacy_gate": True,
        "naming_gate": True,
        "simplify_gate": True,
        "write_quality": True,
        "suggest_compact": True,
        "credential_scanner": True,
        "cost_tracker": True,
    },
}


def get_active_profile() -> str:
    """Get the active hook profile name."""
    env_profile = os.environ.get("MAN_HOOK_PROFILE", "").lower()
    if env_profile in PROFILES:
        return env_profile

    cfg = get_config()
    cfg_profile = cfg.get("hook_profile", "standard").lower()
    if cfg_profile in PROFILES:
        return cfg_profile

    return "standard"


def is_gate_active(gate_name: str) -> bool:
    """Check if a specific gate is active under the current profile."""
    profile = get_active_profile()
    gates = PROFILES.get(profile, PROFILES["standard"])
    return gates.get(gate_name, True)


def get_profile_gates() -> dict[str, bool]:
    """Get the full gate map for the current profile."""
    profile = get_active_profile()
    return dict(PROFILES.get(profile, PROFILES["standard"]))
```

- [ ] **Step 2: Add hook_profile to _DEFAULTS in project_config.py**

```python
"hook_profile": "standard",
```

- [ ] **Step 3: Write tests**

```python
# tests/test_hook_profiles.py
from unittest.mock import patch
from hooks.lib.hook_profiles import get_active_profile, is_gate_active, PROFILES

def test_default_profile():
    with patch.dict("os.environ", {}, clear=True):
        with patch("hooks.lib.hook_profiles.get_config", return_value={}):
            assert get_active_profile() == "standard"

def test_env_overrides_config():
    with patch.dict("os.environ", {"MAN_HOOK_PROFILE": "minimal"}):
        assert get_active_profile() == "minimal"

def test_minimal_disables_naming():
    with patch("hooks.lib.hook_profiles.get_active_profile", return_value="minimal"):
        assert is_gate_active("naming_gate") is False
        assert is_gate_active("security_gate") is True

def test_strict_enables_write_quality():
    with patch("hooks.lib.hook_profiles.get_active_profile", return_value="strict"):
        assert is_gate_active("write_quality") is True

def test_all_profiles_have_security():
    for name, gates in PROFILES.items():
        assert gates["security_gate"] is True, f"{name} must have security_gate"
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_hook_profiles.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add hooks/lib/hook_profiles.py hooks/lib/project_config.py tests/test_hook_profiles.py
git commit -m "feat(hooks): add hook profile system (minimal/standard/strict)"
```

---

### Task 3: Hookify declarative abstraction (T8)

**Depends on:** Task 1 (dispatcher)

**Files:**
- Create: `hooks/lib/hookify_loader.py`
- Create: `skills/hookify/SKILL.md`

- [ ] **Step 1: Create hooks/lib/hookify_loader.py**

```python
"""Hookify — load hook rules from markdown files with YAML frontmatter.

Scans .claude/hookify.*.md files for declarative hook rules.
Each file defines one rule with event, action, and pattern.

File format:
---
event: bash
action: block
pattern: "rm -rf /"
---
Block dangerous recursive delete at root.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


def _parse_hookify_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML-like frontmatter from hookify markdown file."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)', text, re.DOTALL)
    if not match:
        return {}, text
    meta_str, body = match.group(1), match.group(2)
    meta: dict[str, str] = {}
    for line in meta_str.strip().split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body.strip()


def discover_hookify_rules(project_root: str | None = None) -> list[dict[str, Any]]:
    """Discover hookify rules from .claude/hookify.*.md files."""
    root = project_root or os.getcwd()
    rules_dir = Path(root) / ".claude"
    if not rules_dir.is_dir():
        return []

    rules: list[dict[str, Any]] = []
    for f in sorted(rules_dir.glob("hookify.*.md")):
        try:
            text = f.read_text(encoding="utf-8")
            meta, body = _parse_hookify_frontmatter(text)
            if not meta.get("event") or not meta.get("action"):
                continue
            rules.append({
                "name": f.stem.replace("hookify.", ""),
                "event": meta["event"],
                "action": meta["action"],
                "pattern": meta.get("pattern", ""),
                "description": body,
                "path": str(f),
            })
        except Exception:
            continue

    return rules


def evaluate_hookify_rules(rules: list[dict[str, Any]], event: str, content: str) -> dict[str, Any]:
    """Evaluate hookify rules against an event and content. Returns first matching block."""
    for rule in rules:
        if rule["event"] != event:
            continue
        pattern = rule.get("pattern", "")
        if not pattern:
            continue
        try:
            if re.search(pattern, content, re.IGNORECASE):
                if rule["action"] == "block":
                    return {
                        "decision": "block",
                        "reason": f"[hookify/{rule['name']}] {rule['description'][:200]}",
                    }
                elif rule["action"] == "warn":
                    return {
                        "decision": "ok",
                        "systemMessage": f"[hookify/{rule['name']}] Warning: {rule['description'][:200]}",
                    }
        except re.error:
            continue

    return {"decision": "ok"}
```

- [ ] **Step 2: Create skills/hookify/SKILL.md**

```markdown
---
name: hookify
description: Create, list, and manage declarative hook rules using markdown files. Each rule is a .claude/hookify.*.md file with YAML frontmatter.
---

# Hookify — Declarative Hook Rules

Create hook rules as simple markdown files instead of editing JSON config.

## Usage

```
/man-hookify list              # Show all active hookify rules
/man-hookify create <name>     # Create a new rule interactively
/man-hookify delete <name>     # Remove a rule
/man-hookify test <name>       # Test a rule against sample input
```

## Creating Rules

### Interactive (recommended)
Use `/man-hookify create <name>` — will ask for event, action, and pattern via AskUserQuestion.

### Manual
Create `.claude/hookify.<name>.md`:

```markdown
---
event: bash
action: block
pattern: "rm -rf /"
---
Block dangerous recursive delete at root.
```

### Fields

| Field | Required | Values |
|-------|----------|--------|
| event | Yes | `bash`, `edit`, `write`, `read` |
| action | Yes | `block`, `warn` |
| pattern | Yes | Regex pattern to match against command/content |

### Examples

**Block force push:**
```markdown
---
event: bash
action: block
pattern: "git push.*--force"
---
Prevent force pushes. Use --force-with-lease instead.
```

**Warn on TODO comments:**
```markdown
---
event: write
action: warn
pattern: "TODO|FIXME|HACK"
---
TODO/FIXME/HACK detected in written file. Consider resolving before commit.
```

**Block production database access:**
```markdown
---
event: bash
action: block
pattern: "psql.*production|prod.*psql"
---
Direct production database access blocked. Use read replica or staging.
```

## Rule Locations

Rules are discovered from:
1. `{project}/.claude/hookify.*.md` — project-scoped rules
2. `~/.claude/hookify.*.md` — global rules (future)

Project rules take precedence over global rules with the same name.
```

- [ ] **Step 3: Write tests**

```python
# tests/test_hookify.py
import os
import tempfile
from hooks.lib.hookify_loader import discover_hookify_rules, evaluate_hookify_rules, _parse_hookify_frontmatter

def test_parse_frontmatter():
    text = '---\nevent: bash\naction: block\npattern: "rm -rf"\n---\nBlock rm -rf'
    meta, body = _parse_hookify_frontmatter(text)
    assert meta["event"] == "bash"
    assert meta["action"] == "block"
    assert meta["pattern"] == "rm -rf"
    assert body == "Block rm -rf"

def test_discover_rules():
    with tempfile.TemporaryDirectory() as d:
        claude_dir = os.path.join(d, ".claude")
        os.makedirs(claude_dir)
        rule_path = os.path.join(claude_dir, "hookify.no-force-push.md")
        with open(rule_path, "w") as f:
            f.write('---\nevent: bash\naction: block\npattern: "git push.*--force"\n---\nNo force push')
        rules = discover_hookify_rules(d)
        assert len(rules) == 1
        assert rules[0]["name"] == "no-force-push"

def test_evaluate_block():
    rules = [{"name": "test", "event": "bash", "action": "block", "pattern": "rm -rf /", "description": "Blocked"}]
    result = evaluate_hookify_rules(rules, "bash", "rm -rf /home")
    assert result["decision"] == "block"

def test_evaluate_no_match():
    rules = [{"name": "test", "event": "bash", "action": "block", "pattern": "rm -rf /", "description": "Blocked"}]
    result = evaluate_hookify_rules(rules, "bash", "ls -la")
    assert result["decision"] == "ok"

def test_evaluate_wrong_event():
    rules = [{"name": "test", "event": "bash", "action": "block", "pattern": "rm -rf", "description": "Blocked"}]
    result = evaluate_hookify_rules(rules, "write", "rm -rf")
    assert result["decision"] == "ok"

def test_warn_action():
    rules = [{"name": "todo", "event": "write", "action": "warn", "pattern": "TODO", "description": "TODO found"}]
    result = evaluate_hookify_rules(rules, "write", "# TODO fix this")
    assert result["decision"] == "ok"
    assert "TODO found" in result.get("systemMessage", "")
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_hookify.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add hooks/lib/hookify_loader.py skills/hookify/SKILL.md tests/test_hookify.py
git commit -m "feat(hooks): add hookify declarative hook rules with markdown frontmatter"
```

---

## Success Criteria

- [ ] Dispatcher consolidates multiple gates into single-process evaluation
- [ ] Hook profiles switch between minimal/standard/strict via env var or .man.json
- [ ] Hookify rules discovered from `.claude/hookify.*.md` files
- [ ] Hookify supports block and warn actions with regex patterns
- [ ] All existing hook behavior preserved after dispatcher refactor
- [ ] Security gate always active regardless of profile

## Risk Assessment

- **Dispatcher refactor may break existing hooks** — mitigated by preserving exact same gate order and behavior
- **Profile system adds complexity** — mitigated by "standard" default matching current behavior
- **Hookify regex may be unsafe** — patterns run with `re.search`, no user-controlled flags. Timeout not needed for short patterns.
- **Migration path** — existing hooks.json config continues to work; hookify rules are additive, not replacing
