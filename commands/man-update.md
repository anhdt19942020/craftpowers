---
description: "Update mankit to the latest version and apply full setup."
---

Detect install mode first:

- **Plugin install (marketplace):** root under `~/.claude/plugins/cache/craftpowers-dev/mankit/<version>/`
- **Dev clone:** local git repo (legacy junction or user-owned path)

Find the mankit root (try in order, stop at first hit):

1. Plugin install: glob `~/.claude/plugins/cache/craftpowers-dev/mankit/*/`, pick highest semver.

   PowerShell:
   ```
   Get-ChildItem "$HOME\.claude\plugins\cache\craftpowers-dev\mankit" -Directory | Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty FullName
   ```
   Unix:
   ```
   ls -d ~/.claude/plugins/cache/craftpowers-dev/mankit/*/ | sort -V | tail -1
   ```

2. Legacy junction: `(Get-Item "$HOME\.claude\commands").Target` (PowerShell) / `realpath ~/.claude/commands` (Unix).

3. Legacy fallback: `~/.claude/plugins/craftpowers`.

4. If still not found, ask the user.

---

**If root is under `plugins/cache/` (plugin install):**

Tell the user to run these slash commands in order:
```
/plugin marketplace update craftpowers-dev
/plugin install mankit@craftpowers-dev
/reload-plugins
```
Report old version (the directory name detected) and ask user to re-run `/man-check` after reload.

**If root is a git checkout (dev mode):**

Step 1 — Pull latest:
```
git -C <root> pull
```
Report previous commit and new commits pulled.

Step 2 — Install:
```
python <root>/scripts/install.py
```
Report each line.

Step 3 — Verify:
```
python <root>/scripts/verify.py
```
Report every [PASS] and [FAIL] line.

Step 4 — Tell the user: "Restart Claude Code to apply all changes."
