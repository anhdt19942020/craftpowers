"""Workflow state machine — single source of truth for workflow lifecycle.

State file: .claude/workflow-state.json (relative to project root, or state_dir param).

State machine:
    init → planning → implementing → reviewing → testing → done
    Any non-terminal → blocked | failed
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Public exception
# ---------------------------------------------------------------------------

class WorkflowStateError(Exception):
    """Raised on invalid state transitions."""


# ---------------------------------------------------------------------------
# Valid transitions
# ---------------------------------------------------------------------------

_TRANSITIONS: dict[str, set[str]] = {
    "init":         {"planning", "implementing", "blocked", "failed"},
    "planning":     {"implementing", "blocked", "failed"},
    "implementing": {"reviewing", "testing", "blocked", "failed"},
    "reviewing":    {"implementing", "testing", "done", "blocked", "failed"},
    "testing":      {"done", "implementing", "blocked", "failed"},
    "blocked":      {"planning", "implementing", "reviewing", "testing", "failed"},
    "failed":       set(),
    "done":         set(),
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_DEFAULT_STATE_DIR = os.path.join(os.getcwd(), ".claude")


def _state_file(state_dir: Optional[str]) -> Path:
    base = state_dir or _DEFAULT_STATE_DIR
    return Path(base) / "workflow-state.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(state_dir: Optional[str]) -> Optional[dict]:
    path = _state_file(state_dir)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write(state: dict, state_dir: Optional[str]) -> None:
    path = _state_file(state_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write: write to temp then rename
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(path)


def _lock_acquire(path: Path):
    """Return a file lock object (platform-aware). Caller must release."""
    lock_path = path.with_suffix(".lock")
    lock_file = open(lock_path, "w")
    try:
        if sys.platform == "win32":
            import msvcrt
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file, fcntl.LOCK_EX)
    except Exception:
        lock_file.close()
        raise
    return lock_file


def _lock_release(lock_file, path: Path) -> None:
    try:
        if sys.platform == "win32":
            import msvcrt
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file, fcntl.LOCK_UN)
    finally:
        lock_file.close()
        lock_path = path.with_suffix(".lock")
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_workflow(
    workflow_id: str,
    plan_ref: str,
    state_dir: Optional[str] = None,
) -> dict:
    """Create a new workflow state file. Returns the initial state."""
    state = {
        "workflow_id": workflow_id,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "phase": "init",
        "plan_ref": plan_ref,
        "agents": [],
        "execution": {
            "current_step": 0,
            "total_steps": 0,
            "retry_count": 0,
            "blocked_reason": None,
        },
        "context": {
            "branch": None,
            "files_modified": [],
            "test_status": None,
        },
    }
    _write(state, state_dir)
    return state


def get_state(state_dir: Optional[str] = None) -> Optional[dict]:
    """Read current workflow state. Returns None if no state file exists."""
    return _read(state_dir)


def transition(new_phase: str, state_dir: Optional[str] = None, **ctx) -> dict:
    """Transition to new_phase. Raises WorkflowStateError on invalid transition."""
    path = _state_file(state_dir)
    lock = None
    try:
        lock = _lock_acquire(path)
        state = _read(state_dir)
        if state is None:
            raise WorkflowStateError("No active workflow state found")
        current = state["phase"]
        allowed = _TRANSITIONS.get(current, set())
        if new_phase not in allowed:
            raise WorkflowStateError(
                f"Invalid transition: {current!r} → {new_phase!r}. "
                f"Allowed: {sorted(allowed) or 'none (terminal)'}"
            )
        state["phase"] = new_phase
        state["updated_at"] = _now_iso()
        if ctx:
            state.setdefault("context", {}).update(ctx)
        _write(state, state_dir)
        return state
    finally:
        if lock is not None:
            _lock_release(lock, path)


def register_agent(
    role: str,
    task: str,
    state_dir: Optional[str] = None,
) -> dict:
    """Add an agent entry with status 'in_progress'. Returns updated state."""
    path = _state_file(state_dir)
    lock = None
    try:
        lock = _lock_acquire(path)
        state = _read(state_dir)
        if state is None:
            raise WorkflowStateError("No active workflow state found")
        agent = {
            "role": role,
            "task": task,
            "status": "in_progress",
            "started_at": _now_iso(),
            "finished_at": None,
            "error": None,
        }
        agents = state.setdefault("agents", [])
        agents.append(agent)
        # Cap history at 20 entries
        if len(agents) > 20:
            state["agents"] = agents[-20:]
        state["updated_at"] = _now_iso()
        _write(state, state_dir)
        return state
    finally:
        if lock is not None:
            _lock_release(lock, path)


def update_agent(
    role: str,
    status: str,
    error: Optional[str] = None,
    state_dir: Optional[str] = None,
) -> dict:
    """Update the most recent agent entry matching role. Returns updated state."""
    path = _state_file(state_dir)
    lock = None
    try:
        lock = _lock_acquire(path)
        state = _read(state_dir)
        if state is None:
            raise WorkflowStateError("No active workflow state found")
        agents = state.get("agents", [])
        # Update last agent matching role
        for agent in reversed(agents):
            if agent["role"] == role:
                agent["status"] = status
                agent["finished_at"] = _now_iso()
                agent["error"] = error
                break
        state["updated_at"] = _now_iso()
        _write(state, state_dir)
        return state
    finally:
        if lock is not None:
            _lock_release(lock, path)


def get_summary(state_dir: Optional[str] = None) -> str:
    """Return ≤3 lines summary for context injection. Empty string if no state."""
    state = _read(state_dir)
    if state is None:
        return ""
    wf_id = state.get("workflow_id", "unknown")
    phase = state.get("phase", "unknown")
    execution = state.get("execution", {})
    step = execution.get("current_step", 0)
    total = execution.get("total_steps", 0)
    agents = state.get("agents", [])
    last_agent_part = ""
    if agents:
        last = agents[-1]
        last_agent_part = f" | Last agent: {last['role']} → {last['status']}"
    step_part = f"Step {step}/{total}" if total else f"Step {step}"
    return f"Workflow {wf_id}: {phase} | {step_part}{last_agent_part}"
