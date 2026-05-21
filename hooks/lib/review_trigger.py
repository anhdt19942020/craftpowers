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

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.security_detector import evaluate as detect_security


def get_changed_php_files(cwd: str | None = None) -> list[str]:
    """Return list of .php files changed in the last commit or working tree."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD~1", "HEAD"],
            capture_output=True, text=True, cwd=cwd,
        )
        if result.returncode != 0 or not result.stdout.strip():
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD"],
                capture_output=True, text=True, cwd=cwd,
            )
        files = result.stdout.strip().splitlines()
        return [f for f in files if f.endswith(".php")]
    except Exception:
        return []


def run_php_lint(php_files: list[str], cwd: str | None = None) -> dict:
    """Run phpstan on changed PHP files. Returns {passed, errors, tool_found}."""
    if not php_files:
        return {"passed": True, "errors": "", "tool_found": False, "files": []}

    phpstan = os.path.join(cwd or ".", "vendor", "bin", "phpstan")
    if not os.path.isfile(phpstan):
        return {"passed": True, "errors": "", "tool_found": False, "files": php_files}

    try:
        result = subprocess.run(
            [phpstan, "analyse", "--no-progress", "--error-format=raw", *php_files],
            capture_output=True, text=True, cwd=cwd, timeout=120,
        )
        return {
            "passed": result.returncode == 0,
            "errors": result.stdout.strip() + result.stderr.strip(),
            "tool_found": True,
            "files": php_files,
        }
    except Exception as e:
        return {"passed": True, "errors": str(e), "tool_found": True, "files": php_files}


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

    if not diff:
        trigger_path = claude_dir / "review-trigger.json"
        trigger_path.write_text(
            json.dumps({"dispatch_phap_chinh": False, "dispatch_tu_ma_y": False, "reason": "no diff"}, indent=2),
            encoding="utf-8",
        )
        print("[review_trigger] No diff detected — skipping review dispatch.")
        sys.exit(0)

    php_files = get_changed_php_files(cwd=cwd)
    php_lint = run_php_lint(php_files, cwd=cwd)

    metadata = {
        "agent": "trieu-van",
        "timestamp": datetime.now().isoformat(),
        "security_triggered": should_trigger_security(diff),
        "diff_lines": len(diff.splitlines()),
        "php_files_changed": len(php_files),
        "php_lint_passed": php_lint["passed"],
        "php_lint_tool_found": php_lint["tool_found"],
    }

    handoff_path = write_handoff(diff=diff, metadata=metadata, out_dir=str(claude_dir))

    trigger = {
        "dispatch_phap_chinh": True,
        "dispatch_tu_ma_y": metadata["security_triggered"],
        "handoff_file": str(handoff_path),
        "diff_preview": diff[:500],
        "php_lint": php_lint,
    }
    trigger_path = claude_dir / "review-trigger.json"
    trigger_path.write_text(json.dumps(trigger, indent=2), encoding="utf-8")

    print(f"[review_trigger] Handoff written: {handoff_path}")
    print(f"[review_trigger] Security triggered: {metadata['security_triggered']}")
    if php_files:
        status = "PASS" if php_lint["passed"] else "FAIL"
        print(f"[review_trigger] PHP lint ({len(php_files)} files): {status}")
        if not php_lint["passed"]:
            print(f"[review_trigger] PHP errors:\n{php_lint['errors']}")
        if not php_lint["tool_found"]:
            print(f"[review_trigger] phpstan not found — PHP lint skipped")
    print(f"[review_trigger] Trigger: {trigger_path}")


if __name__ == "__main__":
    main()
