"""Post-session conversation analyzer — detects user corrections and generates instinct candidates.

Runs at Stop hook. Scans the session transcript for correction patterns:
- "no, not that" / "don't" / "stop doing X" → negative instinct candidate
- "yes, exactly" / "perfect" / approved unusual approach → positive instinct candidate
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
    (r"\b(no[,\s]+not that|don'?t do that|stop doing|wrong approach|that'?s not right)\b", "negative"),
    (r"\b(yes[,\s]+exactly|perfect|that'?s right|keep doing that|exactly what I wanted)\b", "positive"),
    (r"\b(always use|never use|prefer|instead of|should have|next time)\b", "directive"),
]

CANDIDATE_DIR = ".claude/instincts/candidates"


def _extract_user_messages(transcript_path: str) -> list[str]:
    """Extract user message text from a JSONL transcript file."""
    messages: list[str] = []
    try:
        with open(transcript_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    msg = entry.get("message", entry)
                    if not isinstance(msg, dict):
                        continue
                    if msg.get("role") != "user":
                        continue
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        messages.append(content)
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                messages.append(block.get("text", ""))
                except (json.JSONDecodeError, TypeError):
                    continue
    except (OSError, IOError):
        pass
    return messages


def analyze_corrections(transcript: str) -> list[dict[str, Any]]:
    """Scan a transcript string for correction patterns. Returns candidate instincts."""
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


def analyze_transcript_file(transcript_path: str) -> list[dict[str, Any]]:
    """Analyze a JSONL transcript file. Returns candidate instincts."""
    user_messages = _extract_user_messages(transcript_path)
    full_text = "\n".join(user_messages)
    return analyze_corrections(full_text)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    return slug[:50].strip("-")


def write_candidate(candidate: dict[str, Any], project_root: str | None = None) -> str | None:
    """Write a candidate instinct file for human review. Returns file path or None."""
    root = project_root or os.getcwd()
    candidate_dir = Path(root) / CANDIDATE_DIR
    candidate_dir.mkdir(parents=True, exist_ok=True)

    slug = _slugify(candidate.get("trigger_line", "unknown")[:40])
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{slug}.md"
    filepath = candidate_dir / filename

    content = (
        f"---\n"
        f"id: {slug}\n"
        f"confidence: {candidate['confidence']}\n"
        f"type: candidate\n"
        f"source: conversation-analyzer\n"
        f"detected: {datetime.now().isoformat()}\n"
        f"---\n\n"
        f"# Candidate Instinct: {candidate['type']}\n\n"
        f"## Trigger\n{candidate['trigger_line']}\n\n"
        f"## Context\n```\n{candidate['context']}\n```\n\n"
        f"## Action\n[HUMAN REVIEW REQUIRED] — Describe the behavioral rule this correction implies.\n\n"
        f"## Status\n"
        f"- [ ] Reviewed by human\n"
        f"- [ ] Promoted to `.claude/instincts/personal/` (raise confidence to 0.7+)\n"
        f"- [ ] Rejected (delete this file)\n"
    )

    try:
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)
    except Exception:
        return None


def run_analysis(transcript: str, project_root: str | None = None) -> list[str]:
    """Analyze a transcript string and write candidate files. Returns created file paths."""
    candidates = analyze_corrections(transcript)
    paths: list[str] = []
    for c in candidates:
        path = write_candidate(c, project_root)
        if path:
            paths.append(path)
    return paths


def run_analysis_from_file(transcript_path: str, project_root: str | None = None) -> list[str]:
    """Analyze a JSONL transcript file and write candidate files. Returns created file paths."""
    candidates = analyze_transcript_file(transcript_path)
    paths: list[str] = []
    for c in candidates:
        path = write_candidate(c, project_root)
        if path:
            paths.append(path)
    return paths
