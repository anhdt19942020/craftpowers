---
description: "Quick surgical fix — 1-2 files, no plan. For typo, rename, single-function tweak. Auto-verifies, refuses on scope creep."
---

Dispatch the `quick-fix` agent. Pass the user's task description (everything after `/man-quick`) as input.

When the agent returns:

1. Print the receipt verbatim.
2. If verify **FAILED**: do NOT commit. Tell the user: "Verify failed. Fix the failure or escalate to `/man-fix`."
3. If verify **PASSED**: ask the user "Commit?" — wait for confirmation before staging/committing.
4. If verify **N/A**: tell the user "No verify command available. Review the diff manually before committing."
5. If the agent **refused** (scope too large or vague): print refusal verbatim and suggest the correct tier (`/man-fix` for debug, `/man-plan` for multi-file).

Never expand scope. Never call `/man-plan` automatically. If the user pushes back on a refusal, restate the cap — escalation is the user's choice.
