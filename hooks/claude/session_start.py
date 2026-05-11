"""Claude SessionStart entry — inject using-man + legacy warning. Mirrors the bash hooks/session-start."""
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

from hooks.lib.session_context import build_session_start_context  # noqa: E402


def main() -> int:
    # stdin payload is unused; consume it so the pipe doesn't block.
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    ctx = build_session_start_context(plugin_root=_root)
    cursor = os.environ.get("CURSOR_PLUGIN_ROOT", "")
    claude = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    copilot = os.environ.get("COPILOT_CLI", "")
    if cursor:
        out = {"additional_context": ctx}
    elif claude and not copilot:
        out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}
    else:
        out = {"additionalContext": ctx}
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
