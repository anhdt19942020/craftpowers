#!/usr/bin/env python3
"""Sync skill/agent/command counts in README.md from actual filesystem state.

Run after adding or removing skills/agents/commands, or as part of release prep.
Usage: python scripts/sync-readme-counts.py [--check]
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def count_dirs(path: Path) -> int:
    return sum(1 for p in path.iterdir() if p.is_dir() and not p.name.startswith("."))


def count_md_files(path: Path) -> int:
    return sum(1 for p in path.glob("*.md"))


def main() -> None:
    check_only = "--check" in sys.argv

    skills = count_dirs(ROOT / "skills")
    agents = count_md_files(ROOT / "agents")
    commands = count_md_files(ROOT / "commands")

    readme = ROOT / "README.md"
    content = readme.read_text(encoding="utf-8")

    replacements = [
        (r"### \d+ Skills\b", f"### {skills} Skills"),
        (r"### \d+ Agents\b", f"### {agents} Agents"),
    ]

    updated = content
    changed: list[str] = []
    for pattern, replacement in replacements:
        new = re.sub(pattern, replacement, updated)
        if new != updated:
            m = re.search(pattern, updated)
            if m:
                changed.append(f"  {m.group()} -> {replacement}")
        updated = new

    print(f"Skills: {skills}  Agents: {agents}  Commands: {commands}")

    if not changed:
        print("README counts already up to date.")
        return

    if check_only:
        print("README counts are STALE:")
        for c in changed:
            print(c)
        sys.exit(1)

    readme.write_text(updated, encoding="utf-8")
    print("Updated README.md:")
    for c in changed:
        print(c)


if __name__ == "__main__":
    main()
