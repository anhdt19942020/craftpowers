"""Claude WorktreeCreate entry — auto-provision new worktrees."""
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

from hooks.lib.worktree_provision import provision  # noqa: E402
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    try:
        msg = provision(data, os.environ.get("CLAUDE_PROJECT_DIR"))
        if msg:
            print(json.dumps({"systemMessage": msg}))
        log_hook("worktree_provision", "ok")
    except Exception as exc:
        log_error("worktree_provision", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
