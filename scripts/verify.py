#!/usr/bin/env python3
"""
verify.py — Check that craftpowers is fully set up.
Run after install.py to confirm everything works.

Called by /man-update and /man-check.
"""
import json
import os
import platform
import subprocess
import sys

EXPECTED_AGENTS = ["code-reviewer", "debugger", "doc-writer", "secure-reviewer", "test-engineer"]
EXPECTED_HOOKS = ["SessionStart", "PreToolUse", "PostToolUse", "UserPromptSubmit"]
EXPECTED_HOOK_FILES = ["session-start.py", "security-gate.py", "credential-scanner.py", "context-tracker.py"]
MIN_PERMISSIONS = 50

HOME = os.path.expanduser("~")
SETTINGS_PATH = os.path.join(HOME, ".claude", "settings.json")
AGENTS_LINK = os.path.join(HOME, ".claude", "agents")
SKILLS_LINK = os.path.join(HOME, ".claude", "skills")


def find_craftpowers_root():
    candidate = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(candidate, ".claude-plugin", "plugin.json")):
        return candidate
    candidate = os.path.join(HOME, ".claude", "plugins", "craftpowers")
    if os.path.exists(candidate):
        return candidate
    return None


def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return {}
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def is_junction_or_link(path):
    if os.path.islink(path):
        return True
    try:
        # lstat() does NOT follow junctions — preserves REPARSE_POINT flag
        return bool(os.lstat(path).st_file_attributes & 0x400)
    except AttributeError:
        return False


def check(label, ok, detail=""):
    status = "[PASS]" if ok else "[FAIL]"
    line = f"  {status} {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    return ok


