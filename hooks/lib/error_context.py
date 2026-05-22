"""Error capture, storage, compaction, and injection for agent self-healing.

Errors are stored in {home}/.claude/agent-errors/{workflow_id}/{role}-{timestamp}-{seq}.json
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path


def _error_dir(workflow_id: str, home: str | None = None) -> Path:
    base = Path(home or os.path.expanduser("~"))
    return base / ".claude" / "agent-errors" / workflow_id


def capture_error(
    workflow_id: str,
    role: str,
    status: str,
    output_tail: str,
    files: list[str],
    home: str | None = None,
) -> None:
    """Write error JSON for a failed agent attempt."""
    error_dir = _error_dir(workflow_id, home)
    error_dir.mkdir(parents=True, exist_ok=True)

    # Count existing files to derive attempt_number and avoid collisions
    existing = list(error_dir.glob(f"{role}-*.json"))
    attempt_number = len(existing) + 1

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    # Use microseconds + counter to avoid name collision on rapid calls
    unique = f"{int(time.time() * 1000000)}-{attempt_number}"
    filename = f"{role}-{unique}.json"

    record = {
        "workflow_id": workflow_id,
        "agent_role": role,
        "timestamp": timestamp,
        "status": status,
        "error_summary": _extract_summary(output_tail),
        "last_output_tail": output_tail,
        "files_touched": files,
        "attempt_number": attempt_number,
    }
    (error_dir / filename).write_text(json.dumps(record, indent=2), encoding="utf-8")


def _extract_summary(output_tail: str) -> str:
    """Best-effort one-line summary from output tail."""
    lines = [l.strip() for l in output_tail.splitlines() if l.strip()]
    return lines[-1][:120] if lines else "(no output)"


def get_error_history(workflow_id: str, home: str | None = None) -> list[dict]:
    """Return all error records for workflow, sorted by attempt_number."""
    error_dir = _error_dir(workflow_id, home)
    if not error_dir.exists():
        return []
    records = []
    for f in error_dir.glob("*.json"):
        try:
            records.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass
    return sorted(records, key=lambda r: r.get("attempt_number", 0))


def compact_errors(errors: list[dict], max_tokens: int = 500) -> str:
    """Compact error list into ≤max_tokens token string.

    Latest error: full detail.
    Older errors: one line each.
    Token estimate: 1 token ≈ 4 chars.
    """
    if not errors:
        return ""

    max_chars = max_tokens * 4

    latest = errors[-1]
    older = errors[:-1]

    # Build one-liners for older errors (oldest first)
    one_liners = [
        f"Attempt {e.get('attempt_number', '?')}: {e.get('agent_role', '?')} → "
        f"{e.get('status', '?')}: {e.get('error_summary', '(no summary)')}"
        for e in older
    ]

    # Build full detail for latest
    files_str = ", ".join(latest.get("files_touched", [])) or "none"
    latest_block = (
        f"**Latest failure** (attempt {latest.get('attempt_number', '?')}, "
        f"{latest.get('agent_role', '?')}):\n"
        f"Status: {latest.get('status', '?')}\n"
        f"Error: {latest.get('error_summary', '(no summary)')}\n"
        f"Output tail: {latest.get('last_output_tail', '')[:300]}\n"
        f"Files touched: {files_str}"
    )

    # Assemble: one-liners first, then latest detail
    parts = []
    if one_liners:
        parts.append("**Earlier:**\n" + "\n".join(one_liners))
    parts.append(latest_block)

    result = "\n\n".join(parts)

    # Trim if over budget (remove oldest one-liners first)
    while len(result) > max_chars and one_liners:
        one_liners.pop(0)
        if one_liners:
            earlier_block = "**Earlier:**\n" + "\n".join(one_liners)
            result = "\n\n".join([earlier_block, latest_block])
        else:
            result = latest_block

    # Last resort: truncate latest block
    if len(result) > max_chars:
        result = result[:max_chars]

    return result


def inject_error_context(workflow_id: str, home: str | None = None) -> str:
    """Return formatted markdown for session injection, or empty string if no errors."""
    errors = get_error_history(workflow_id, home=home)
    if not errors:
        return ""

    summary = compact_errors(errors)
    return (
        "⚠️ Previous agent(s) failed on this workflow. Read before starting.\n\n"
        + summary
    )


def cleanup_errors(workflow_id: str, home: str | None = None) -> None:
    """Remove all error files for a workflow (call when workflow completes)."""
    error_dir = _error_dir(workflow_id, home)
    if not error_dir.exists():
        return
    for f in error_dir.glob("*.json"):
        try:
            f.unlink()
        except Exception:
            pass
    try:
        error_dir.rmdir()
    except Exception:
        pass  # not empty — that's fine
