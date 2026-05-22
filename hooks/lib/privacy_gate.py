"""Privacy gate — blocks Read/Edit/Write/MultiEdit on sensitive files.

evaluate(tool_name, file_path) -> {"decision": "allow"|"block", "reason": str}

ALLOW_PATTERNS take precedence over SENSITIVE_PATTERNS.
Pattern matching uses fnmatch (case-insensitive on all platforms for consistency).
"""
from __future__ import annotations
import fnmatch
import os

# Tools that operate on files and should be checked
_FILE_TOOLS = {"Read", "Edit", "Write", "MultiEdit"}

SENSITIVE_PATTERNS: list[str] = [
    ".env",
    ".env.*",
    "*credentials*",
    "*secret*",
    "*secrets*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "**/id_rsa*",
    "**/id_ed25519*",
    ".git/config",
    "*token*",
    "**/.aws/*",
    "**/.gcp/*",
]

ALLOW_PATTERNS: list[str] = [
    "*.env.example",
    "*.env.template",
    "*.env.sample",
    "**/test*/**",
    "**/fixture*/**",
    "**/*mock*/**",
]


def _match(pattern: str, path: str) -> bool:
    """Case-insensitive fnmatch against both the full path and the basename."""
    path_lower = path.lower().replace("\\", "/")
    pattern_lower = pattern.lower()

    # Direct match against full path
    if fnmatch.fnmatch(path_lower, pattern_lower):
        return True
    # Match against basename only (for patterns without path separators)
    if "/" not in pattern_lower:
        return fnmatch.fnmatch(os.path.basename(path_lower), pattern_lower)
    # Handle ** glob: try matching any suffix of the path components
    # e.g. "**/id_rsa*" should match "/home/user/.ssh/id_rsa"
    if "**/" in pattern_lower:
        suffix_pattern = pattern_lower.replace("**/", "")
        parts = path_lower.split("/")
        for i in range(len(parts)):
            candidate = "/".join(parts[i:])
            if fnmatch.fnmatch(candidate, suffix_pattern):
                return True
    return False


def evaluate(tool_name: str, file_path: str) -> dict:
    """Check whether a tool call on file_path should be blocked.

    Returns {"decision": "allow"|"block", "reason": str}.
    """
    if tool_name not in _FILE_TOOLS:
        return {"decision": "allow", "reason": ""}

    if not file_path:
        return {"decision": "allow", "reason": ""}

    # Normalize separators
    normalized = file_path.replace("\\", "/")

    # Whitelist check — allow patterns take precedence
    for pattern in ALLOW_PATTERNS:
        if _match(pattern, normalized):
            return {"decision": "allow", "reason": ""}

    # Sensitive pattern check
    for pattern in SENSITIVE_PATTERNS:
        if _match(pattern, normalized):
            return {
                "decision": "block",
                "reason": (
                    f"[craftpowers/privacy-gate] Blocked access to sensitive file: {file_path} "
                    f"(matched pattern: {pattern})"
                ),
            }

    return {"decision": "allow", "reason": ""}
