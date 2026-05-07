---
description: "Scan the codebase for files, patterns, and conventions touched by a feature. Read-only. Run before /man-plan."
---

Dispatch the `codebase-explorer` agent. Pass the user's feature description (everything after `/man-explore`) as the input.

When the agent returns:
1. Print the report verbatim — do not paraphrase, do not editorialize.
2. If the agent returned a "Questions for the planner" section with non-empty content, ask the user to answer those before invoking `/man-plan`.
3. Do NOT propose code changes. Do NOT edit files. Do NOT run tests. The output is for planning only.
