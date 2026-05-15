"""Skill invocation telemetry — lightweight JSONL logger.

Appends one JSON line per skill invocation to ~/.claude/mankit-telemetry.jsonl
Tracks cumulative stats in ~/.claude/mankit-telemetry-summary.json

Detection is intentionally narrow:
- Explicit slash commands the user typed: /man-plan, /man-ship, etc.
- <command-name>...</command-name> blocks injected by slash-command expansion.

Note: Skills invoked via the Skill tool by Claude (not by user text) are NOT
captured here — this hook only sees the user prompt.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_CLAUDE_DIR = Path.home() / ".claude"
_DEFAULT_JSONL = str(_CLAUDE_DIR / "mankit-telemetry.jsonl")
_DEFAULT_SUMMARY = str(_CLAUDE_DIR / "mankit-telemetry-summary.json")

# Match /man-plan, /man-ship, /writing-plans, /brainstorming, etc.
# Use negative lookbehind to avoid matching </tag> closing tags.
_SLASH_RE = re.compile(r"(?<![<a-z])/([a-z][a-z0-9-]+)")
# Match <command-name>foo-bar</command-name>
_TAG_RE = re.compile(r"<command-name>([a-z][a-z0-9-]+)</command-name>")


def detect_invoked_skills(text: Optional[str]) -> list[str]:
    """Return skill names detected in user prompt text.

    Only matches explicit slash-command invocations and <command-name> tags.
    Never matches free-form natural language.
    """
    if not text:
        return []
    found: list[str] = []
    for m in _SLASH_RE.finditer(text):
        found.append(m.group(1))
    for m in _TAG_RE.finditer(text):
        name = m.group(1)
        if name not in found:
            found.append(name)
    return found


def estimate_skill_lines(skill_name: str, root: str = ".") -> int:
    """Return line count of the skill's SKILL.md file, or 0 if not found."""
    skill_file = Path(root) / "skills" / skill_name / "SKILL.md"
    try:
        return sum(1 for _ in skill_file.open(encoding="utf-8", errors="ignore"))
    except Exception:
        return 0


def log_skill(
    skill_name: str,
    *,
    session_id: str,
    root: str = ".",
    jsonl_path: str = _DEFAULT_JSONL,
    summary_path: str = _DEFAULT_SUMMARY,
) -> None:
    """Append one entry to the JSONL log and update the summary.

    Crash-safe: JSONL is append-only; summary is written via atomic replace.
    Fails silently if any I/O error occurs.
    """
    try:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "skill": skill_name,
            "session_id": session_id,
            "lines": estimate_skill_lines(skill_name, root=root),
        }
        _append_jsonl(jsonl_path, entry)
        _update_summary(summary_path, skill_name)
    except Exception:
        pass


def _append_jsonl(path: str, entry: dict) -> None:
    """Append one JSON line to the JSONL file. Creates the file if needed."""
    p = Path(path)
    # Don't create parent directories — only write if parent exists.
    if not p.parent.exists():
        raise OSError(f"Parent directory does not exist: {p.parent}")
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _update_summary(path: str, skill_name: str) -> None:
    """Increment per-skill count in summary file using atomic write."""
    p = Path(path)
    if not p.parent.exists():
        raise OSError(f"Parent directory does not exist: {p.parent}")

    # Read existing summary, tolerate corruption.
    summary: dict[str, int] = {}
    if p.exists():
        try:
            summary = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(summary, dict):
                summary = {}
        except Exception:
            summary = {}

    summary[skill_name] = summary.get(skill_name, 0) + 1

    # Atomic write via temp file + os.replace.
    tmp_fd, tmp_path = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, str(p))
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


def get_session_summary(session_id: str, *, jsonl_path: str = _DEFAULT_JSONL) -> dict[str, int]:
    """Return per-skill invocation counts for the given session_id.

    Reads the JSONL log and filters by session_id.
    Returns empty dict if file doesn't exist or on any error.
    """
    p = Path(jsonl_path)
    if not p.exists():
        return {}
    counts: dict[str, int] = {}
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("session_id") == session_id:
                        skill = entry.get("skill", "")
                        if skill:
                            counts[skill] = counts.get(skill, 0) + 1
                except Exception:
                    continue
    except Exception:
        return {}
    return counts


def format_session_skills_message(counts: dict[str, int], total_skills: int = 42) -> str:
    """Format a human-readable session skill usage summary.

    Returns empty string if no skills were used this session.
    """
    if not counts:
        return ""
    unique_used = len(counts)
    parts = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    skills_str = ", ".join(f"{name} ({n}x)" for name, n in parts)
    return (
        f"Skills used this session: {skills_str}. "
        f"{unique_used} of {total_skills} skills used."
    )
