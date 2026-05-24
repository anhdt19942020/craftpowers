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
