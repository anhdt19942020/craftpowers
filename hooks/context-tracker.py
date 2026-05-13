#!/usr/bin/env python3
"""
UserPromptSubmit hook: Warn Claude when context window is filling up.
Thin wrapper over hooks/lib/context_tracker.py — all logic lives there.
"""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hooks.lib.context_tracker import context_warning  # noqa: E402


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    msg = context_warning(data.get("transcript_path", ""), os.environ.get("CLAUDE_MODEL", ""))
    if msg:
        print(json.dumps({"systemMessage": msg}))
    sys.exit(0)


if __name__ == "__main__":
    main()
