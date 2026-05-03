---
description: "Check that craftpowers is fully configured — hooks, agents, permissions, and hook smoke tests."
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

2. Fallback: `~/.claude/plugins/craftpowers`

3. If still not found, ask the user where craftpowers is installed.

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
