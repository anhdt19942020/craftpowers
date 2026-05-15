---
description: "View mankit skill usage telemetry — top skills, never-used skills, context cost."
---

## man-stats — Skill Usage Telemetry

Read `~/.claude/mankit-telemetry-summary.json` and `~/.claude/mankit-telemetry.jsonl` to produce a usage report.

### Step 1 — Load summary

```python
import json, os
from pathlib import Path

summary_path = Path.home() / ".claude" / "mankit-telemetry-summary.json"
if not summary_path.exists():
    print("No telemetry recorded yet. Use /man-plan, /man-ship, etc. to start collecting data.")
else:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    print(json.dumps(summary, indent=2))
```

If the file does not exist, tell the user: "No telemetry recorded yet. Skill invocations via `/man-*` commands are logged automatically."

### Step 2 — List all known skills

Enumerate skills from the mankit root (find via `CLAUDE_PLUGIN_ROOT` env var or common paths):

```python
import os
from pathlib import Path

root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", ""))
if not root.exists():
    # Try common locations
    for candidate in [Path.home() / ".claude" / "plugins" / "craftpowers",
                      Path("D:/Projects/craftpowers")]:
        if (candidate / "skills").exists():
            root = candidate
            break

skills_dir = root / "skills"
all_skills = sorted(d.name for d in skills_dir.iterdir() if d.is_dir()) if skills_dir.exists() else []
print("Total skills:", len(all_skills))
print(all_skills)
```

### Step 3 — Report

Produce a formatted report with three sections:

**Top skills by usage** — show all skills with invocation count > 0, sorted descending.

Example:
```
Top skills by usage:
  man-plan        12x
  brainstorming    8x
  writing-plans    5x
```

**Never-used skills** — skills in `all_skills` that have zero invocations in the summary.

Example:
```
Never-used skills (29 of 42):
  adversarial-design, agent-teams, api-and-interface-design, ...
```

**Context cost estimate** — for each skill that HAS a `skills/<name>/SKILL.md`, estimate its size:

```python
for skill in all_skills:
    skill_file = root / "skills" / skill / "SKILL.md"
    if skill_file.exists():
        lines = sum(1 for _ in skill_file.open(encoding="utf-8", errors="ignore"))
        # rough token estimate: 1 line ≈ 15 tokens
        tokens = lines * 15
        print(f"  {skill}: ~{lines} lines (~{tokens} tokens)")
```

Show total estimated token cost of ALL loaded skills combined.

### Step 4 — Suggest unused skills to disable

If any skills have never been used AND have been available for multiple sessions:

> "Consider disabling these skills to save context: [list]. You can do this via `man-check` or by editing your settings."

Only suggest disabling if the telemetry JSONL has more than 5 entries (i.e., at least some usage has been recorded — not a fresh install).

```python
jsonl_path = Path.home() / ".claude" / "mankit-telemetry.jsonl"
entry_count = 0
if jsonl_path.exists():
    with jsonl_path.open(encoding="utf-8", errors="ignore") as f:
        entry_count = sum(1 for line in f if line.strip())
print("Total logged invocations:", entry_count)
```

Present the full report in a clean, readable format. No JSON dumps in the final output — format it as human-readable text.
