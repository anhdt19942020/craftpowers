---
description: "Debug and fix a bug, test failure, or unexpected behavior. Invokes the systematic-debugging skill, then auto-logs to journal."
---

Invoke the `systematic-debugging` skill now.

After the bug is resolved (root cause identified, fix verified):

1. Dispatch the `journal-writer` agent with a concise summary of:
   - The bug (symptom)
   - Root cause (why it happened)
   - What approaches were tried before the fix worked
   - Resolution (final fix, file paths)
   - Lesson (what to remember next time)
2. Print the journal file path returned by the agent.
3. Tell the user: "Logged to <path>. Edit if you want to refine the lesson."

If the bug is **not** resolved (skill returned blocked / user gave up): still dispatch `journal-writer` but mark the entry as "still open" in the Resolution field. A failed debug session is the most valuable kind of journal entry.

Never skip the journal step. If user explicitly says "skip journal", honor that — but ask once before skipping.
