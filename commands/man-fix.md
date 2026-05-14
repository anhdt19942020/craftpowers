---
description: "Debug and fix a bug, test failure, or unexpected behavior. Dispatches bang-thong (debugger agent)."
---

Dispatch the `debugger` agent (`subagent_type: "man:bang-thong"`). Pass the user's bug description (everything after `/man-fix`) as input, including any error messages, file paths, or reproduction steps.

When the agent returns:

1. Print the diagnosis and fix summary verbatim.
2. If the agent **found and fixed the bug**:
   - Show which files changed and what the root cause was.
   - Run tests if applicable, ask user to confirm before committing.
3. If the agent **could not reproduce** the bug:
   - Report what was investigated and what evidence was found.
   - Ask the user for more context (logs, reproduction steps, env).
4. If the bug **spans too many systems** for a single agent:
   - Suggest `/man-plan` to break into an implementation plan.
   - Or dispatch parallel `man:bang-thong` agents per subsystem.

Never expand scope beyond what the user described. Root cause first, fix second.
