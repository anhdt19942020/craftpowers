"""Claude Stop entry — print end-of-session token summary. Mirrors hooks/session-summary.py."""
import io
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

from hooks.lib.session_summary import build_summary  # noqa: E402

try:  # Windows cp1252 stdout breaks on box-drawing chars
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    print(build_summary(data.get("transcript_path", "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
