"""Workflow event log — append-only event stream stored in workflow-state.json.

Events are stored under the "events" key in workflow-state.json.
The list is capped at 100 entries; oldest are pruned on append.

Event types: workflow_init, agent_start, agent_done, transition, error, agent_retry, checkpoint
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_MAX_EVENTS = 100

# Events eligible to be returned by get_last_checkpoint()
_CHECKPOINT_TYPES = {"agent_done", "transition", "checkpoint"}


def _state_file(state_dir: Optional[str]) -> Path:
    import os
    base = state_dir or os.path.join(os.getcwd(), ".claude")
    return Path(base) / "workflow-state.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_state(state_dir: Optional[str]) -> Optional[dict]:
    path = _state_file(state_dir)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_state(state: dict, state_dir: Optional[str]) -> None:
    path = _state_file(state_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def append_event(
    workflow_id: str,
    event_type: str,
    data: dict,
    state_dir: Optional[str] = None,
) -> None:
    """Append one event to the events list in workflow-state.json.

    If events exceed 100 entries, the oldest are pruned (keep last 100).
    Silently does nothing if workflow-state.json does not exist.
    """
    state = _read_state(state_dir)
    if state is None:
        return
    # Only act on matching workflow
    if state.get("workflow_id") != workflow_id:
        return

    events: list = state.setdefault("events", [])
    events.append({
        "ts": _now_iso(),
        "type": event_type,
        "data": data,
    })
    if len(events) > _MAX_EVENTS:
        state["events"] = events[-_MAX_EVENTS:]

    _write_state(state, state_dir)


def get_events(
    workflow_id: str,
    last_n: Optional[int] = None,
    event_type: Optional[str] = None,
    state_dir: Optional[str] = None,
) -> list[dict]:
    """Return events for workflow_id, sorted by timestamp (oldest first).

    Args:
        last_n: If set, return only the last N events (after filtering).
        event_type: If set, filter to only events of this type.
        state_dir: Optional override for the state directory.

    Returns:
        List of event dicts, or [] if workflow not found.
    """
    state = _read_state(state_dir)
    if state is None:
        return []
    if state.get("workflow_id") != workflow_id:
        return []

    events = state.get("events", [])
    # Events are stored in insertion order (oldest first) — already sorted
    if event_type is not None:
        events = [e for e in events if e.get("type") == event_type]
    if last_n is not None:
        events = events[-last_n:]
    return events


def get_last_checkpoint(
    workflow_id: str,
    state_dir: Optional[str] = None,
) -> Optional[dict]:
    """Return the most recent checkpoint-eligible event.

    Eligible types: agent_done, transition, checkpoint.

    Returns:
        The most recent eligible event dict, or None if none exist.
    """
    events = get_events(workflow_id, state_dir=state_dir)
    for event in reversed(events):
        if event.get("type") in _CHECKPOINT_TYPES:
            return event
    return None


def summarize_events(events: list[dict], max_lines: int = 5) -> str:
    """Compact human-readable summary of events.

    Format per line: "HH:MM {event_type} → {key detail}"

    Args:
        events: List of event dicts (as returned by get_events).
        max_lines: Maximum number of lines in the summary.

    Returns:
        Multiline string, or "" if events is empty.
    """
    if not events:
        return ""

    # Use last max_lines events for summary
    subset = events[-max_lines:]
    lines = []
    for evt in subset:
        ts_str = evt.get("ts", "")
        # Extract HH:MM from ISO timestamp "2026-05-25T01:23:00Z"
        hhmm = ""
        if len(ts_str) >= 16:
            hhmm = ts_str[11:16]  # "HH:MM"

        evt_type = evt.get("type", "unknown")
        data = evt.get("data", {})

        # Build a compact detail string from data
        detail = _format_detail(evt_type, data)
        lines.append(f"{hhmm} {evt_type} → {detail}")

    return "\n".join(lines)


def _format_detail(event_type: str, data: dict) -> str:
    """Extract the key detail from event data for summary display."""
    if not data:
        return ""
    if event_type == "transition":
        frm = data.get("from", "?")
        to = data.get("to", "?")
        return f"{frm} → {to}"
    if event_type in ("agent_start", "agent_done", "agent_retry"):
        role = data.get("role", "")
        status = data.get("status", "")
        parts = [p for p in [role, status] if p]
        return " ".join(parts)
    if event_type == "error":
        return data.get("msg", data.get("message", str(data)))
    # Generic: first value as string
    first_val = next(iter(data.values()), "")
    return str(first_val)


def replay_from(
    workflow_id: str,
    checkpoint_ts: str,
    state_dir: Optional[str] = None,
) -> dict:
    """Return events from checkpoint_ts onwards (inclusive).

    Args:
        workflow_id: Workflow to query.
        checkpoint_ts: ISO timestamp string — include events with ts >= this value.
        state_dir: Optional state directory override.

    Returns:
        Dict with "events" key containing the filtered list.
    """
    events = get_events(workflow_id, state_dir=state_dir)
    subset = [e for e in events if e.get("ts", "") >= checkpoint_ts]
    return {"events": subset}
