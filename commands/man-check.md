---
description: "Check that craftpowers is fully configured — hooks, agents, permissions, and hook smoke tests."
---

Find the craftpowers directory by checking these locations in order:
1. `~/.claude/plugins/craftpowers`
2. Ask the user where they installed it if not found

Then run `python scripts/verify.py` inside that directory and report the full output.

Every check has a [PASS] or [FAIL] status. If anything fails, tell the user to run:
```
python scripts/install.py
```
Then restart Claude Code.
