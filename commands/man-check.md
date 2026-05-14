---
description: "Check that mankit is fully configured — hooks, agents, permissions, and hook smoke tests."
---

## Step 0 — Detect dev path and auto-sync

Check `~/.claude/settings.json` for a local dev path:

```python
import json, os
s = json.load(open(os.path.expanduser("~/.claude/settings.json")))
dev_path = s.get("extraKnownMarketplaces", {}).get("mankit", {}).get("source", {}).get("path")
print(dev_path or "NOT SET")
```

**If dev path is set** (e.g. `D:\projects\craftpowers`):
- Read version from `<dev_path>/package.json`
- Read version from highest cache dir under `~/.claude/plugins/cache/mankit/mankit/`
- If versions differ OR cache junction is stale → **automatically run:**
  ```
  python <dev_path>/scripts/install.py
  ```
  Report: `[AUTO] Ran install.py — synced to v<version>`
- No need to ask the user. Just do it.

**If no dev path** → skip to Step 1.

## Step 1 — Find mankit root

Try in order, stop at first hit:

1. **Plugin install (marketplace):** glob `~/.claude/plugins/cache/mankit/mankit/*/` and pick the highest semver directory.

   PowerShell:
   ```
   Get-ChildItem "$HOME\.claude\plugins\cache\mankit\mankit" -Directory | Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty FullName
   ```
   Unix:
   ```
   ls -d ~/.claude/plugins/cache/mankit/mankit/*/ | sort -V | tail -1
   ```

2. **Legacy junction:** resolve `~/.claude/commands/` real path, go up one level.

   PowerShell: `(Get-Item "$HOME\.claude\commands").Target`
   Unix: `realpath ~/.claude/commands`

3. **Legacy fallback:** `~/.claude/plugins/craftpowers`

4. If still not found, ask the user where mankit is installed.

Once you have the root, run:
```
python <root>/scripts/verify.py
```

Report every [PASS] and [FAIL] line exactly as printed.

After verify.py, also check:

```
# PowerShell
python -c "import json,os; s=json.load(open(os.path.expanduser('~/.claude/settings.json'))); print('agentTeams:', s.get('agentTeams'))"

# Unix
python3 -c "import json,os; s=json.load(open(os.path.expanduser('~/.claude/settings.json'))); print('agentTeams:', s.get('agentTeams'))"
```

If `agentTeams` is not `True`, report: `[FAIL] agentTeams not enabled — team coordination disabled.`
If `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is not `"1"` in env section, report: `[FAIL] CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS not set — Agent Teams UI will not activate.`

If any [FAIL] appears (from verify.py or agentTeams check), tell the user to run:
```
python <root>/scripts/install.py
```
Then restart Claude Code.
