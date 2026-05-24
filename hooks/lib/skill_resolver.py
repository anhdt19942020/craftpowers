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

    cache_key = f"{root}:{name}"
    if cache_key in _cache:
        cached = _cache[cache_key]
        if Path(cached).exists():
            return cached
        del _cache[cache_key]

    parts = name.split(":")
    if parts and parts[0] == "man":
        parts = parts[1:]

    if not parts:
        return None

    if len(parts) == 1:
        exact = skills_dir / parts[0] / "SKILL.md"
        if exact.exists():
            _cache[cache_key] = str(exact)
            return str(exact)

    if len(parts) >= 2:
        namespaced = skills_dir / parts[0] / parts[1] / "SKILL.md"
        if namespaced.exists():
            _cache[cache_key] = str(namespaced)
            return str(namespaced)

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
            continue
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
