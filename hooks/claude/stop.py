"""Claude Stop entry — emit session token summary as systemMessage JSON."""
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

from hooks.lib.session_summary import build_summary  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    summary = build_summary(
        data.get("transcript_path", ""),
        os.environ.get("CLAUDE_MODEL", ""),
    )
    print(json.dumps({"systemMessage": summary}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
