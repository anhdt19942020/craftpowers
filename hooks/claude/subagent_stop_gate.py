"""Claude SubagentStop entry — validate subagent output quality."""
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = (
    os.environ.get("CLAUDE_PLUGIN_ROOT")
    or os.environ.get("CURSOR_PLUGIN_ROOT")
    or os.path.abspath(os.path.join(_here, "..", ".."))
)
if _root not in sys.path:
    sys.path.insert(0, _root)

from hooks.lib.subagent_stop_gate import evaluate  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    allow, reason = evaluate(data)
    if not allow:
        print(json.dumps({"decision": "block", "reason": reason}))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
