#!/usr/bin/env python3
"""Stop hook: Append per-session cost record to ~/.claude/metrics/costs.jsonl."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hooks.lib.cost_tracker import track  # noqa: E402


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    track(
        transcript_path=data.get("transcript_path", ""),
        session_id=data.get("session_id", ""),
        model=os.environ.get("CLAUDE_MODEL", data.get("model", "")),
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
