"""Security gate — pure decision function (ported from hooks/security-gate.py).

evaluate(command) -> (allow: bool, reason: str)

`reason` is the human-readable label only (e.g. "Recursive force delete (rm -rf)").
Harness entry points are responsible for formatting/output (block JSON, exit codes).
"""
from __future__ import annotations
import re

# Copied verbatim from hooks/security-gate.py — do not edit without updating both.
DANGEROUS_PATTERNS = [
    (r'\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b', "Recursive force delete (rm -rf)"),
    (r'\brm\s+-[a-zA-Z]*f[a-zA-Z]*r\b', "Recursive force delete (rm -fr)"),
    (r'\bsudo\s+rm\b', "Privileged delete (sudo rm)"),
    (r'git\s+push\s+[^|&;]*--force(?!\s*-with-lease)', "Force push without --force-with-lease"),
    (r'git\s+push\s+[^|&;]*\s-f\b', "Force push (-f flag)"),
    (r'git\s+push\s+[^|&;]*\s-f$', "Force push (-f flag)"),
    (r'\bDROP\s+TABLE\b', "Destructive SQL: DROP TABLE"),
    (r'\bDROP\s+DATABASE\b', "Destructive SQL: DROP DATABASE"),
    (r'\bDROP\s+SCHEMA\b', "Destructive SQL: DROP SCHEMA"),
    (r'\bchmod\s+777\b', "World-writable permissions (chmod 777)"),
    (r'curl\s+[^|]*\|\s*(?:sudo\s+)?(?:bash|sh)\b', "Piped remote execution (curl | bash)"),
    (r'wget\s+[^|]*\|\s*(?:sudo\s+)?(?:bash|sh)\b', "Piped remote execution (wget | bash)"),
    (r'\bdd\s+[^|&;]*\bof=/dev/[sh]d[a-z]\b', "Raw disk overwrite (dd to block device)"),
    (r'>\s*/dev/sd[a-z]\b', "Raw disk write"),
    (r'git\s+reset\s+--hard\s+HEAD~[2-9][0-9]*', "Hard reset of 20+ commits"),
    (r'\btruncate\s+[^|&;]*--size\s+0\b', "Truncate file to zero"),
    (r':(){:|:&};:', "Fork bomb"),
]

_COMPILED = [(re.compile(p, re.IGNORECASE), reason) for p, reason in DANGEROUS_PATTERNS]


def evaluate(command: str | None) -> tuple[bool, str]:
    if not command:
        return True, ""
    for pat, reason in _COMPILED:
        if pat.search(command):
            return False, reason
    return True, ""
