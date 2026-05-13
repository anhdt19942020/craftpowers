"""PreCompact/PostCompact hooks — preserve and log context around compaction."""
from __future__ import annotations
import json
import os
import datetime


def pre_compact(data: dict) -> str:
    """Inject reminder to preserve critical state before compaction."""
    trigger = data.get("trigger", "unknown")
    custom = data.get("custom_instructions", "")

    reminder = (
        "[craftpowers/pre-compact] Compaction triggered ({trigger}). "
        "Before compacting, ensure you have noted: "
        "(1) current plan file path, "
        "(2) completed vs remaining tasks, "
        "(3) branch and worktree path, "
        "(4) key decisions from reviews. "
        "Full protocol: man:context-management"
    ).format(trigger=trigger)

    return reminder


def post_compact(data: dict) -> str:
    """Remind to re-read plan and rebuild context after compaction."""
    reminder = (
        "[craftpowers/post-compact] Compaction complete. "
        "REQUIRED recovery steps: "
        "(1) Re-read plan file from disk (source of truth), "
        "(2) Run: git log --oneline -10, git status, "
        "(3) Re-extract remaining tasks from plan, "
        "(4) Confirm with user before resuming work. "
        "Full protocol: man:context-management"
    )
    return reminder
