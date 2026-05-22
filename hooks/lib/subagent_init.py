"""SubagentStart context injection — auto-inject plan path, workflow ID, and project context into subagents."""
from __future__ import annotations

import json
import os
from pathlib import Path


def evaluate(data: dict) -> dict:
    """Return context to inject into subagent prompt. Always succeeds (fail-open)."""
    agent_type = data.get("agent_type", "")
    project_root = (
        os.environ.get("CLAUDE_PLUGIN_ROOT")
        or os.environ.get("CURSOR_PLUGIN_ROOT")
        or os.getcwd()
    )

    context_parts: list[str] = []

    plans_dir = os.path.join(project_root, "plans")
    if os.path.isdir(plans_dir):
        context_parts.append(f"Plans path: {plans_dir}")
        reports_dir = os.path.join(plans_dir, "reports")
        if os.path.isdir(reports_dir):
            context_parts.append(f"Reports path: {reports_dir}")

    try:
        from lib.workflow_state import get_state
        state = get_state()
        if state and isinstance(state, dict):
            wf_id = state.get("workflow_id", "")
            wf_phase = state.get("phase", "")
            if wf_id:
                context_parts.append(f"Workflow ID: {wf_id}")
            if wf_phase:
                context_parts.append(f"Workflow phase: {wf_phase}")
    except Exception:
        pass

    try:
        from lib.error_context import inject_error_context
        if "workflow_id" in dir():
            pass
        state = None
        try:
            from lib.workflow_state import get_state as _gs
            state = _gs()
        except Exception:
            pass
        if state and isinstance(state, dict):
            wf_id = state.get("workflow_id", "")
            if wf_id:
                error_ctx = inject_error_context(wf_id)
                if error_ctx:
                    context_parts.append(f"Prior errors:\n{error_ctx}")
    except Exception:
        pass

    agents_md = os.path.join(project_root, "AGENTS.md")
    if os.path.isfile(agents_md):
        context_parts.append(f"Agent conventions: {agents_md}")

    claude_md = os.path.join(project_root, "CLAUDE.md")
    if os.path.isfile(claude_md):
        context_parts.append(f"Project guidelines: {claude_md}")

    team_name = data.get("team_name", "")
    if team_name:
        context_parts.append(f"Team: {team_name}")
        team_dir = os.path.join(project_root, ".team", team_name)
        if os.path.isdir(team_dir):
            context_parts.append(f"Team artifacts: {team_dir}")

    if not context_parts:
        return {"decision": "approve"}

    injection = "\n".join([
        "<subagent-context>",
        f"Work context: {project_root}",
        *context_parts,
        "</subagent-context>",
    ])

    return {
        "decision": "approve",
        "suppressOutput": True,
        "stdout": injection,
    }
