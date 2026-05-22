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
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402
from hooks.lib.skill_telemetry import detect_invoked_skills, log_skill  # noqa: E402
from hooks.lib.simplify_gate import evaluate as simplify_evaluate  # noqa: E402


def _log_skills(data: dict) -> None:
    """Detect and log skill invocations from the user prompt. Fails silently."""
    try:
        prompt = data.get("prompt", "")
        session_id = data.get("session_id", "") or os.environ.get("CLAUDE_SESSION_ID", "")
        if not session_id or not prompt:
            return
        skills = detect_invoked_skills(prompt)
        for skill in skills:
            log_skill(skill, session_id=session_id, root=_root)
    except Exception:
        pass


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    _log_skills(data)

    # Simplify gate: warn/block large diffs before commit/ship/push/merge
    try:
        prompt = data.get("prompt", "") or ""
        gate = simplify_evaluate(prompt)
        if gate["decision"] == "block":
            log_hook("user_prompt_submit", "block", gate["reason"])
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "permissionsGranted": False}, "stopReason": gate["reason"]}))
            return 2
        if gate["decision"] == "warn":
            log_hook("user_prompt_submit", "warn", gate["reason"])
            print(json.dumps({"systemMessage": f"⚠️ [craftpowers/simplify-gate] {gate['reason']}"}))
    except Exception as exc:
        log_error("user_prompt_submit", exc)

    try:
        msg = context_warning(data.get("transcript_path", ""), os.environ.get("CLAUDE_MODEL", ""))
        if msg:
            print(json.dumps({"systemMessage": msg}))
        log_hook("user_prompt_submit", "ok")
    except Exception as exc:
        log_error("user_prompt_submit", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
