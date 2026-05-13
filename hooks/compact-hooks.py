#!/usr/bin/env python3
"""PreCompact/PostCompact hook. Thin wrapper."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hooks.lib.compact_hooks import pre_compact, post_compact


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    event = os.environ.get("CLAUDE_HOOK_EVENT", "")
    if event == "PreCompact":
        msg = pre_compact(data)
    elif event == "PostCompact":
        msg = post_compact(data)
    else:
        sys.exit(0)

    if msg:
        print(json.dumps({"systemMessage": msg}))
    sys.exit(0)


if __name__ == "__main__":
    main()
