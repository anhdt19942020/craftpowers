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
import urllib.request


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


def setup_skills(craftpowers_root):
    """Create junction/symlink: ~/.claude/skills/ -> craftpowers/skills/"""
    setup_directory_link(
        "Skills",
        os.path.join(os.path.expanduser("~"), ".claude", "skills"),
        os.path.join(craftpowers_root, "skills")
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


def setup_user_permissions(settings_path, craftpowers_root=None):
    """Merge user-defined permissions and env from ~/.claude/user-permissions.json."""
    user_config_path = os.path.join(os.path.expanduser("~"), ".claude", "user-permissions.json")

    if not os.path.exists(user_config_path):
        if craftpowers_root:
            bundled = os.path.join(craftpowers_root, "user-permissions.json")
            if os.path.isfile(bundled):
                shutil.copy2(bundled, user_config_path)
                print(f"[OK] User permissions: copied from {bundled}")
            else:
                print("[SKIP] No user-permissions.json found")
                return
        else:
            print("[SKIP] No user-permissions.json found")
            return

    try:
        with open(user_config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except Exception as e:
        print(f"[WARN] Could not read user-permissions.json: {e}")
        return

    source_url = user_config.get("_source")
    if source_url:
        try:
            req = urllib.request.Request(source_url, headers={"User-Agent": "craftpowers/install"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                fetched = json.loads(resp.read().decode("utf-8"))
            fetched["_source"] = source_url
            with open(user_config_path, "w", encoding="utf-8") as f:
                json.dump(fetched, f, indent=2)
                f.write("\n")
            user_config = fetched
            print(f"[OK] User permissions: fetched latest from {source_url}")
        except Exception as e:
            print(f"[WARN] Could not fetch user-permissions, using cached version: {e}")

    settings = {}
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            pass

    perm_added = 0
    user_perms = user_config.get("permissions", [])
    if user_perms:
        if "permissions" not in settings:
            settings["permissions"] = {}
        if "allow" not in settings["permissions"]:
            settings["permissions"]["allow"] = []
        existing = set(settings["permissions"]["allow"])
        added = [p for p in user_perms if p not in existing]
        settings["permissions"]["allow"].extend(added)
        perm_added = len(added)

    env_added = 0
    user_env = user_config.get("env", {})
    if user_env:
        if "env" not in settings:
            settings["env"] = {}
        for key, value in user_env.items():
            settings["env"][key] = value
            env_added += 1

    if perm_added or env_added:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
            f.write("\n")

    print(f"[OK] User permissions: {perm_added} new rules, {env_added} env vars")


def setup_hooks(craftpowers_root, settings_path):
    """Add/update craftpowers hooks in ~/.claude/settings.json."""
    hooks_dir = os.path.join(craftpowers_root, "hooks").replace("\\", "/")

    hooks_config = {
        "SessionStart": [
            {
                "matcher": "",
                "hooks": [{"type": "command", "command": f'python "{hooks_dir}/session-start.py"'}]
            }
        ],
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


def sync_user_permissions(url):
    """Bootstrap: fetch user-permissions.json from URL and save locally."""
    user_config_path = os.path.join(os.path.expanduser("~"), ".claude", "user-permissions.json")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "craftpowers/install"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            fetched = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERR] Could not fetch from {url}: {e}")
        sys.exit(1)

    fetched["_source"] = url
    os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
    with open(user_config_path, "w", encoding="utf-8") as f:
        json.dump(fetched, f, indent=2)
        f.write("\n")

    print(f"[OK] user-permissions.json saved -> {user_config_path}")


def setup_context_mode():
    """Install Context Mode plugin globally via npm."""
    result = subprocess.run(
        ["npm", "install", "-g", "context-mode"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("[OK] Context Mode installed/updated")
    else:
        print(f"[WARN] Context Mode install failed (npm may not be available): {result.stderr.strip()}")


def main():
    sync_url = None
    if "--sync" in sys.argv:
        idx = sys.argv.index("--sync")
        if idx + 1 < len(sys.argv):
            sync_url = sys.argv[idx + 1]
        else:
            print("[ERR] --sync requires a URL argument")
            sys.exit(1)

    craftpowers_root = find_craftpowers_root()
    if not craftpowers_root:
        print("[ERR] Cannot find craftpowers root. Run from inside the craftpowers directory.")
        sys.exit(1)

    settings_path = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")

    if sync_url:
        sync_user_permissions(sync_url)

    print(f"craftpowers: {craftpowers_root}")
    setup_hooks(craftpowers_root, settings_path)
    setup_permissions(settings_path)
    setup_user_permissions(settings_path, craftpowers_root)
    setup_agents(craftpowers_root)
    setup_skills(craftpowers_root)
    setup_directory_link(
        "Commands",
        os.path.join(os.path.expanduser("~"), ".claude", "commands"),
        os.path.join(craftpowers_root, "commands")
    )
    setup_claudeignore(craftpowers_root)
    setup_context_mode()
    print("\nRestart Claude Code to apply changes.")


if __name__ == "__main__":
    main()
