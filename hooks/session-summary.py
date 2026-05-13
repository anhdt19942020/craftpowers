#!/usr/bin/env python3
"""
Stop hook: Emit session token summary (usage + RTK savings) as systemMessage JSON.
Input: JSON via stdin (transcript_path). Output: JSON with systemMessage.
"""
import json
import os
import subprocess
import sys

CHARS_PER_TOKEN = 4

_model = os.environ.get("CLAUDE_MODEL", "").lower()
if "opus-4-7" in _model or "opus-4.7" in _model:
    CONTEXT_LIMIT_TOKENS = 1_000_000
else:
    CONTEXT_LIMIT_TOKENS = 200_000


def estimate_tokens(transcript_path):
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


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    transcript_path = data.get("transcript_path", "")
    input_tok, output_tok = estimate_tokens(transcript_path)
    total = input_tok + output_tok
    pct = min(100, int((total / CONTEXT_LIMIT_TOKENS) * 100))
    limit_label = f"{CONTEXT_LIMIT_TOKENS // 1000}k"

    rtk_saved = get_rtk_gain() or "N/A"

    summary = (
        f"[craftpowers/session-summary] "
        f"Input: {format_tokens(input_tok)} | "
        f"Output: {format_tokens(output_tok)} | "
        f"Total: {format_tokens(total)} (~{pct}% of {limit_label}) | "
        f"RTK savings: {rtk_saved}"
    )
    print(json.dumps({"systemMessage": summary}))
    sys.exit(0)


if __name__ == "__main__":
    main()
