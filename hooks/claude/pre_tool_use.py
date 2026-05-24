"""Claude PreToolUse entry — consolidated dispatcher."""
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

from hooks.lib.dispatcher import HookDispatcher  # noqa: E402
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402
from hooks.lib.hook_profiles import is_gate_active  # noqa: E402
from hooks.lib.security_gate import evaluate as security_evaluate  # noqa: E402
from hooks.lib.privacy_gate import evaluate as privacy_evaluate  # noqa: E402
from hooks.lib.naming_gate import evaluate as naming_evaluate  # noqa: E402
from hooks.lib.suggest_compact import evaluate as compact_evaluate  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = data.get("tool_name", "") or ""
    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    file_path = tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""

    dispatcher = HookDispatcher("pre_tool_use")
    if is_gate_active("privacy_gate"):
        dispatcher.register("privacy", privacy_evaluate, arg_map={"tool_name": "tool_name", "file_path": "file_path"})
    if is_gate_active("naming_gate"):
        dispatcher.register("naming", naming_evaluate, arg_map={"tool_name": "tool_name", "file_path": "file_path"})

    context = {"tool_name": tool_name, "file_path": file_path, "command": command}
    result = dispatcher.run(context, logger=log_hook)

    if result.get("decision") == "block":
        print(json.dumps(result))
        return 2

    # Security gate has a different signature (returns tuple) — run separately
    if is_gate_active("security_gate"):
        try:
            ok, reason = security_evaluate(command)
            if not ok:
                log_hook("pre_tool_use", "block", reason)
                print(json.dumps({
                    "decision": "block",
                    "reason": f"[craftpowers/security-gate] Blocked: {reason}\nCommand: {command[:300]}",
                }))
                return 2
            log_hook("pre_tool_use", "ok")
        except Exception as exc:
            log_error("pre_tool_use", exc)

    # Compact suggestion (non-blocking)
    if is_gate_active("suggest_compact"):
        try:
            compact_msg = compact_evaluate()
            if compact_msg:
                print(compact_msg, file=sys.stderr)
        except Exception as exc:
            log_error("pre_tool_use", exc)

    return 0


if __name__ == "__main__":
    sys.exit(main())
