#!/usr/bin/env python3
"""install-overlay.py — selective craftpowers overlay for a ClaudeKit-managed ~/.claude.

Copies a curated WHITELIST of skills (real files, user-owned — never junctions)
plus the intent-driven-development glue rule into ~/.claude.

Unlike install.py, this NEVER replaces whole directories and never touches
ClaudeKit-owned files. Safe to re-run anytime, including after `ck update`.

Usage:
  python scripts/install-overlay.py              install / refresh overlay
  python scripts/install-overlay.py --uninstall  remove everything this script installed
"""
import os
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAUDE_DIR = os.path.join(os.path.expanduser("~"), ".claude")
MARKER = ".craftpowers-overlay"  # ownership marker inside each installed skill dir

# Skill whitelist: name -> description override (None = keep original trigger).
# Overrides narrow auto-trigger so these skills never collide with the /ck:* pipeline.
SKILLS = {
    "brainstorming": (
        "Socratic intent-discovery interview. Use ONLY when user explicitly asks to "
        "brainstorm, or when routed by the intent-driven-development rule (Tier 2: "
        "ambiguous goal or large multi-phase work, BEFORE /ck:plan). Do NOT auto-trigger "
        "for regular feature work — /ck:plan owns that."
    ),
    "adversarial-design": None,
    "verification-before-completion": None,
    "test-driven-development": (
        "Strict red-green-refactor TDD discipline. Use ONLY when user explicitly "
        "requests TDD. Do NOT auto-trigger for regular implementation or test runs — "
        "/ck:cook and /ck:test own those."
    ),
}

RULES = ["intent-driven-development.md"]


def patch_description(skill_md_path, new_desc):
    """Replace the description: line in SKILL.md YAML frontmatter."""
    with open(skill_md_path, encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            lines[i] = 'description: "%s"\n' % new_desc.replace('"', '\\"')
            break
    else:
        print("[WARN] no description: line in %s — left unpatched" % skill_md_path)
        return
    with open(skill_md_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)


def overlay_owned(dst):
    """True if dst was installed by this script (has marker file)."""
    return os.path.isfile(os.path.join(dst, MARKER))


def install_skill(name, desc_override):
    src = os.path.join(REPO_ROOT, "skills", name)
    dst = os.path.join(CLAUDE_DIR, "skills", name)
    if not os.path.isdir(src):
        print("[ERR] skill missing in repo: %s" % src)
        return False
    if os.path.isdir(dst):
        if not overlay_owned(dst):
            # Same-named skill from another source (e.g. ClaudeKit) — never clobber.
            print("[SKIP] %s exists and is not overlay-owned — refusing to replace" % name)
            return False
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    open(os.path.join(dst, MARKER), "w").close()
    if desc_override:
        patch_description(os.path.join(dst, "SKILL.md"), desc_override)
        print("[OK] skill %s installed (trigger narrowed)" % name)
    else:
        print("[OK] skill %s installed" % name)
    return True


def install_rule(fname):
    src = os.path.join(REPO_ROOT, "rules", fname)
    dst = os.path.join(CLAUDE_DIR, "rules", fname)
    if not os.path.isfile(src):
        print("[ERR] rule missing in repo: %s" % src)
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print("[OK] rule %s installed" % fname)
    return True


def uninstall():
    for name in SKILLS:
        dst = os.path.join(CLAUDE_DIR, "skills", name)
        if os.path.isdir(dst) and overlay_owned(dst):
            shutil.rmtree(dst)
            print("[OK] removed skill %s" % name)
        elif os.path.isdir(dst):
            print("[SKIP] %s not overlay-owned — left in place" % name)
    for fname in RULES:
        dst = os.path.join(CLAUDE_DIR, "rules", fname)
        if os.path.isfile(dst):
            os.remove(dst)
            print("[OK] removed rule %s" % fname)


def main():
    if "--uninstall" in sys.argv:
        uninstall()
        return
    ok = True
    for name, desc in SKILLS.items():
        ok = install_skill(name, desc) and ok
    for fname in RULES:
        ok = install_rule(fname) and ok
    print("\nOverlay %s. Restart Claude Code to apply." % ("complete" if ok else "finished with errors"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
