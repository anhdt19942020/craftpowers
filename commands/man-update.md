---
description: "Update craftpowers to the latest version by pulling from the remote repository."
---

Find the craftpowers plugin directory by checking these locations in order:
1. `~/.claude/plugins/craftpowers`
2. The directory containing this command file (go up two levels from the commands folder)
3. Ask the user where they installed it if not found above

Then run `git pull` inside that directory and report:
- What version/commit they were on before
- What changed (new commits pulled in)
- Whether the update was successful
