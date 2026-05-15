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
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402
from hooks.lib.skill_telemetry import get_session_summary, format_session_skills_message  # noqa: E402


def _skills_line(data: dict) -> str:
    """Return a skills-used line for the stop message, or empty string."""
    try:
        session_id = data.get("session_id", "") or os.environ.get("CLAUDE_SESSION_ID", "")
        if not session_id:
            return ""
        counts = get_session_summary(session_id)
        return format_session_skills_message(counts)
    except Exception:
        return ""


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    try:
        summary = build_summary(
            data.get("transcript_path", ""),
            os.environ.get("CLAUDE_MODEL", ""),
        )
        skills_line = _skills_line(data)
        if skills_line:
            summary = f"{summary}\n{skills_line}"
        print(json.dumps({"systemMessage": summary}))
        log_hook("stop", "ok")
    except Exception as exc:
        log_error("stop", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
