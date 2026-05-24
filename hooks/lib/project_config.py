"""Per-project config loader — reads .man.json from project root.

Usage:
    from hooks.lib.project_config import get_config
    cfg = get_config()
    cfg.get("hooks", {}).get("naming_gate", True)

Schema (.man.json):
    {
      "coding_level": 3,                          # 1-5, default 3
      "hooks": {
        "naming_gate": true,                       # toggle on/off
        "privacy_gate": true,
        "simplify_gate": {"warn": 500, "block": 1000},
        "security_gate": true
      },
      "test_command": "pytest -x",                 # auto-detect if omitted
      "lint_command": "ruff check .",
      "plan_naming": "{date}-{slug}",              # default format
      "default_mode": "interactive",               # interactive | autonomous
      "privacy_patterns": []                       # extra sensitive patterns
    }
"""
from __future__ import annotations

import json
import os
from typing import Any

_DEFAULTS: dict[str, Any] = {
    "coding_level": 3,
    "hooks": {
        "naming_gate": True,
        "privacy_gate": True,
        "simplify_gate": {"warn": 500, "block": 1000},
        "security_gate": True,
    },
    "test_command": "",
    "lint_command": "",
    "plan_naming": "{date}-{slug}",
    "default_mode": "interactive",
    "privacy_patterns": [],
    "instincts": {
        "enabled": True,
        "confidence_threshold": 0.7,
        "max_injected": 6,
    },
    "write_quality": {
        "enabled": False,
        "auto_format": True,
        "auto_lint": True,
        "block_config_edit": True,
    },
}

_cache: dict[str, Any] | None = None
_cache_mtime: float = 0.0


def _find_config_path() -> str | None:
    root = (
        os.environ.get("CLAUDE_PLUGIN_ROOT")
        or os.environ.get("CURSOR_PLUGIN_ROOT")
        or os.getcwd()
    )
    path = os.path.join(root, ".man.json")
    if os.path.isfile(path):
        return path
    return None


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Merge overlay into base recursively. Overlay wins on leaf values."""
    result = dict(base)
    for key, val in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def get_config(*, force_reload: bool = False) -> dict[str, Any]:
    """Load and cache .man.json config merged with defaults.

    Returns defaults if no .man.json exists. Caches by mtime.
    Fail-open: returns defaults on parse error.
    """
    global _cache, _cache_mtime

    path = _find_config_path()
    if path is None:
        return dict(_DEFAULTS)

    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return dict(_DEFAULTS)

    if _cache is not None and not force_reload and mtime == _cache_mtime:
        return _cache

    try:
        with open(path, encoding="utf-8") as f:
            user_config = json.load(f)
        if not isinstance(user_config, dict):
            return dict(_DEFAULTS)
        merged = _deep_merge(_DEFAULTS, user_config)
        _cache = merged
        _cache_mtime = mtime
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def is_hook_enabled(hook_name: str) -> bool:
    """Check if a specific hook is enabled in config."""
    cfg = get_config()
    hooks = cfg.get("hooks", {})
    val = hooks.get(hook_name, True)
    if isinstance(val, bool):
        return val
    if isinstance(val, dict):
        return True
    return bool(val)


def get_hook_config(hook_name: str) -> dict[str, Any]:
    """Get config dict for a specific hook. Returns {} if hook is bool or missing."""
    cfg = get_config()
    hooks = cfg.get("hooks", {})
    val = hooks.get(hook_name, {})
    if isinstance(val, dict):
        return val
    return {}


def reset_cache() -> None:
    """Clear cached config. Used in tests."""
    global _cache, _cache_mtime
    _cache = None
    _cache_mtime = 0.0
