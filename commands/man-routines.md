---
description: "List and manage mankit bundled cloud routines."
---

## Usage

```
/man-routines list
/man-routines enable <name>
/man-routines disable <name>
```

## `list` — Show available routines

List all routine definitions in `routines/`:

```
ls routines/*.md
```

For each file, print:
- **Name:** filename without extension
- **Schedule:** value of the `schedule` frontmatter field
- **Description:** value of the `description` frontmatter field

Output format:

```
Bundled routines in routines/:

  skill-rot-scan   (weekly Mon 9am)   Weekly scan for stale model IDs, broken links, removed providers
  dep-tick         (weekly Mon 10am)  Major dependency version bump check
  pr-babysitter    (daily 9am)        Nudge stale non-draft PRs with no approval

Run `/man-routines enable <name>` for scheduling instructions.
```

## `enable <name>` — Schedule a routine

Print instructions for scheduling the named routine via Claude Code:

1. Confirm the routine file exists at `routines/<name>.md`.
2. Read the `schedule` and `description` fields from its frontmatter.
3. Print:

```
To schedule <name>:

1. Open https://claude.ai/code/routines
2. Click "New Routine"
3. Set:
   - Name:        <name>
   - Trigger:     <schedule>   (cron)
   - Repository:  <current repo remote URL>
   - Prompt:      Paste the contents of routines/<name>.md
4. Save and enable the routine.

The routine prompt is at: routines/<name>.md
```

To get the current repo remote URL:
```
git remote get-url origin
```

## `disable <name>` — Unschedule a routine

Print instructions for removing the named routine:

1. Confirm the routine file exists at `routines/<name>.md`.
2. Print:

```
To disable <name>:

1. Open https://claude.ai/code/routines
2. Find the routine named "<name>"
3. Click the three-dot menu → "Disable" or "Delete"

The local definition at routines/<name>.md is unchanged.
```

## Notes

- This command provides instructions only. Actual scheduling is managed at claude.ai/code/routines.
- Routine definitions live in `routines/` — edit them there to change behavior.
- See `skills/cloud-routines/SKILL.md` for background on how cloud routines work.
