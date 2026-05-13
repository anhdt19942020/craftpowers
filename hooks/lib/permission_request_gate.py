"""PermissionRequest gate — auto-deny dangerous permission requests."""
from __future__ import annotations
import json
import re
import sys

DENY_PATTERNS = [
    (r'\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b', "Recursive force delete"),
    (r'\bsudo\b', "Privileged execution"),
    (r'curl\s+[^|]*\|\s*(?:sudo\s+)?(?:bash|sh)\b', "Piped remote execution"),
    (r'wget\s+[^|]*\|\s*(?:sudo\s+)?(?:bash|sh)\b', "Piped remote execution"),
    (r'\bdd\s+.*\bof=/dev/', "Raw disk write"),
    (r':(){:|:&};:', "Fork bomb"),
]

_COMPILED = [(re.compile(p, re.IGNORECASE), reason) for p, reason in DENY_PATTERNS]


def evaluate(data: dict) -> tuple[bool, str]:
    """Return (allow, reason). allow=False means deny the request."""
    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")
    if not command:
        return True, ""
    for pat, reason in _COMPILED:
        if pat.search(command):
            return False, reason
    return True, ""
