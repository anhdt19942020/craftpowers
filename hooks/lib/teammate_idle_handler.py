"""Teammate idle handler — injects unblocked tasks when a teammate goes idle.

Callers (team coordination, future TeammateIdle hook) are responsible for
fetching the task list and passing it in via data["tasks"].  This module
never reads external APIs directly.

Usage::

    from lib.teammate_idle_handler import handle_idle

    result = handle_idle({
        "agent_id": "agent-1",
        "agent_role": "implementer",
        "team_name": "my-team",
        "tasks": [<task dicts from TaskList>],
    })
    # result["action"] in ("inject_tasks", "noop")
    # result["message"]  — injection prompt for the idle agent
    # result["tasks"]    — list of unblocked task dicts (max 3)
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Role → accepted role_tags mapping
# ---------------------------------------------------------------------------

_ROLE_TAGS: dict[str, set[str]] = {
    "implementer": {"implementer", "coding", "development"},
    "tester":      {"tester", "testing", "qa"},
    "reviewer":    {"reviewer", "review", "code-review"},
}

_NOOP: dict[str, Any] = {"action": "noop", "message": "", "tasks": []}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def handle_idle(data: dict) -> dict:
    """Return inject_tasks or noop for an idle teammate.

    Args:
        data: {
            "agent_id": str,
            "agent_role": str,
            "team_name": str,
            "tasks": list[dict],   # full task list from TaskList API
        }

    Returns:
        {
            "action": "inject_tasks" | "noop",
            "message": str,
            "tasks": list[dict],
        }
    """
    try:
        return _handle(data)
    except Exception:
        return dict(_NOOP)


# ---------------------------------------------------------------------------
# Internal logic
# ---------------------------------------------------------------------------

def _handle(data: dict) -> dict:
    tasks = data.get("tasks")
    if not tasks:
        return dict(_NOOP)

    agent_role: str = data.get("agent_role", "")
    completed_ids = {t["id"] for t in tasks if t.get("status") == "completed"}

    unblocked = [
        t for t in tasks
        if _is_unblocked(t, completed_ids) and _matches_role(t, agent_role)
    ]

    if not unblocked:
        return dict(_NOOP)

    unblocked.sort(key=lambda t: t["id"])
    selected = unblocked[:3]

    return {
        "action": "inject_tasks",
        "message": _format_message(selected),
        "tasks": selected,
    }


def _is_unblocked(task: dict, completed_ids: set) -> bool:
    """True if task is pending and all its dependencies are completed."""
    if task.get("status") != "pending":
        return False
    deps = task.get("dependencies") or []
    return all(dep_id in completed_ids for dep_id in deps)


def _matches_role(task: dict, agent_role: str) -> bool:
    """True if task has no role_tags, or if agent_role matches a task tag."""
    tags = task.get("role_tags") or []
    if not tags:
        return True
    accepted = _ROLE_TAGS.get(agent_role, {agent_role})
    return bool(set(tags) & accepted)


def _format_message(tasks: list[dict]) -> str:
    lines = ["You have unblocked tasks available:\n"]
    for i, task in enumerate(tasks, 1):
        priority = task.get("priority", "medium")
        title = task.get("title", "(untitled)")
        desc = task.get("description", "")
        lines.append(f"{i}. [Task {task['id']}] {title} (priority: {priority})")
        if desc:
            lines.append(f"   Description: {desc}")
        lines.append("")
    lines.append("Claim the lowest-ID task by setting it to in_progress and starting work.")
    return "\n".join(lines)
