---
description: "End-to-end feature implementation: scout → plan → implement → review → test → finalize. One command, full workflow with hard gates."
---

Load skill `man:cook`. Pass the user's input (everything after `/man-cook`) as the task description.

Detect mode from input flags or intent (see Smart Intent Detection in skill). Default: interactive.

If input is a path to a plan file → skip scout + requirements, start at Step 4 (Implement).

Follow the pipeline strictly: Scout → Requirements → Plan → Implement → Review → Test → Finalize. Each hard gate MUST pass before proceeding.

**Scope guard:** `/man-cook` is for NEW FEATURES. Redirect:
- Bug? → `/man-debug`
- 1-2 file tweak? → `/man-quick`
- Plan only? → `/man-plan`
- Ship existing work? → `/man-ship`
