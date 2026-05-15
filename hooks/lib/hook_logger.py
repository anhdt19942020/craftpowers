"""Structured logging for mankit hooks. Writes to ~/.claude/mankit-hooks.log"""
import json
import os
import sys
from datetime import datetime, timezone

_LOG_PATH = os.path.join(os.path.expanduser("~"), ".claude", "mankit-hooks.log")
_MAX_LOG_SIZE = 1_000_000  # 1MB


def log_hook(hook_name: str, status: str, detail: str = "") -> None:
    """Append a structured log line. status: 'ok', 'error', 'block'."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "hook": hook_name,
        "status": status,
    }
    if detail:
        entry["detail"] = detail[:500]  # cap detail length
    try:
        os.makedirs(os.path.dirname(_LOG_PATH), exist_ok=True)
        # Rotate by truncating if file exceeds size limit
        if os.path.exists(_LOG_PATH) and os.path.getsize(_LOG_PATH) >= _MAX_LOG_SIZE:
            with open(_LOG_PATH, "w", encoding="utf-8") as f:
                f.write("")
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # logging must never crash the hook


def log_error(hook_name: str, exc: Exception) -> None:
    """Log an exception from a hook."""
    log_hook(hook_name, "error", f"{type(exc).__name__}: {exc}")
