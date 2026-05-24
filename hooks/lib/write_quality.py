"""Write-time quality enforcement — runs formatter and linter on modified files.

PostToolUse hook on Edit/Write events. Catches issues at write time, not commit time.
Disabled by default — enable with .man.json: {"write_quality": {"enabled": true}}.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from hooks.lib.project_config import get_config
from hooks.lib.project_stack import detect_stack

# Linter config files that agents should not modify
CONFIG_FILES = {
    ".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml",
    "biome.json", "biome.jsonc",
    ".prettierrc", ".prettierrc.js", ".prettierrc.json",
    "ruff.toml", "pyproject.toml",
    ".flake8", "setup.cfg",
    ".rubocop.yml",
    "clippy.toml",
}

FORMATTER_MAP: dict[str, list[str]] = {
    "python": ["ruff", "format"],
    "typescript": ["npx", "prettier", "--write"],
    "node": ["npx", "prettier", "--write"],
    "rust": ["rustfmt"],
    "go": ["gofmt", "-w"],
}

LINTER_MAP: dict[str, list[str]] = {
    "python": ["ruff", "check", "--fix"],
    "typescript": ["npx", "eslint", "--fix"],
    "node": ["npx", "eslint", "--fix"],
    "rust": ["cargo", "clippy", "--fix", "--allow-dirty"],
}

EXT_TO_STACK: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "node",
    ".jsx": "node",
    ".rs": "rust",
    ".go": "go",
}


def _is_config_file(file_path: str) -> bool:
    return Path(file_path).name in CONFIG_FILES


def _run_tool(cmd: list[str], file_path: str, timeout: int = 30) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd + [file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return True, ""


def evaluate(tool_name: str, file_path: str) -> dict[str, Any]:
    """Evaluate a file write/edit for quality. Returns verdict dict."""
    result: dict[str, Any] = {"decision": "ok", "messages": []}

    cfg = get_config()
    wq_cfg = cfg.get("write_quality", {})
    if not wq_cfg.get("enabled", False):
        return result

    if not file_path:
        return result

    # Block linter/formatter config file edits
    if wq_cfg.get("block_config_edit", True) and _is_config_file(file_path):
        return {
            "decision": "block",
            "reason": (
                f"[write-quality] Blocked: editing linter/formatter config "
                f"'{Path(file_path).name}' is not allowed. Change code to match the "
                f"config, not the other way around."
            ),
        }

    # Determine stack for this file extension
    ext = Path(file_path).suffix
    stack_for_file = EXT_TO_STACK.get(ext)
    if not stack_for_file:
        return result

    # Only run tools if the detected project stack includes this language
    stacks = detect_stack()
    if stack_for_file not in stacks:
        return result

    messages: list[str] = []

    if wq_cfg.get("auto_format", True) and stack_for_file in FORMATTER_MAP:
        ok, output = _run_tool(FORMATTER_MAP[stack_for_file], file_path)
        if not ok and output:
            messages.append(f"Formatter issues: {output[:200]}")

    if wq_cfg.get("auto_lint", True) and stack_for_file in LINTER_MAP:
        ok, output = _run_tool(LINTER_MAP[stack_for_file], file_path)
        if not ok and output:
            messages.append(f"Lint violations (unfixable): {output[:300]}")

    if messages:
        result["messages"] = messages
        result["systemMessage"] = "[write-quality] " + "; ".join(messages)

    return result
