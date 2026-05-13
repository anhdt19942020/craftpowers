"""ConfigChange gate — blocks unsafe settings mutations mid-session."""
from __future__ import annotations
import json
import sys

BLOCKED_PERMISSION_PATTERNS = [
    "Bash(*)",
    "Write(*)",
    "Edit(*)",
    "PowerShell(*)",
]


def evaluate(data: dict) -> tuple[bool, str]:
    """Return (allow, reason). allow=False means block the change."""
    changes = data.get("changes", {})

    # Check if new permissions include overly broad rules
    new_allow = changes.get("permissions", {}).get("allow", [])
    for rule in new_allow:
        for blocked in BLOCKED_PERMISSION_PATTERNS:
            if rule == blocked:
                return False, f"Blocked overly permissive rule: {rule}"

    # Check if hooks are being removed/disabled
    hooks_removed = changes.get("hooks_removed", [])
    if hooks_removed:
        for hook in hooks_removed:
            if "security-gate" in str(hook) or "credential-scanner" in str(hook):
                return False, f"Blocked removal of security hook: {hook}"

    return True, ""
