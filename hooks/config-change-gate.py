#!/usr/bin/env python3
"""ConfigChange hook: block unsafe settings mutations. Thin wrapper."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hooks.lib.config_change_gate import evaluate

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    allow, reason = evaluate(data)
    if not allow:
        print(json.dumps({"decision": "block", "reason": reason}))
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
