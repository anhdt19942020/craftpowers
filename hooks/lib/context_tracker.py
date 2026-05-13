"""Context-window usage estimator (ported from hooks/context-tracker.py)."""
from __future__ import annotations
import json
import os

CHARS_PER_TOKEN = 4


def _limits(model: str) -> tuple[int, int, int]:
    m = (model or "").lower()
    if "opus-4-7" in m or "opus-4.7" in m:
        # 1M true window, but compact at the same thresholds as 200k models.
        return 1_000_000, 140_000, 175_000
    return 200_000, 140_000, 175_000


def estimate_tokens(transcript_path: str | None) -> int:
    if not transcript_path or not os.path.exists(transcript_path):
        return 0
    total_chars = 0
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    msg = entry.get("message", entry)
                    if not isinstance(msg, dict):
                        continue
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        total_chars += len(content)
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict):
                                total_chars += len(str(block.get("text", "")))
                                total_chars += len(str(block.get("content", "")))
                            elif isinstance(block, str):
                                total_chars += len(block)
                except Exception:
                    continue
    except Exception:
        return 0
    return total_chars // CHARS_PER_TOKEN


def context_warning(transcript_path: str | None, model: str) -> str | None:
    limit, warn, critical = _limits(model)
    tokens = estimate_tokens(transcript_path)
    if tokens < warn:
        return None
    pct = min(99, int(tokens / limit * 100))
    if tokens >= critical:
        return (f"[craftpowers/context-tracker] Context ~{tokens:,} tokens (~{pct}% full). "
                f"COMPACT NOW. Use man:context-management for the compact strategy — "
                f"what to preserve, prompt template, recovery steps.")
    return (f"[craftpowers/context-tracker] Context ~{tokens:,} tokens (~{pct}% full). "
            f"Finish current task, then compact. Use man:context-management for strategy.")
