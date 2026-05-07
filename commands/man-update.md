---
description: "Update craftpowers to the latest version and apply full setup."
---

Find the craftpowers root directory using this method:

1. Resolve `~/.claude/commands/` to its real path — it is a junction/symlink pointing to `craftpowers/commands/`. Go up one level to get the craftpowers root.

   On Windows (PowerShell):
   ```
   (Get-Item "$HOME\.claude\commands").Target
   ```
   On Unix:
   ```
   realpath ~/.claude/commands
   ```

2. Fallback: `~/.claude/plugins/man`

3. If still not found, ask the user where craftpowers is installed.

Once you have the root, run these steps in order:

**Step 1 — Pull latest code**
Run `git pull` inside the craftpowers directory and report:
- What version/commit they were on before
- What changed (new commits pulled in)

**Step 2 — Run install script**
Run `python <root>/scripts/install.py`
Report each line of output.

**Step 3 — Verify setup**
Run `python <root>/scripts/verify.py`
Report every [PASS] and [FAIL] line.

**Step 4 — Remind user**
Tell the user: "Restart Claude Code to apply all changes."
