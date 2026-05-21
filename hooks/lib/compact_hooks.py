"""PreCompact/PostCompact hooks — auto-snapshot state before compaction, recover after."""
from __future__ import annotations
import json
import os
import datetime
import glob
import subprocess


_SNAPSHOT_DIR = os.path.join(os.path.expanduser("~"), ".claude", "compact-snapshots")


def _run_git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git"] + list(args),
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def _find_active_plans() -> list[str]:
    cwd = os.getcwd()
    plans_dir = os.path.join(cwd, "plans")
    if not os.path.isdir(plans_dir):
        return []
    plan_files = glob.glob(os.path.join(plans_dir, "**", "plan.md"), recursive=True)
    plan_files += glob.glob(os.path.join(plans_dir, "**", "phase-*.md"), recursive=True)
    plan_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    return plan_files[:5]


def _snapshot_state(data: dict) -> dict:
    """Capture critical state to disk before compaction."""
    branch = _run_git("branch", "--show-current")
    log = _run_git("log", "--oneline", "-5")
    status = _run_git("status", "--short")
    worktree = _run_git("worktree", "list", "--porcelain")
    plans = _find_active_plans()

    snapshot = {
        "timestamp": datetime.datetime.now().isoformat(),
        "trigger": data.get("trigger", "unknown"),
        "cwd": os.getcwd(),
        "branch": branch,
        "git_log_5": log,
        "git_status": status,
        "worktrees": worktree,
        "plan_files": plans,
        "custom_instructions": data.get("custom_instructions", ""),
    }

    os.makedirs(_SNAPSHOT_DIR, exist_ok=True)
    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
    path = os.path.join(_SNAPSHOT_DIR, f"{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot


def _load_snapshot() -> dict | None:
    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
    path = os.path.join(_SNAPSHOT_DIR, f"{session_id}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _cleanup_old_snapshots(keep: int = 10) -> None:
    if not os.path.isdir(_SNAPSHOT_DIR):
        return
    files = sorted(
        glob.glob(os.path.join(_SNAPSHOT_DIR, "*.json")),
        key=lambda f: os.path.getmtime(f),
        reverse=True,
    )
    for old in files[keep:]:
        try:
            os.remove(old)
        except Exception:
            pass


def pre_compact(data: dict) -> str:
    """Auto-snapshot critical state before compaction."""
    snap = _snapshot_state(data)
    _cleanup_old_snapshots()

    plan_list = ""
    if snap["plan_files"]:
        plan_list = " Plan files: " + ", ".join(snap["plan_files"][:3]) + "."

    return (
        "[craftpowers/pre-compact] State auto-saved to disk. "
        "Trigger: {trigger}. Branch: {branch}.{plans} "
        "Before compacting, note in /compact prompt: "
        "(1) what you are doing + current task, "
        "(2) key decisions from reviews, "
        "(3) any uncommitted intent not yet in code. "
        "Full protocol: man:context-management"
    ).format(
        trigger=snap["trigger"],
        branch=snap["branch"] or "unknown",
        plans=plan_list,
    )


def post_compact(data: dict) -> str:
    """Inject recovery instructions from auto-saved snapshot."""
    snap = _load_snapshot()
    if not snap:
        return (
            "[craftpowers/post-compact] Compaction complete. No snapshot found. "
            "REQUIRED: git log --oneline -10, git status, "
            "find plan files in plans/, confirm with user. "
            "Full protocol: man:session-recovery"
        )

    recovery_parts = [
        "[craftpowers/post-compact] Compaction complete. Recovery from snapshot:"
    ]

    if snap.get("branch"):
        recovery_parts.append(f"Branch: {snap['branch']}")

    if snap.get("plan_files"):
        recovery_parts.append("Re-read these plan files (source of truth):")
        for pf in snap["plan_files"][:3]:
            recovery_parts.append(f"  - {pf}")

    if snap.get("git_status"):
        lines = snap["git_status"].split("\n")
        if len(lines) <= 5:
            recovery_parts.append(f"Uncommitted changes: {snap['git_status']}")
        else:
            recovery_parts.append(f"Uncommitted changes: {len(lines)} files modified")

    recovery_parts.append(
        "REQUIRED: (1) Re-read plan files above, "
        "(2) Run: git log --oneline -10, "
        "(3) Confirm with user before resuming. "
        "Full protocol: man:session-recovery"
    )

    return " | ".join(recovery_parts)
