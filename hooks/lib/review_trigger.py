"""Review trigger — called by trieu-van's Stop hook.

Workflow:
1. Extract git diff HEAD~1
2. Write .claude/review-handoff.md
3. Detect security patterns
4. Write .claude/review-trigger.json for orchestrator to read
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from lib.security_detector import evaluate as detect_security


def get_diff(cwd: str | None = None) -> str:
    """Return unified diff of last commit vs its parent. Empty string if unavailable."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD"],
            capture_output=True, text=True, cwd=cwd
        )
        if result.returncode != 0 or not result.stdout.strip():
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                capture_output=True, text=True, cwd=cwd
            )
        return result.stdout.strip()
    except Exception:
        return ""


def write_handoff(diff: str, metadata: dict, out_dir: str) -> Path:
    """Write review handoff file. Returns path written."""
    out = Path(out_dir) / "review-handoff.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Review Handoff — {timestamp}",
        "",
        "## Metadata",
        "",
        "```json",
        json.dumps(metadata, indent=2),
        "```",
        "",
        "## Diff",
        "",
        "```diff",
        diff if diff else "(no changes detected)",
        "```",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def should_trigger_security(diff: str) -> bool:
    found, _ = detect_security(diff)
    return found


def main() -> None:
    cwd = os.getcwd()
    claude_dir = Path(cwd) / ".claude"
    claude_dir.mkdir(exist_ok=True)

    diff = get_diff(cwd=cwd)

    metadata = {
        "agent": "trieu-van",
        "timestamp": datetime.now().isoformat(),
        "security_triggered": should_trigger_security(diff),
        "diff_lines": len(diff.splitlines()) if diff else 0,
    }

    handoff_path = write_handoff(diff=diff, metadata=metadata, out_dir=str(claude_dir))

    trigger = {
        "dispatch_phap_chinh": True,
        "dispatch_tu_ma_y": metadata["security_triggered"],
        "handoff_file": str(handoff_path),
        "diff_preview": diff[:500] if diff else "",
    }
    trigger_path = claude_dir / "review-trigger.json"
    trigger_path.write_text(json.dumps(trigger, indent=2), encoding="utf-8")

    if not diff:
        print("[review_trigger] No diff detected — skipping review dispatch.")
        sys.exit(0)

    print(f"[review_trigger] Handoff written: {handoff_path}")
    print(f"[review_trigger] Security triggered: {metadata['security_triggered']}")
    print(f"[review_trigger] Trigger: {trigger_path}")


if __name__ == "__main__":
    main()
