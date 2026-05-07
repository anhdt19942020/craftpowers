---
description: "Pre-deploy audit: env vars, migrations, breaking changes, changelog draft. Run after tests pass and before /man-ship."
---

Dispatch the `release-prep` agent.

When the agent returns:
1. Print the Pre-Ship Report verbatim.
2. If the report has any items in the **Block** section, tell the user: "Fix block items before /man-ship." Do NOT proceed to ship.
3. If only **Warning** items appear, summarize them and ask the user whether to proceed or address first.
4. If the report is `No stack detected — nothing to audit.`, tell the user: "No deploy artifacts detected. /man-ship is fine to run."

Never deploy. Never push. Never tag. The agent audits; the user decides.
