#!/usr/bin/env python3
"""
Stop hook: Print session token summary (usage + RTK savings) when session ends.
Input: JSON via stdin (transcript_path). Output: human-readable summary to stdout.
"""
import io
import json
import os
import subprocess
import sys

# Force UTF-8 stdout on Windows (cp1252 default breaks on box-drawing chars).
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

CHARS_PER_TOKEN = 4


def estimate_tokens(transcript_path):
    """Estimate input vs output tokens from transcript file."""
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


def get_rtk_gain():
    """Run `rtk gain` and parse the 'Tokens saved' line."""
    try:
        result = subprocess.run(
            ["rtk", "gain"],
            capture_output=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        stdout_text = result.stdout.decode("utf-8", errors="replace")
        for line in stdout_text.splitlines():
            if "Tokens saved:" in line:
                return line.split(":", 1)[1].strip()
        return None
    except Exception:
        return None


def format_tokens(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def context_pct(total_tokens):
    """Estimate percent of 200k context limit used."""
    return min(100, int((total_tokens / 200_000) * 100))


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    transcript_path = data.get("transcript_path", "")
    input_tok, output_tok = estimate_tokens(transcript_path)
    total = input_tok + output_tok
    pct = context_pct(total)

    rtk_saved = get_rtk_gain() or "N/A (rtk gain unavailable)"

    bar = "-" * 50
    summary = (
        f"\n{bar}\n"
        f"Session Summary\n"
        f"{bar}\n"
        f"Input tokens:    {format_tokens(input_tok)}\n"
        f"Output tokens:   {format_tokens(output_tok)}\n"
        f"Total tokens:    {format_tokens(total)} (~{pct}% of 200k)\n"
        f"RTK savings:     {rtk_saved}\n"
        f"{bar}\n"
    )
    print(summary)


if __name__ == "__main__":
    main()
