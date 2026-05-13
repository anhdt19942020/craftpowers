#!/usr/bin/env python3
"""WorktreeCreate hook: auto-provision new worktrees. Thin wrapper."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hooks.lib.worktree_provision import provision

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    msg = provision(data, os.environ.get("CLAUDE_PROJECT_DIR"))
    if msg:
        print(json.dumps({"systemMessage": msg}))
    sys.exit(0)

if __name__ == "__main__":
    main()
