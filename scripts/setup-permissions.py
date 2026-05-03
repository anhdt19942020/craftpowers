#!/usr/bin/env python3
"""
setup-permissions.py — Seed safe permission rules into .claude/settings.json.
Run once per project to reduce Claude Code permission prompts for common operations.

Usage: python scripts/setup-permissions.py [--path /path/to/project]
"""
import argparse
import json
import os
import sys

SAFE_PERMISSIONS = [
    # Read-only tools — always safe
    "Read(*)",
    "Glob(*)",
    "Grep(*)",

    # Git read operations
    "Bash(git status*)",
    "Bash(git log*)",
    "Bash(git diff*)",
    "Bash(git show*)",
    "Bash(git branch*)",
    "Bash(git fetch*)",
    "Bash(git remote*)",
    "Bash(git tag*)",
    "Bash(git blame*)",
    "Bash(git describe*)",
    "Bash(git reflog*)",
    "Bash(git rev-parse*)",
    "Bash(git config --list*)",
    "Bash(git config --get*)",
    "Bash(git stash list*)",
    "Bash(git worktree list*)",
    "Bash(git --version*)",

    # Test runners
    "Bash(npm test*)",
    "Bash(npm run test*)",
    "Bash(pnpm test*)",
    "Bash(pnpm run test*)",
    "Bash(yarn test*)",
    "Bash(cargo test*)",
    "Bash(go test*)",
    "Bash(pytest*)",
    "Bash(python -m pytest*)",
    "Bash(python3 -m pytest*)",
    "Bash(vitest*)",
    "Bash(jest*)",
    "Bash(npx vitest*)",
    "Bash(npx jest*)",

    # Build and lint (read results)
    "Bash(npm run build*)",
    "Bash(npm run lint*)",
    "Bash(npm run typecheck*)",
    "Bash(npm run check*)",
    "Bash(npm run format*)",
    "Bash(pnpm run build*)",
    "Bash(pnpm run lint*)",
    "Bash(pnpm run typecheck*)",
    "Bash(tsc*)",
    "Bash(eslint*)",
    "Bash(cargo build*)",
    "Bash(cargo check*)",
    "Bash(cargo clippy*)",
    "Bash(go build*)",
    "Bash(go vet*)",

    # Version / info
    "Bash(node --version*)",
    "Bash(node -v*)",
    "Bash(npm --version*)",
    "Bash(npm -v*)",
    "Bash(python --version*)",
    "Bash(python3 --version*)",
    "Bash(cargo --version*)",
    "Bash(go version*)",

    # File inspection (read-only)
    "Bash(ls*)",
    "Bash(cat*)",
    "Bash(head*)",
    "Bash(tail*)",
    "Bash(wc*)",
    "Bash(echo*)",
    "Bash(pwd*)",
    "Bash(which*)",
    "Bash(where*)",
    "Bash(find . *)",

    # RTK (token-optimized wrappers — safe by design)
    "Bash(rtk git*)",
    "Bash(rtk ls*)",
    "Bash(rtk grep*)",
    "Bash(rtk read*)",
    "Bash(rtk find*)",
]

def main():
    parser = argparse.ArgumentParser(description="Seed safe Claude Code permissions")
    parser.add_argument("--path", default=os.getcwd(), help="Project root (default: cwd)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be added without writing")
    args = parser.parse_args()

    claude_dir = os.path.join(args.path, ".claude")
    settings_path = os.path.join(claude_dir, "settings.json")

    # Load existing settings
    settings = {}
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception as e:
            print(f"Warning: could not read {settings_path}: {e}", file=sys.stderr)

    # Ensure permissions structure exists
    if "permissions" not in settings:
        settings["permissions"] = {}
    if "allow" not in settings["permissions"]:
        settings["permissions"]["allow"] = []

    existing = set(settings["permissions"]["allow"])
    to_add = [p for p in SAFE_PERMISSIONS if p not in existing]

    if not to_add:
        print(f"All {len(SAFE_PERMISSIONS)} permissions already present in {settings_path}")
        return

    if args.dry_run:
        print(f"Would add {len(to_add)} permissions to {settings_path}:")
        for p in to_add:
            print(f"  + {p}")
        return

    settings["permissions"]["allow"].extend(to_add)

    os.makedirs(claude_dir, exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    print(f"Added {len(to_add)} permission rules to {settings_path}")
    print(f"Total rules: {len(settings['permissions']['allow'])}")
    print("Restart Claude Code for changes to take effect.")

if __name__ == "__main__":
    main()
