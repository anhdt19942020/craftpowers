"""Hook profile system — minimal/standard/strict gate sets.

Profiles control which hooks are active. Selected via:
1. MAN_HOOK_PROFILE env var
2. .man.json "hook_profile" key
3. Default: "minimal"  (changed from "standard" to cut per-tool-call spawn latency)

## Hook tiers

### minimal (default)
Low-latency profile — only non-negotiable security gates fire on every tool call.
On Windows each Python spawn costs ~100-300 ms, so we keep PreToolUse spawns to 1.
- credential_scanner: ALWAYS ON — catches API keys / secrets in Bash + Write calls
- security_gate: ALWAYS ON — blocks dangerous shell commands
- privacy_gate: ON — prevents leaking file paths / PII to external tools
These three are non-negotiable and must remain True in ALL profiles.
SessionStart hooks (session_start.py) are cheap (once per session) and unaffected by profile.

### standard
Adds developer-productivity gates on top of minimal:
- naming_gate: enforces file/symbol naming conventions
- simplify_gate: flags overly complex code before it lands
- suggest_compact: prompts to compact context when nearing limits
- cost_tracker: tracks token/cost usage per session

### strict
Adds quality enforcement on top of standard:
- write_quality: blocks low-quality writes (undocumented public APIs, etc.)
All standard gates also active.
"""
from __future__ import annotations

import os
from typing import Any

from hooks.lib.project_config import get_config

PROFILES: dict[str, dict[str, bool]] = {
    # NON-NEGOTIABLE: credential_scanner + security_gate must be True in every profile.
    "minimal": {
        "security_gate": True,       # non-negotiable — blocks dangerous commands
        "privacy_gate": True,        # non-negotiable — prevents PII leakage
        "naming_gate": False,
        "simplify_gate": False,
        "write_quality": False,
        "suggest_compact": False,
        "credential_scanner": True,  # non-negotiable — catches secrets in writes/bash
        "cost_tracker": False,
    },
    "standard": {
        "security_gate": True,       # non-negotiable
        "privacy_gate": True,        # non-negotiable
        "naming_gate": True,
        "simplify_gate": True,
        "write_quality": False,
        "suggest_compact": True,
        "credential_scanner": True,  # non-negotiable
        "cost_tracker": True,
    },
    "strict": {
        "security_gate": True,       # non-negotiable
        "privacy_gate": True,        # non-negotiable
        "naming_gate": True,
        "simplify_gate": True,
        "write_quality": True,
        "suggest_compact": True,
        "credential_scanner": True,  # non-negotiable
        "cost_tracker": True,
    },
}


def get_active_profile() -> str:
    """Get the active hook profile name."""
    env_profile = os.environ.get("MAN_HOOK_PROFILE", "").lower()
    if env_profile in PROFILES:
        return env_profile

    cfg = get_config()
    cfg_profile = cfg.get("hook_profile", "minimal").lower()
    if cfg_profile in PROFILES:
        return cfg_profile

    return "minimal"


def is_gate_active(gate_name: str) -> bool:
    """Check if a specific gate is active under the current profile."""
    profile = get_active_profile()
    gates = PROFILES.get(profile, PROFILES["standard"])
    return gates.get(gate_name, True)


def get_profile_gates() -> dict[str, bool]:
    """Get the full gate map for the current profile."""
    profile = get_active_profile()
    return dict(PROFILES.get(profile, PROFILES["standard"]))