def run_hook_test(script_path, stdin_json, expect_block=False):
    """Run a hook script with test input, return (success, output)."""
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            input=json.dumps(stdin_json),
            capture_output=True, text=True, timeout=5
        )
        if expect_block:
            blocked = result.returncode == 2
            return blocked, result.stdout.strip()
        else:
            passed = result.returncode == 0
            return passed, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def main():
    root = find_craftpowers_root()
    all_pass = True

    print(f"craftpowers verify — {root or 'ROOT NOT FOUND'}")
    print("")

    # 1. Mankit root
    print("[1] Installation")
    ok = root is not None
    all_pass &= check("craftpowers root found", ok, root or "not found")
    if not ok:
        print("\n[FAIL] Cannot continue without craftpowers root.")
        sys.exit(1)

    # 2. Settings file
    print("")
    print("[2] settings.json")
    settings = load_settings()
    all_pass &= check("~/.claude/settings.json exists", os.path.exists(SETTINGS_PATH))

    hooks = settings.get("hooks", {})
    for event in EXPECTED_HOOKS:
        all_pass &= check(f"hooks.{event} configured", event in hooks)

    perms = settings.get("permissions", {}).get("allow", [])
    all_pass &= check(
        f"permissions.allow >= {MIN_PERMISSIONS} rules",
        len(perms) >= MIN_PERMISSIONS,
        f"{len(perms)} rules found"
    )

    # 3. Hook files
    print("")
    print("[3] Hook scripts")
    hooks_dir = os.path.join(root, "hooks")
    for fname in EXPECTED_HOOK_FILES:
        fpath = os.path.join(hooks_dir, fname)
        exists = os.path.isfile(fpath)
        all_pass &= check(f"hooks/{fname}", exists)

    # 4. Hook commands in settings point to existing files
    print("")
    print("[4] Hook paths valid")
    for event, entries in hooks.items():
        for entry in entries:
            for hook in entry.get("hooks", []):
                cmd = hook.get("command", "")
                # Extract path between quotes
                parts = cmd.split('"')
                if len(parts) >= 2:
                    path = parts[1]
                    all_pass &= check(f"{event} -> {os.path.basename(path)}", os.path.isfile(path), path)

    # 5. Agents
    print("")
    print("[5] Agents")
    agents_ok = os.path.exists(AGENTS_LINK)
    all_pass &= check("~/.claude/agents/ exists", agents_ok)

    if agents_ok:
        is_link = is_junction_or_link(AGENTS_LINK)
        all_pass &= check("~/.claude/agents/ is junction/symlink", is_link,
                          "copy (won't auto-update)" if not is_link else "live")

        agents_target = os.path.join(root, "agents")
        try:
            in_sync = os.path.samefile(AGENTS_LINK, agents_target)
        except Exception:
            in_sync = False
        all_pass &= check("agents/ points to craftpowers", in_sync, agents_target)

        for name in EXPECTED_AGENTS:
            fpath = os.path.join(AGENTS_LINK, f"{name}.md")
            all_pass &= check(f"agent: {name}", os.path.isfile(fpath))

    # 6. Skills
    print("")
    print("[6] Skills")
    skills_ok = os.path.exists(SKILLS_LINK)
    all_pass &= check("~/.claude/skills/ exists", skills_ok)

    if skills_ok:
        is_link = is_junction_or_link(SKILLS_LINK)
        all_pass &= check("~/.claude/skills/ is junction/symlink", is_link,
                          "copy (won't auto-update)" if not is_link else "live")

        skills_target = os.path.join(root, "skills")
        try:
            in_sync = os.path.samefile(SKILLS_LINK, skills_target)
        except Exception:
            in_sync = False
        all_pass &= check("skills/ points to craftpowers", in_sync, skills_target)

    # 7. Token optimization
    print("")
    print("[7] Token optimization")
    claudeignore = os.path.join(root, ".claudeignore")
    all_pass &= check(".claudeignore exists", os.path.isfile(claudeignore),
                       "reduces context by excluding build/deps/logs" if os.path.isfile(claudeignore) else "run install.py to create")

    # 8. User permissions
    print("")
    print("[8] User permissions")
    user_config_path = os.path.join(HOME, ".claude", "user-permissions.json")
    if os.path.isfile(user_config_path):
        try:
            with open(user_config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            user_perms = len(user_config.get("permissions", []))
            user_env = len(user_config.get("env", {}))
            source = user_config.get("_source", "local-only")
            check("user-permissions.json found", True, f"{user_perms} permissions, {user_env} env vars, source: {source}")
        except Exception as e:
            check("user-permissions.json readable", False, str(e))
            all_pass = False
    else:
        print("  [SKIP] user-permissions.json not found (optional)")

    # 9. Hook smoke tests
    print("")
    print("[9] Hook smoke tests")
    print("")

    sg = os.path.join(hooks_dir, "security-gate.py")
    ok, out = run_hook_test(sg, {"tool_input": {"command": "rm -rf /tmp/x"}}, expect_block=True)
    all_pass &= check("security-gate blocks rm -rf", ok, "blocked" if ok else f"NOT blocked: {out[:60]}")

    ok, out = run_hook_test(sg, {"tool_input": {"command": "git status"}}, expect_block=False)
    all_pass &= check("security-gate passes git status", ok, "passed" if ok else f"wrongly blocked: {out[:60]}")

    cs = os.path.join(hooks_dir, "credential-scanner.py")
    ok, out = run_hook_test(cs, {"tool_input": {"file_path": "x.py", "content": 'KEY="AKIAIOSFODNN7EXAMPLE"'}})
    detected = "systemMessage" in out
    all_pass &= check("credential-scanner detects AWS key", detected, "detected" if detected else "silent")

    ok, out = run_hook_test(cs, {"tool_input": {"file_path": "x.py", "content": 'KEY=os.environ["KEY"]'}})
    clean = out == ""
    all_pass &= check("credential-scanner ignores env var", clean, "clean" if clean else "false positive")

    # Summary
    print("")
    if all_pass:
        print("[ALL PASS] craftpowers is fully configured.")
    else:
        print("[INCOMPLETE] Some checks failed. Run: python scripts/install.py")
    print("")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
