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


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    event = os.environ.get("CLAUDE_HOOK_EVENT", "")
    if event == "PreCompact":
        msg = pre_compact(data)
    elif event == "PostCompact":
        msg = post_compact(data)
    else:
        return 0

    if msg:
        print(json.dumps({"systemMessage": msg}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
