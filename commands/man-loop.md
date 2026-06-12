---
description: "Manage a tracked agentic loop with iteration checkpoints. Tracks pass/fail history and supports resume. Subcommands: start, status."
---

Invoke the `loop-checkpoint` skill now.

- If the user ran `/man-loop start <task>`: tell the skill the intent is "start" and pass the task description.
- If the user ran `/man-loop status [args]`: tell the skill the intent is "status" and pass any arguments (e.g., `record pass`, `record fail`).

Pass the subcommand and any trailing arguments to the skill unchanged.
