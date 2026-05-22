"""SubagentStop gate — validate subagent output quality."""
from __future__ import annotations
import json

try:
    from lib.workflow_state import update_agent as _update_agent
except ImportError:
    _update_agent = None


def evaluate(data: dict) -> tuple[bool, str]:
    """Return (allow_stop, reason). allow_stop=False means force subagent to continue."""
    # Extract subagent output — platform sends last_assistant_message, not output
    output = data.get("output", "") or data.get("last_assistant_message", "")
    agent_type = data.get("agent_type", "")

    # Check for trivially short output — only block if output field was actually
    # populated by the platform. If output is missing/empty (platform did not
    # set the field), allow stop to avoid infinite blocking loops.
    if isinstance(output, str) and output.strip() and len(output.strip()) < 20:
        reason = "Subagent output is too short — continue working or report BLOCKED."
        try:
            if _update_agent and agent_type:
                _update_agent(agent_type, "BLOCKED", error=reason)
        except Exception:
            pass
        # Phase 2: capture error for self-healing
        _capture_gate_error(output, agent_type, "BLOCKED")
        return False, reason

    # Check implementer agents report proper status
    if agent_type == "implementer":
        if isinstance(output, str):
            has_status = any(s in output for s in ["Status: DONE", "Status: BLOCKED", "Status: NEEDS_CONTEXT", "Status: DONE_WITH_CONCERNS"])
            if not has_status:
                return False, "Implementer must report Status: DONE|BLOCKED|NEEDS_CONTEXT|DONE_WITH_CONCERNS"

            # Phase 2: capture explicit BLOCKED/NEEDS_CONTEXT for self-healing
            for bad_status in ("BLOCKED", "NEEDS_CONTEXT"):
                if f"Status: {bad_status}" in output:
                    _capture_gate_error(output, agent_type, bad_status)
                    break

    # On clean completion, update agent status in workflow state.
    try:
        if _update_agent and agent_type:
            _update_agent(agent_type, "DONE")
    except Exception:
        pass

    return True, ""


def _capture_gate_error(output: str, agent_role: str, status: str) -> None:
    """Capture error context for self-healing. Wrapped in try/except — must never break gate."""
    try:
        from lib.error_context import capture_error

        workflow_id = "unknown"
        try:
            from lib.workflow_state import get_state
            state = get_state()
            if state and isinstance(state, dict):
                workflow_id = state.get("workflow_id", "unknown")
        except Exception:
            pass  # workflow_state not available — use fallback

        output_tail = output[-500:] if isinstance(output, str) else ""
        capture_error(
            workflow_id=workflow_id,
            role=agent_role or "unknown",
            status=status,
            output_tail=output_tail,
            files=[],
        )
    except Exception:
        pass  # error capture must not affect gate decisions
