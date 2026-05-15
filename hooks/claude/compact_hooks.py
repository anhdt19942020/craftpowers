"""Claude PreCompact/PostCompact entry — preserve context around compaction."""
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

from hooks.lib.compact_hooks import pre_compact, post_compact  # noqa: E402
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    event = os.environ.get("CLAUDE_HOOK_EVENT", "")
    if event not in ("PreCompact", "PostCompact"):
        return 0

    try:
        if event == "PreCompact":
            msg = pre_compact(data)
        else:
            msg = post_compact(data)
        if msg:
            print(json.dumps({"systemMessage": msg}))
        log_hook("compact_hooks", "ok", event)
    except Exception as exc:
        log_error("compact_hooks", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
