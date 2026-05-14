---
description: "Update mankit to the latest version and apply full setup."
---

Detect install mode first:

- **Plugin install (marketplace):** root under `~/.claude/plugins/cache/mankit/mankit/<version>/`
- **Dev clone:** local git repo (legacy junction or user-owned path)

Find the mankit root (try in order, stop at first hit):

1. Plugin install: glob `~/.claude/plugins/cache/mankit/mankit/*/`, pick highest semver.

   PowerShell:
   ```
   Get-ChildItem "$HOME\.claude\plugins\cache\mankit\mankit" -Directory | Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty FullName
   ```
   Unix:
   ```
   ls -d ~/.claude/plugins/cache/mankit/mankit/*/ | sort -V | tail -1
   ```

2. Legacy junction: `(Get-Item "$HOME\.claude\commands").Target` (PowerShell) / `realpath ~/.claude/commands` (Unix).

3. Legacy fallback: `~/.claude/plugins/craftpowers`.

4. If still not found, ask the user.

---

**If root is under `plugins/cache/` (plugin install):**

Step 1 — Pull latest from marketplace. Run this command:
```bash
# Unix/Mac
claude --print-only /plugin marketplace update mankit 2>/dev/null || echo "Run manually: /plugin marketplace update mankit"

# The command above may not work non-interactively. If so, tell user:
```
Tell the user to run: `/plugin marketplace update mankit`
Wait for user confirmation before proceeding.

Step 2 — Detect latest version in cache:
```powershell
# PowerShell
$latest = Get-ChildItem "$HOME\.claude\plugins\cache\mankit\mankit" -Directory | Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty FullName
echo "Latest version: $latest"
```
```bash
# Unix
latest=$(ls -d ~/.claude/plugins/cache/mankit/mankit/*/ | sort -V | tail -1)
echo "Latest version: $latest"
```

Step 3 — Run install.py from the latest cached version:
```powershell
# PowerShell
python "$latest\scripts\install.py"
```
```bash
# Unix
python3 "$latest/scripts/install.py"
```
This automatically updates:
- Commands junction → latest version
- Agents junction → latest version
- Skills junction → latest version
- Hooks in settings.json → latest version paths
- Permissions → latest safe rules

Step 4 — Report old version and new version. Tell user:
```
/reload-plugins
```

Step 5 — Verify:
```powershell
# PowerShell
python "$latest\scripts\verify.py"
```
```bash
# Unix
python3 "$latest/scripts/verify.py"
```
Report every [PASS] and [FAIL] line.

---

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

Step 4 — Tell the user: "Run `/reload-plugins` then restart Claude Code to apply all changes."
