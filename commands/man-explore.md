---
description: "Route to the right exploration mode, then scan for files, patterns, and conventions. Read-only. Run before /man-plan."
---

## Step 1 — Route using research-playbook

Before dispatching, classify the user's request using the research-playbook decision tree:

- **Does the task need EXTERNAL info** (library docs, best practices, comparisons, unfamiliar domain)?
  → Dispatch `deep-researcher` (deep-researcher) — outward-facing research with cited sources.

- **Does the task need INTERNAL info** (where is X in our codebase, what conventions do we use, what files are touched)?
  → Dispatch `codebase-explorer` (codebase-explorer) — inward-facing repo scan.

- **Does the task need BOTH?**
  → Dispatch both in parallel. Combine reports before presenting to user.

If ambiguous, ask the user: "Do you need external research (docs/best-practices) or internal codebase scanning?"

## Step 2 — Dispatch

Pass the user's feature description (everything after `/man-explore`) as the input to the chosen agent(s).

## Step 3 — Report

When the agent(s) return:
1. Print the report verbatim — do not paraphrase, do not editorialize.
2. If using both agents, present external research first, then internal scan.
3. If the agent returned a "Questions for the planner" section with non-empty content, ask the user to answer those before invoking `/man-plan`.
4. Do NOT propose code changes. Do NOT edit files. Do NOT run tests. The output is for planning only.
