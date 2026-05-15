"""Claude StopFailure entry — log session errors."""
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

from hooks.lib.stop_failure import handle_failure  # noqa: E402
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    try:
        msg = handle_failure(data)
        if msg:
            print(json.dumps({"systemMessage": msg}))
        log_hook("stop_failure", "ok")
    except Exception as exc:
        log_error("stop_failure", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
