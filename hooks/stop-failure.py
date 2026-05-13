#!/usr/bin/env python3
"""StopFailure hook: log session errors. Thin wrapper."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hooks.lib.stop_failure import handle_failure

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    msg = handle_failure(data)
    if msg:
        print(json.dumps({"systemMessage": msg}))
    sys.exit(0)

if __name__ == "__main__":
    main()
