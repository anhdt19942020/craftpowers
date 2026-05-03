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
        # lstat() does NOT follow junctions — preserves REPARSE_POINT flag
        return bool(os.lstat(path).st_file_attributes & 0x400)
    except AttributeError:
        return False


def setup_directory_link(label, link_path, target_path):
    """Generic junction/symlink creator — shared by agents and commands."""
    if is_pointing_to(link_path, target_path):
        print(f"[OK] {label} already linked -> {target_path}")
        return

    if os.path.exists(link_path):
        if is_junction_or_link(link_path):
            os.rmdir(link_path)
        else:
            shutil.rmtree(link_path)

    if platform.system() == "Windows":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", link_path, target_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"[ERR] Junction failed for {label}: {result.stderr.strip()}")
            sys.exit(1)
    else:
        os.symlink(target_path, link_path)

    print(f"[OK] {label} linked -> {target_path}")


def setup_agents(craftpowers_root):
    """Create junction/symlink: ~/.claude/agents/ -> craftpowers/agents/"""
    setup_directory_link(
        "Agents",
        os.path.join(os.path.expanduser("~"), ".claude", "agents"),
        os.path.join(craftpowers_root, "agents")
    )


SAFE_PERMISSIONS = [
    "Read(*)", "Glob(*)", "Grep(*)",
    "Bash(git status*)", "Bash(git log*)", "Bash(git diff*)", "Bash(git show*)",
    "Bash(git branch*)", "Bash(git fetch*)", "Bash(git remote*)", "Bash(git tag*)",
    "Bash(git blame*)", "Bash(git describe*)", "Bash(git reflog*)",
    "Bash(git rev-parse*)", "Bash(git config --list*)", "Bash(git config --get*)",
    "Bash(git stash list*)", "Bash(git worktree list*)", "Bash(git --version*)",
    "Bash(npm test*)", "Bash(npm run test*)", "Bash(npm run build*)",
    "Bash(npm run lint*)", "Bash(npm run typecheck*)", "Bash(npm run check*)",
    "Bash(npm run format*)", "Bash(npm --version*)", "Bash(npm -v*)",
    "Bash(pnpm test*)", "Bash(pnpm run test*)", "Bash(pnpm run build*)",
    "Bash(pnpm run lint*)", "Bash(pnpm run typecheck*)",
    "Bash(yarn test*)",
    "Bash(tsc*)", "Bash(eslint*)", "Bash(vitest*)", "Bash(jest*)",
    "Bash(npx vitest*)", "Bash(npx jest*)",
    "Bash(cargo test*)", "Bash(cargo build*)", "Bash(cargo check*)",
    "Bash(cargo clippy*)", "Bash(cargo --version*)",
    "Bash(go test*)", "Bash(go build*)", "Bash(go vet*)", "Bash(go version*)",
    "Bash(pytest*)", "Bash(python -m pytest*)", "Bash(python3 -m pytest*)",
    "Bash(python --version*)", "Bash(python3 --version*)",
    "Bash(node --version*)", "Bash(node -v*)",
    "Bash(ls*)", "Bash(cat*)", "Bash(head*)", "Bash(tail*)",
    "Bash(wc*)", "Bash(echo*)", "Bash(pwd*)", "Bash(which*)",
    "Bash(where*)", "Bash(find . *)",
    "Bash(rtk git*)", "Bash(rtk ls*)", "Bash(rtk grep*)",
    "Bash(rtk read*)", "Bash(rtk find*)",
]


def setup_permissions(settings_path):
    """Add safe permission rules to ~/.claude/settings.json (global, idempotent)."""
    settings = {}
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            pass

    if "permissions" not in settings:
        settings["permissions"] = {}
    if "allow" not in settings["permissions"]:
        settings["permissions"]["allow"] = []

    existing = set(settings["permissions"]["allow"])
    added = [p for p in SAFE_PERMISSIONS if p not in existing]
    settings["permissions"]["allow"].extend(added)

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    if added:
        print(f"[OK] Permissions: added {len(added)} rules ({len(settings['permissions']['allow'])} total)")
    else:
        print(f"[OK] Permissions: all {len(SAFE_PERMISSIONS)} rules already present")


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


CLAUDEIGNORE_TEMPLATE = """\
# Build outputs
dist/
build/
out/
.next/
target/
*.min.js
*.min.css
*.bundle.js

# Dependencies
node_modules/
vendor/
.venv/
__pycache__/
*.pyc

# Logs and databases
*.log
*.sqlite
*.db

# Lock files (large, low signal)
package-lock.json
pnpm-lock.yaml
yarn.lock
Cargo.lock
poetry.lock
composer.lock

# IDE and OS
.idea/
.vscode/
*.swp
.DS_Store
Thumbs.db

# Test artifacts
coverage/
.nyc_output/
htmlcov/
.pytest_cache/

# Generated docs
docs/craftpowers/
"""


def setup_claudeignore(project_root):
    """Create .claudeignore template in current project if not present."""
    target = os.path.join(project_root, ".claudeignore")
    if os.path.exists(target):
        print(f"[OK] .claudeignore already exists -> {target}")
        return

    with open(target, "w", encoding="utf-8") as f:
        f.write(CLAUDEIGNORE_TEMPLATE)

    print(f"[OK] .claudeignore created -> {target}")


def main():
    craftpowers_root = find_craftpowers_root()
    if not craftpowers_root:
        print("[ERR] Cannot find craftpowers root. Run from inside the craftpowers directory.")
        sys.exit(1)

    settings_path = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")

    print(f"craftpowers: {craftpowers_root}")
    setup_hooks(craftpowers_root, settings_path)
    setup_permissions(settings_path)
    setup_agents(craftpowers_root)
    setup_directory_link(
        "Commands",
        os.path.join(os.path.expanduser("~"), ".claude", "commands"),
        os.path.join(craftpowers_root, "commands")
    )
    setup_claudeignore(craftpowers_root)
    print("\nRestart Claude Code to apply changes.")


if __name__ == "__main__":
    main()
