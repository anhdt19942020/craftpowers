"""Loop checkpoint — tracks agentic loop state across iterations.

Checkpoint file: .claude/loop-checkpoint.json

A loop is a repeated (implement → verify → pass/fail) cycle.
Workflow state tracks PHASES. Loop checkpoint tracks ITERATIONS.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _checkpoint_file(state_dir: Optional[str]) -> Path:
    base = state_dir or os.path.join(os.getcwd(), ".claude")
    return Path(base) / "loop-checkpoint.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def start_loop(
    loop_id: str,
    task: str,
    max_iterations: int = 10,
    state_dir: Optional[str] = None,
) -> dict:
    """Initialize a new loop checkpoint. Overwrites any existing checkpoint."""
    checkpoint = {
        "loop_id": loop_id,
        "task": task,
        "started_at": _now_iso(),
        "updated_at": _now_iso(),
        "status": "running",
        "max_iterations": max_iterations,
        "current_iteration": 0,
        "iterations": [],
    }
    path = _checkpoint_file(state_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    tmp.replace(path)
    return checkpoint


def record_iteration(
    result: str,
    notes: str = "",
    state_dir: Optional[str] = None,
) -> dict:
    """Record one loop iteration result. result: 'pass' | 'fail' | 'skip'."""
    path = _checkpoint_file(state_dir)
    if not path.exists():
        raise FileNotFoundError("No active loop checkpoint. Run /man-loop-start first.")
    checkpoint = json.loads(path.read_text(encoding="utf-8"))
    checkpoint["current_iteration"] += 1
    iteration = {
        "n": checkpoint["current_iteration"],
        "timestamp": _now_iso(),
        "result": result,
        "notes": notes,
    }
    checkpoint["iterations"].append(iteration)
    checkpoint["updated_at"] = _now_iso()
    if result == "pass":
        checkpoint["status"] = "done"
    elif checkpoint["current_iteration"] >= checkpoint["max_iterations"]:
        checkpoint["status"] = "max_iterations_reached"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    tmp.replace(path)
    return checkpoint


def get_checkpoint(state_dir: Optional[str] = None) -> Optional[dict]:
    """Read current loop checkpoint. Returns None if no checkpoint exists.

    Raises ValueError if checkpoint file exists but contains invalid JSON —
    distinguishes "no checkpoint" from "corrupt checkpoint".
    """
    path = _checkpoint_file(state_dir)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Loop checkpoint at {path} is corrupt (invalid JSON): {exc}. "
            "Delete it manually or run /man-loop-start to reset."
        ) from exc


def get_status_summary(state_dir: Optional[str] = None) -> str:
    """Return <=4 lines summary. Empty string if no checkpoint."""
    cp = get_checkpoint(state_dir)
    if cp is None:
        return ""
    loop_id = cp.get("loop_id", "unknown")
    status = cp.get("status", "unknown")
    current = cp.get("current_iteration", 0)
    max_i = cp.get("max_iterations", "?")
    iterations = cp.get("iterations", [])
    passes = sum(1 for i in iterations if i.get("result") == "pass")
    fails = sum(1 for i in iterations if i.get("result") == "fail")
    task = cp.get("task", "")[:60]
    return (
        f"Loop {loop_id}: {status} | Iteration {current}/{max_i} | "
        f"Pass: {passes} Fail: {fails} | Task: {task}"
    )


def clear_checkpoint(state_dir: Optional[str] = None) -> None:
    """Delete the loop checkpoint file."""
    path = _checkpoint_file(state_dir)
    if path.exists():
        path.unlink()
