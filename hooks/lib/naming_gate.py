"""PreToolUse naming gate — enforce descriptive kebab-case file names on Write."""
from __future__ import annotations

import os
import re

_GENERIC_NAMES = frozenset({
    "utils", "util", "helpers", "helper", "common", "misc", "temp", "tmp",
    "test", "index", "main", "app", "data", "config", "constants", "types",
    "models", "services", "core", "base", "manager", "handler", "processor",
})

_BAD_PREFIXES = frozenset({
    "enhanced-", "new-", "old-", "v2-", "v3-", "updated-", "improved-",
    "better-", "final-", "copy-", "backup-",
})

_KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

_SKIP_DIRS = frozenset({
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt",
})

_SKIP_EXTENSIONS = frozenset({
    ".json", ".lock", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".env", ".gitignore", ".dockerignore", ".editorconfig",
})

_ALWAYS_ALLOW = frozenset({
    "README.md", "CLAUDE.md", "AGENTS.md", "CHANGELOG.md", "LICENSE",
    "Makefile", "Dockerfile", "Taskfile.yml", "MEMORY.md",
    "__init__.py", "conftest.py", "pytest.ini", "pyproject.toml",
    "package.json", "tsconfig.json", ".gitignore",
})


def evaluate(tool_name: str, file_path: str) -> dict:
    """Check file name on Write/Edit. Returns {decision, reason}."""
    try:
        from hooks.lib.project_config import is_hook_enabled
        if not is_hook_enabled("naming_gate"):
            return {"decision": "approve", "reason": ""}
    except Exception:
        pass

    if tool_name not in ("Write",):
        return {"decision": "approve", "reason": ""}

    if not file_path:
        return {"decision": "approve", "reason": ""}

    basename = os.path.basename(file_path)
    name_only, ext = os.path.splitext(basename)

    if basename in _ALWAYS_ALLOW:
        return {"decision": "approve", "reason": ""}

    if ext.lower() in _SKIP_EXTENSIONS:
        return {"decision": "approve", "reason": ""}

    parts = file_path.replace("\\", "/").split("/")
    if any(p in _SKIP_DIRS for p in parts):
        return {"decision": "approve", "reason": ""}

    if basename.startswith("."):
        return {"decision": "approve", "reason": ""}

    if ext == ".md":
        stem_lower = name_only.lower()
        if stem_lower == stem_lower.upper():
            return {"decision": "approve", "reason": ""}

    for prefix in _BAD_PREFIXES:
        if name_only.lower().startswith(prefix):
            clean = name_only[len(prefix):]
            return {
                "decision": "block",
                "reason": (
                    f"[naming-gate] Bad prefix '{prefix}' in '{basename}'. "
                    f"Update existing file or use descriptive name: '{clean}{ext}'"
                ),
            }

    if name_only.lower() in _GENERIC_NAMES and ext not in (".md",):
        return {
            "decision": "block",
            "reason": (
                f"[naming-gate] Generic name '{basename}'. "
                f"Describe purpose: e.g. 'workflow-{name_only}{ext}' or 'auth-{name_only}{ext}'"
            ),
        }

    if ext in (".py", ".js", ".ts", ".tsx", ".jsx", ".vue", ".svelte", ".rb", ".go", ".rs"):
        if name_only.startswith("_"):
            return {"decision": "approve", "reason": ""}
        check_name = name_only.replace("_", "-")
        if not _KEBAB_RE.match(check_name) and not name_only.startswith("test_"):
            return {
                "decision": "warn",
                "reason": (
                    f"[naming-gate] '{basename}' not kebab-case. "
                    f"Suggested: '{check_name.lower()}{ext}'"
                ),
            }

    return {"decision": "approve", "reason": ""}
