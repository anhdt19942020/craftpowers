#!/usr/bin/env python3
"""
UserPromptSubmit hook: Estimate context window usage from transcript and warn Claude.
Input: JSON via stdin (includes transcript_path). Output: systemMessage if approaching limit.
"""
import json
import os
import sys

CHARS_PER_TOKEN = 4

# Model-aware context limits.
# opus-4-7 has 1M context window; all other current models have 200k.
_model = __import__("os").environ.get("CLAUDE_MODEL", "").lower()
if "opus-4-7" in _model or "opus-4.7" in _model:
    CONTEXT_LIMIT_TOKENS = 1_000_000  # true limit, but compact early same as 200k models
    WARN_TOKENS     =  140_000  # same as 200k models — 1M is safety buffer, not fill target
    CRITICAL_TOKENS =  175_000
else:
    CONTEXT_LIMIT_TOKENS = 200_000
    WARN_TOKENS     =  140_000  # 70%
    CRITICAL_TOKENS =  175_000  # 87%

def estimate_tokens(transcript_path: str) -> int:
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

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript_path = data.get("transcript_path", "")
    tokens = estimate_tokens(transcript_path)

    if tokens < WARN_TOKENS:
        sys.exit(0)

    pct = min(99, int(tokens / CONTEXT_LIMIT_TOKENS * 100))

    if tokens >= CRITICAL_TOKENS:
        msg = (
            f"[craftpowers/context-tracker] Context ~{tokens:,} tokens (~{pct}% full). "
            f"Run /compact now to avoid losing context."
        )
    else:
        msg = (
            f"[craftpowers/context-tracker] Context ~{tokens:,} tokens (~{pct}% full). "
            f"Consider /compact soon."
        )

    print(json.dumps({"systemMessage": msg}))
    sys.exit(0)

if __name__ == "__main__":
    main()
