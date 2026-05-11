"""End-of-session token summary (ported from hooks/session-summary.py)."""
from __future__ import annotations
import json
import os
import subprocess

CHARS_PER_TOKEN = 4


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


def context_pct(total_tokens: int) -> int:
    return min(100, int((total_tokens / 200_000) * 100))


def build_summary(transcript_path: str | None, rtk_runner=None) -> str:
    runner = rtk_runner or _default_rtk_runner
    input_tok, output_tok = estimate_tokens(transcript_path)
    total = input_tok + output_tok
    pct = context_pct(total)
    rtk_saved = runner() or "N/A (rtk gain unavailable)"
    bar = "-" * 50
    return (
        f"\n{bar}\n"
        f"Session Summary\n"
        f"{bar}\n"
        f"Input tokens:    {format_tokens(input_tok)}\n"
        f"Output tokens:   {format_tokens(output_tok)}\n"
        f"Total tokens:    {format_tokens(total)} (~{pct}% of 200k)\n"
        f"RTK savings:     {rtk_saved}\n"
        f"{bar}\n"
    )
