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
