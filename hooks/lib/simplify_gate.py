"""Simplify gate — blocks commit/ship commands when diff is too large.

evaluate(user_message) -> {"decision": "allow"|"warn"|"block", "reason": str, "diff_lines": int}

Triggered from UserPromptSubmit when message contains commit/ship/push/merge keywords.
Fails open (allow) on git subprocess errors or timeout.
"""
from __future__ import annotations
import re
import subprocess

_DEFAULT_WARN = 500
_DEFAULT_BLOCK = 1000


def _get_thresholds() -> tuple[int, int]:
    """Load thresholds from .man.json or use defaults."""
    try:
        from hooks.lib.project_config import is_hook_enabled, get_hook_config
        if not is_hook_enabled("simplify_gate"):
            return 999999, 999999
        cfg = get_hook_config("simplify_gate")
        warn = cfg.get("warn", _DEFAULT_WARN)
        block = cfg.get("block", _DEFAULT_BLOCK)
        return int(warn), int(block)
    except Exception:
        return _DEFAULT_WARN, _DEFAULT_BLOCK

# Words that indicate a commit/ship/push/merge action
_TRIGGER_PATTERN = re.compile(
    r'\b(?:commit|ship|push|merge)\b|/man-ship',
    re.IGNORECASE,
)


def _count_diff_lines() -> int | None:
    """Run `git diff --stat HEAD` and return total changed line count.

    Returns None on timeout or other subprocess errors (fail-open).
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        output = result.stdout
        # Parse summary line: " N files changed, X insertions(+), Y deletions(-)"
        # We count insertions + deletions as "diff_lines"
        total = 0
        for m in re.finditer(r'(\d+)\s+(?:insertion|deletion)', output):
            total += int(m.group(1))
        return total
    except (subprocess.TimeoutExpired, Exception):
        return None


def evaluate(user_message: str) -> dict:
    """Evaluate whether a commit/ship action should be blocked or warned.

    Returns a dict with keys: decision, reason, diff_lines.
    """
    if not _TRIGGER_PATTERN.search(user_message or ""):
        return {"decision": "allow", "reason": "", "diff_lines": 0}

    diff_lines = _count_diff_lines()
    if diff_lines is None:
        # Fail-open: git unavailable or timed out
        return {"decision": "allow", "reason": "Git stat unavailable (fail-open)", "diff_lines": 0}

    warn_threshold, block_threshold = _get_thresholds()

    if diff_lines > block_threshold:
        return {
            "decision": "block",
            "reason": (
                f"Diff too large ({diff_lines} lines). "
                "Run simplification pass first or split into smaller commits."
            ),
            "diff_lines": diff_lines,
        }
    if diff_lines > warn_threshold:
        return {
            "decision": "warn",
            "reason": f"Large diff ({diff_lines} lines). Consider running simplification pass.",
            "diff_lines": diff_lines,
        }
    return {"decision": "allow", "reason": "", "diff_lines": diff_lines}
