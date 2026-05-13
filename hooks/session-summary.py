#!/usr/bin/env python3
"""
Stop hook: Emit session token summary as systemMessage JSON.
Thin wrapper over hooks/lib/session_summary.py — all logic lives there.
"""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hooks.lib.session_summary import build_summary  # noqa: E402


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    summary = build_summary(
        data.get("transcript_path", ""),
        os.environ.get("CLAUDE_MODEL", ""),
    )
    print(json.dumps({"systemMessage": summary}))
    sys.exit(0)


if __name__ == "__main__":
    main()
