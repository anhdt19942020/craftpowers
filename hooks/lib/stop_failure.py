"""StopFailure hook — log session failures (rate limit, auth, billing)."""
from __future__ import annotations
import json
import os
import datetime


def handle_failure(data: dict) -> str:
    """Return a systemMessage logging the failure."""
    error_type = data.get("error", "unknown")
    message = data.get("message", "")

    return (
        f"[craftpowers/stop-failure] Session ended with error: {error_type}. "
        f"{message} "
        f"If rate-limited, wait and retry. If auth failure, check API key."
    )
