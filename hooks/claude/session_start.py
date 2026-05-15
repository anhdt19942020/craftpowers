"""Claude SessionStart entry — inject using-man + legacy warning. On resume, add recovery guidance."""
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

from hooks.lib.session_context import build_session_start_context  # noqa: E402
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402

_RESUME_GUIDANCE = (
    "\n\n[craftpowers/session-recovery] This is a RESUMED session. "
    "Your conversation memory may be incomplete. Before continuing work:\n"
    "1. Run: git status, git log --oneline -10, git branch\n"
    "2. Check for plan files: ls docs/mankit/plans/\n"
    "3. Re-read any plan file from disk (do NOT trust compacted memory for task specs)\n"
    "4. State what you found and confirm with user before resuming work.\n"
    "Full protocol: man:session-recovery"
)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    try:
        source = data.get("source", "")
        ctx = build_session_start_context(plugin_root=_root)

        if source == "resume":
            ctx += _RESUME_GUIDANCE

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
        log_hook("session_start", "ok")
    except Exception as exc:
        log_error("session_start", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
