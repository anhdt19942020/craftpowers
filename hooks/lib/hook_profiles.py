"""Hook profile system — minimal/standard/strict gate sets.

Profiles control which hooks are active. Selected via:
1. MAN_HOOK_PROFILE env var
2. .man.json "hook_profile" key
3. Default: "standard"
"""
from __future__ import annotations

import os
from typing import Any

from hooks.lib.project_config import get_config

PROFILES: dict[str, dict[str, bool]] = {
    "minimal": {
        "security_gate": True,
        "privacy_gate": True,
        "naming_gate": False,
        "simplify_gate": False,
        "write_quality": False,
        "suggest_compact": False,
        "credential_scanner": True,
        "cost_tracker": False,
    },
    "standard": {
        "security_gate": True,
        "privacy_gate": True,
        "naming_gate": True,
        "simplify_gate": True,
        "write_quality": False,
        "suggest_compact": True,
        "credential_scanner": True,
        "cost_tracker": True,
    },
    "strict": {
        "security_gate": True,
        "privacy_gate": True,
        "naming_gate": True,
        "simplify_gate": True,
        "write_quality": True,
        "suggest_compact": True,
        "credential_scanner": True,
        "cost_tracker": True,
    },
}


def get_active_profile() -> str:
    """Get the active hook profile name."""
    env_profile = os.environ.get("MAN_HOOK_PROFILE", "").lower()
    if env_profile in PROFILES:
        return env_profile

    cfg = get_config()
    cfg_profile = cfg.get("hook_profile", "standard").lower()
    if cfg_profile in PROFILES:
        return cfg_profile

    return "standard"


def is_gate_active(gate_name: str) -> bool:
    """Check if a specific gate is active under the current profile."""
    profile = get_active_profile()
    gates = PROFILES.get(profile, PROFILES["standard"])
    return gates.get(gate_name, True)


def get_profile_gates() -> dict[str, bool]:
    """Get the full gate map for the current profile."""
    profile = get_active_profile()
    return dict(PROFILES.get(profile, PROFILES["standard"]))
