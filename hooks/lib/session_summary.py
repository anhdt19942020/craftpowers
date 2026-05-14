"""End-of-session token summary (ported from hooks/session-summary.py)."""
from __future__ import annotations
import json
import os
import subprocess

CHARS_PER_TOKEN = 4


def _limits(model: str) -> int:
    m = (model or "").lower()
    if "opus-4-7" in m or "opus-4.7" in m:
        return 1_000_000
    return 200_000


def estimate_tokens(transcript_path: str | None) -> tuple[int, int]:
    """Return (input_tokens, output_tokens). assistant role -> output, everything else -> input."""
    if not transcript_path or not os.path.exists(transcript_path):
        return 0, 0
    input_chars = 0
    output_chars = 0
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
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    chars = 0
                    if isinstance(content, str):
                        chars = len(content)
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict):
                                chars += len(str(block.get("text", "")))
                                chars += len(str(block.get("content", "")))
                            elif isinstance(block, str):
                                chars += len(block)
                    if role == "assistant":
                        output_chars += chars
                    else:
                        input_chars += chars
                except Exception:
                    continue
    except Exception:
        return 0, 0
    return input_chars // CHARS_PER_TOKEN, output_chars // CHARS_PER_TOKEN


def _default_rtk_runner() -> str | None:
    try:
        result = subprocess.run(["rtk", "gain"], capture_output=True, timeout=10)
        if result.returncode != 0:
            return None
        text = result.stdout.decode("utf-8", errors="replace")
        for line in text.splitlines():
            if "Tokens saved:" in line:
                return line.split(":", 1)[1].strip()
        return None
    except Exception:
        return None


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def context_pct(tokens: int, limit: int = 200_000) -> int:
    """Return context usage as integer percentage, capped at 100."""
    return min(100, round(tokens * 100 / limit))


def _safe_transcript_path(raw: str | None) -> str | None:
    """Validate transcript_path resolves under ~/.claude to prevent path traversal."""
    if not raw:
        return None
    import pathlib
    p = pathlib.Path(raw).resolve()
    allowed = pathlib.Path.home() / ".claude"
    try:
        p.relative_to(allowed)
        return str(p)
    except ValueError:
        return None


def build_summary(transcript_path: str | None, model: str = "", rtk_runner=None) -> str:
    runner = rtk_runner or _default_rtk_runner
    limit = _limits(model)
    safe_path = _safe_transcript_path(transcript_path)
    input_tok, output_tok = estimate_tokens(safe_path)
    total = input_tok + output_tok
    pct = min(100, int((total / limit) * 100))
    rtk_saved = runner() or "N/A"

    return (
        f"[craftpowers/session-summary] Session Summary\n"
        f"Input: {format_tokens(input_tok)} | "
        f"Output: {format_tokens(output_tok)} | "
        f"Total: {format_tokens(total)} (~{pct}% of {format_tokens(limit)}) | "
        f"RTK savings: {rtk_saved}"
    )
