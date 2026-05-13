"""SubagentStop gate — validate subagent output quality."""
from __future__ import annotations
import json


def evaluate(data: dict) -> tuple[bool, str]:
    """Return (allow_stop, reason). allow_stop=False means force subagent to continue."""
    # Extract subagent output
    output = data.get("output", "")
    agent_type = data.get("agent_type", "")

    # Check for trivially short output — only block if output field was actually
    # populated by the platform. If output is missing/empty (platform did not
    # set the field), allow stop to avoid infinite blocking loops.
    if isinstance(output, str) and output.strip() and len(output.strip()) < 20:
        return False, "Subagent output is too short — continue working or report BLOCKED."

    # Check implementer agents report proper status
    if agent_type in ("trieu-van", "implementer"):
        if isinstance(output, str):
            has_status = any(s in output for s in ["Status: DONE", "Status: BLOCKED", "Status: NEEDS_CONTEXT", "Status: DONE_WITH_CONCERNS"])
            if not has_status:
                return False, "Implementer must report Status: DONE|BLOCKED|NEEDS_CONTEXT|DONE_WITH_CONCERNS"

    return True, ""
