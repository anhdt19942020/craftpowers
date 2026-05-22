"""Claude SubagentStart entry — inject context into subagents."""
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

from hooks.lib.subagent_init import evaluate  # noqa: E402
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    try:
        result = evaluate(data)
        stdout = result.get("stdout", "")
        if stdout:
            log_hook("subagent_init", "inject", f"{len(stdout)} chars")
            print(json.dumps(result))
        else:
            log_hook("subagent_init", "ok")
    except Exception as exc:
        log_error("subagent_init", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
