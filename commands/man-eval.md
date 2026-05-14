---
description: "Run a human-driven A/B eval for a skill. Loads fixtures from evals/<skill-name>/, prints paste-ready eval cards, collects pass/fail interactively, writes results file."
---

Run the eval harness for the given skill.

## Step 1 — Identify skill name

The skill name is everything after `/man-eval`. Example: `/man-eval engineering-principles` → skill name is `engineering-principles`.

If no skill name is provided, list available skills that have fixtures:

```python
import os
from pathlib import Path
evals_dir = Path("evals")
dirs = [d.name for d in evals_dir.iterdir() if d.is_dir() and list(d.glob("*.json"))]
print("Available evals:", dirs)
```

## Step 2 — Run the harness

```bash
python scripts/eval.py <skill-name>
```

To compare against a baseline git ref:

```bash
python scripts/eval.py <skill-name> --baseline <git-ref>
```

The harness will:
1. Print a paste-ready eval card for each fixture (skill content + prompt + signal hints)
2. Prompt you to mark each fixture **pass** or **fail** after pasting into Claude
3. Print a summary and write results to `evals/<skill-name>/results-<timestamp>.md`

## Step 3 — Report results

After the run completes, display:
- Pass rate
- Per-fixture pass/fail table
- Path to the results file

If the results file exists, read and display it inline.
