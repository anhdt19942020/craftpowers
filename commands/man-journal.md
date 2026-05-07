---
description: "Log a failure, setback, or lesson to today's journal. Brutally honest, append-only. Use after bug fix, deploy fail, or abandoned approach."
---

Dispatch the `journal-writer` agent. Pass the user's input (everything after `/man-journal`) as the incident description.

When the agent returns:

1. Print the file path written and the 1-line summary verbatim.
2. Do NOT commit the journal file automatically — journals are working notes, user decides whether to track in git.
3. If user has no input after `/man-journal`, ask: "What setback/failure should I log? (concrete: error, root cause, what you tried)"

The journal lives at `docs/mankit/journal/YYYY-MM-DD.md`. One file per day. Append-only.

Never sanitize entries. Never push back on harsh self-assessment — that is the point of the journal.
