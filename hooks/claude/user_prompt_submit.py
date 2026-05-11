"""Claude UserPromptSubmit entry — context-window warning. Mirrors hooks/context-tracker.py."""
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

from hooks.lib.context_tracker import context_warning  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    msg = context_warning(data.get("transcript_path", ""), os.environ.get("CLAUDE_MODEL", ""))
    if msg:
        print(json.dumps({"systemMessage": msg}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
