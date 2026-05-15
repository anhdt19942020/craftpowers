"""Claude PreToolUse entry — security gate. Mirrors hooks/security-gate.py output."""
import json
import os
import sys

# Ensure repo root is on sys.path before importing hooks.lib
_here = os.path.dirname(os.path.abspath(__file__))
_root = (
    os.environ.get("CLAUDE_PLUGIN_ROOT")
    or os.environ.get("CURSOR_PLUGIN_ROOT")
    or os.path.abspath(os.path.join(_here, "..", ".."))
)
if _root not in sys.path:
    sys.path.insert(0, _root)

from hooks.lib.security_gate import evaluate  # noqa: E402
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    try:
        ok, reason = evaluate(command)
        if not ok:
            log_hook("pre_tool_use", "block", reason)
            print(json.dumps({
                "decision": "block",
                "reason": f"[craftpowers/security-gate] Blocked: {reason}\nCommand: {command[:300]}",
            }))
            return 2
        log_hook("pre_tool_use", "ok")
    except Exception as exc:
        log_error("pre_tool_use", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
