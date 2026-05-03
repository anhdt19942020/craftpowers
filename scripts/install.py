#!/usr/bin/env python3
"""
install.py — Setup craftpowers hooks and agents for Claude Code.
Idempotent: safe to run multiple times.

Called automatically by /man-update after git pull.
Run manually on first install: python scripts/install.py
"""
import json
import os
import platform
import shutil
import subprocess
import sys


def find_craftpowers_root():
    """Detect craftpowers root from this script's location."""
    # scripts/install.py -> go up 1 level -> craftpowers root
    candidate = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(candidate, ".claude-plugin", "plugin.json")):
        return candidate

    # Fallback: ~/.claude/plugins/craftpowers (installed via plugin system)
    candidate = os.path.join(os.path.expanduser("~"), ".claude", "plugins", "craftpowers")
    if os.path.exists(candidate):
        return candidate

    return None


def is_pointing_to(link_path, target_path):
    """Check if link_path already resolves to target_path (junction or symlink)."""
    try:
        return os.path.exists(link_path) and os.path.samefile(link_path, target_path)
    except Exception:
        return False


def is_junction_or_link(path):
    """Detect Windows junction (reparse point) or Unix symlink."""
    if os.path.islink(path):
        return True
    try:
        # FILE_ATTRIBUTE_REPARSE_POINT = 0x400
        return bool(os.stat(path).st_file_attributes & 0x400)
    except AttributeError:
        return False


def setup_agents(craftpowers_root):
    """Create junction/symlink: ~/.claude/agents/ -> craftpowers/agents/"""
    agents_target = os.path.join(craftpowers_root, "agents")
    agents_link = os.path.join(os.path.expanduser("~"), ".claude", "agents")

    if is_pointing_to(agents_link, agents_target):
        print(f"[OK] Agents already linked -> {agents_target}")
        return

    # Remove existing (junction -> rmdir, regular dir -> rmtree)
    if os.path.exists(agents_link):
        if is_junction_or_link(agents_link):
            os.rmdir(agents_link)
        else:
            shutil.rmtree(agents_link)

    # Create junction (Windows) or symlink (Unix/macOS)
    if platform.system() == "Windows":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", agents_link, agents_target],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"[ERR] Junction failed: {result.stderr.strip()}")
            sys.exit(1)
    else:
        os.symlink(agents_target, agents_link)

    print(f"[OK] Agents linked -> {agents_target}")


def setup_hooks(craftpowers_root, settings_path):
    """Add/update craftpowers hooks in ~/.claude/settings.json."""
    hooks_dir = os.path.join(craftpowers_root, "hooks").replace("\\", "/")

    hooks_config = {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [{"type": "command", "command": f'python "{hooks_dir}/security-gate.py"'}]
            }
        ],
        "PostToolUse": [
            {
                "matcher": "Write|Edit",
                "hooks": [{"type": "command", "command": f'python "{hooks_dir}/credential-scanner.py"'}]
            }
        ],
        "UserPromptSubmit": [
            {
                "matcher": "",
                "hooks": [{"type": "command", "command": f'python "{hooks_dir}/context-tracker.py"'}]
            }
        ],
    }

    settings = {}
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            pass

    settings["hooks"] = hooks_config

    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    print(f"[OK] Hooks configured -> {hooks_dir}")


def main():
    craftpowers_root = find_craftpowers_root()
    if not craftpowers_root:
        print("[ERR] Cannot find craftpowers root. Run from inside the craftpowers directory.")
        sys.exit(1)

    settings_path = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")

    print(f"craftpowers: {craftpowers_root}")
    setup_hooks(craftpowers_root, settings_path)
    setup_agents(craftpowers_root)
    print("\nRestart Claude Code to apply changes.")


if __name__ == "__main__":
    main()
