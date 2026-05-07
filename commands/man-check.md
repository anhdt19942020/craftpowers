---
description: "Check that mankit is fully configured — hooks, agents, permissions, and hook smoke tests."
---

Find the mankit root directory using this method (try in order, stop at first hit):

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
If any [FAIL] appears, tell the user to run:
```
python <root>/scripts/install.py
```
Then restart Claude Code.
