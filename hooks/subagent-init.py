#!/usr/bin/env python3
"""SubagentStart hook: inject context into subagents. Thin wrapper."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hooks.lib.subagent_init import evaluate

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    result = evaluate(data)
    stdout = result.get("stdout", "")
    if stdout:
        print(json.dumps(result))
    sys.exit(0)

if __name__ == "__main__":
    main()
