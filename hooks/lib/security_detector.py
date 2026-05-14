"""Security pattern detector for git diffs.

evaluate(diff) -> (found: bool, matched_keywords: list[str])

Scans only added lines (+ prefix) in a unified diff for security-sensitive keywords.
Used by review_trigger.py to decide whether to dispatch tu-ma-y (secure-reviewer).
"""
from __future__ import annotations
import re

SENSITIVE_KEYWORDS = [
    "auth", "password", "passwd", "token", "secret",
    "crypto", "encrypt", "decrypt", "hash", "salt",
    "sql", "query", "execute", "cursor",
    "input", "request.body", "req.body",
    "upload", "file_path", "filepath",
    "permission", "role", "admin",
    "session", "cookie", "jwt", "oauth",
    "subprocess", "os.system", "eval(",
]

_COMPILED = [re.compile(re.escape(kw), re.IGNORECASE) for kw in SENSITIVE_KEYWORDS]


def evaluate(diff: str) -> tuple[bool, list[str]]:
    """Scan added lines in diff for sensitive keywords.

    Returns (True, [matched_keywords]) if any sensitive pattern found on added lines.
    Returns (False, []) if diff is clean or has no added lines.
    """
    added_lines = [
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    if not added_lines:
        return False, []

    content = "\n".join(added_lines)
    matched = []
    for kw, pat in zip(SENSITIVE_KEYWORDS, _COMPILED):
        if pat.search(content):
            matched.append(kw)

    return bool(matched), matched
