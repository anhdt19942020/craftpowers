---
name: hookify
description: Create, list, and manage declarative hook rules using markdown files. Each rule is a .claude/hookify.*.md file with YAML frontmatter. MUST BE USED when: user wants to block or warn on specific commands/file patterns without editing Python hooks.
---

# Hookify — Declarative Hook Rules

Create hook rules as simple markdown files instead of editing JSON config.

## Usage

```
/man-hookify list              # Show all active hookify rules
/man-hookify create <name>     # Create a new rule interactively
/man-hookify delete <name>     # Remove a rule
/man-hookify test <name>       # Test a rule against sample input
```

## Creating Rules

### Interactive (recommended)

Use `/man-hookify create <name>` — will ask for event, action, and pattern via AskUserQuestion.

### Manual

Create `.claude/hookify.<name>.md`:

```markdown
---
event: bash
action: block
pattern: "rm -rf /"
---
Block dangerous recursive delete at root.
```

### Fields

| Field | Required | Values |
|-------|----------|--------|
| event | Yes | `bash`, `edit`, `write`, `read` |
| action | Yes | `block`, `warn` |
| pattern | Yes | Regex pattern to match against command/content |

### Examples

**Block force push:**
```markdown
---
event: bash
action: block
pattern: "git push.*--force"
---
Prevent force pushes. Use --force-with-lease instead.
```

**Warn on TODO comments:**
```markdown
---
event: write
action: warn
pattern: "TODO|FIXME|HACK"
---
TODO/FIXME/HACK detected in written file. Consider resolving before commit.
```

**Block production database access:**
```markdown
---
event: bash
action: block
pattern: "psql.*production|prod.*psql"
---
Direct production database access blocked. Use read replica or staging.
```

## Rule Locations

Rules are discovered from:
1. `{project}/.claude/hookify.*.md` — project-scoped rules
2. `~/.claude/hookify.*.md` — global rules (future)

Project rules take precedence over global rules with the same name.

## How It Works

Rules are loaded by `hooks/lib/hookify_loader.py` and evaluated by the hook dispatcher
on each `bash`, `edit`, `write`, or `read` event. Rules are additive — they run after
the built-in security and privacy gates.
