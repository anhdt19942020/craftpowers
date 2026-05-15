#!/usr/bin/env python3
"""ConfigChange hook (plugin harness): block unsafe settings mutations."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from hooks.lib.config_change_gate import evaluate
from hooks.lib.hook_logger import log_hook, log_error

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    try:
        allow, reason = evaluate(data)
        if not allow:
            log_hook("config_change_gate", "block", reason)
            print(json.dumps({"decision": "block", "reason": reason}))
            sys.exit(2)
        log_hook("config_change_gate", "ok")
    except Exception as exc:
        log_error("config_change_gate", exc)
    sys.exit(0)

if __name__ == "__main__":
    main()
