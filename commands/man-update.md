---
description: "Update craftpowers to the latest version and apply full setup."
---

Find the craftpowers plugin directory by checking these locations in order:
1. The directory containing this command file (go up two levels from the commands folder)
2. `~/.claude/plugins/craftpowers`
3. Ask the user where they installed it if not found above

Then run these steps in order:

**Step 1 — Pull latest code**
Run `git pull` inside the craftpowers directory and report:
- What version/commit they were on before
- What changed (new commits pulled in)
- Whether the pull was successful

**Step 2 — Run install script**
Run `python scripts/install.py` inside the craftpowers directory.
This configures hooks and agents automatically. Report the output.

**Step 3 — Remind user**
Tell the user: "Restart Claude Code to apply all changes."
