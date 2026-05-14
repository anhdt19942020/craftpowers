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

Step 0 — Check current version and compare with npm registry:
```powershell
# PowerShell — get current cached version
$current = Get-ChildItem "$HOME\.claude\plugins\cache\mankit\mankit" -Directory | Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty Name
echo "Current cached: $current"
# Fetch latest from npm
$latest_npm = (Invoke-RestMethod "https://registry.npmjs.org/craftpowers/latest").version
echo "Latest on npm: $latest_npm"
```
```bash
# Unix
current=$(ls -d ~/.claude/plugins/cache/mankit/mankit/*/ | sort -V | tail -1 | xargs basename)
latest_npm=$(curl -s https://registry.npmjs.org/craftpowers/latest | python3 -c "import sys,json; print(json.load(sys.stdin)['version'])")
echo "Current cached: $current — Latest on npm: $latest_npm"
```
If versions match: tell user "Already on latest version ($current). No update needed." and STOP.

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

Step 3.5 — Remove old cache dirs (keep only latest):
```powershell
# PowerShell
$all = Get-ChildItem "$HOME\.claude\plugins\cache\mankit\mankit" -Directory | Sort-Object Name -Descending
$all | Select-Object -Skip 1 | ForEach-Object { Remove-Item $_.FullName -Recurse -Force; echo "Removed old cache: $($_.Name)" }
```
```bash
# Unix
ls -d ~/.claude/plugins/cache/mankit/mankit/*/ | sort -V | head -n -1 | while read d; do
  rm -rf "$d" && echo "Removed old cache: $d"
done
```

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
