# Environment Variable Resolution

## Overview

All Claude Code plugin skills use a centralized environment variable resolver (`~/.claude/scripts/resolve_env.py`) for consistent configuration management across project-local and user-global scopes.

## Priority Hierarchy

Environment variables are resolved in this order (highest to lowest):

1. **process.env** — Runtime environment variables (HIGHEST)
2. **PROJECT/.claude/skills/\<skill\>/.env** — Project skill-specific overrides
3. **PROJECT/.claude/skills/.env** — Project shared across all skills
4. **PROJECT/.claude/.env** — Project global defaults
5. **~/.claude/skills/\<skill\>/.env** — User skill-specific overrides
6. **~/.claude/skills/.env** — User shared across all skills
7. **~/.claude/.env** — User global defaults (LOWEST)

## Benefits

### Consistency
All skills use the same resolution logic — no divergent implementations.

### Flexibility
Supports both project-local and user-global configurations:
- **Project-local** (`.claude/` in project root): version-controlled, team-shared defaults
- **User-global** (`~/.claude/`): personal overrides, API keys, machine-specific config

### Debuggability
Built-in tools for troubleshooting:
```bash
# Show hierarchy for specific skill
python ~/.claude/scripts/resolve_env.py --show-hierarchy --skill <skill-name>

# Find where variable is defined
python ~/.claude/scripts/resolve_env.py MY_API_KEY --find-all

# Resolve with verbose output
python ~/.claude/scripts/resolve_env.py MY_API_KEY --skill <skill-name> --verbose
```

### Maintainability
Single source of truth — update once, affects all skills.

## Usage

### CLI

```bash
# Resolve variable for specific skill
python ~/.claude/scripts/resolve_env.py MY_API_KEY --skill my-skill

# With default value
python ~/.claude/scripts/resolve_env.py API_KEY --default fallback-value

# Export format for shell
eval $(python ~/.claude/scripts/resolve_env.py MY_API_KEY --export)

# Show hierarchy
python ~/.claude/scripts/resolve_env.py --show-hierarchy --skill my-skill
```

### Python API

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.claude' / 'scripts'))
from resolve_env import resolve_env

api_key = resolve_env('MY_API_KEY', skill='my-skill')

if not api_key:
    print("Error: MY_API_KEY not found")
    sys.exit(1)
```

### Integration in Skills

Skills use the centralized resolver with a fallback for backward compatibility:

```python
sys.path.insert(0, str(Path.home() / '.claude' / 'scripts'))
try:
    from resolve_env import resolve_env
    CENTRALIZED_RESOLVER_AVAILABLE = True
except ImportError:
    CENTRALIZED_RESOLVER_AVAILABLE = False

def find_api_key() -> Optional[str]:
    if CENTRALIZED_RESOLVER_AVAILABLE:
        return resolve_env('MY_API_KEY', skill='my-skill')
    # Fallback logic...
```

## Common Scenarios

### Scenario 1: Global default
```bash
# ~/.claude/.env
MY_API_KEY=personal-key
```
All skills use `personal-key` by default.

### Scenario 2: Project override
```bash
# ~/.claude/.env
MY_API_KEY=personal-key

# PROJECT/.claude/.env
MY_API_KEY=team-shared-key
```
When working in PROJECT, skills use `team-shared-key`.

### Scenario 3: Skill-specific override
```bash
# ~/.claude/.env
MY_API_KEY=default-key

# ~/.claude/skills/my-skill/.env
MY_API_KEY=high-quota-key
```
`my-skill` uses `high-quota-key`; other skills use `default-key`.

### Scenario 4: Runtime override
```bash
export MY_API_KEY=test-key
python script.py
```
All skills use `test-key` regardless of config files.

## Debugging

### Check hierarchy
```bash
python ~/.claude/scripts/resolve_env.py --show-hierarchy --skill my-skill
```

Output shows which config files exist (`✓`) and their priority:
```
Environment Variable Resolution Hierarchy
============================================================

Priority order (highest to lowest):
1. process.env - Runtime environment
2. Project skill-specific (my-skill) ✗ /path/to/project/.claude/skills/my-skill/.env
3. Project skills shared          ✓ /path/to/project/.claude/skills/.env
4. Project global                 ✓ /path/to/project/.claude/.env
5. User skill-specific (my-skill) ✗ /Users/you/.claude/skills/my-skill/.env
6. User skills shared             ✓ /Users/you/.claude/skills/.env
7. User global                    ✓ /Users/you/.claude/.env
```

### Find all locations
```bash
python ~/.claude/scripts/resolve_env.py MY_API_KEY --find-all
```

Shows everywhere the variable is defined and which wins:
```
Variable 'MY_API_KEY' found in 2 location(s):
============================================================

2. Project global
   Path: /path/to/project/.claude/.env
   Value: sk-proj-...FJI

7. User global
   Path: /Users/you/.claude/.env
   Value: sk-proj-...XYZ

============================================================
✓ Resolved value (highest priority): sk-proj-...FJI
```

### Verbose resolution
```bash
python ~/.claude/scripts/resolve_env.py MY_API_KEY --skill my-skill --verbose
```

Shows step-by-step where the resolver looks:
```
✗ MY_API_KEY not in: Runtime environment
✗ MY_API_KEY not in: Project skill-specific (my-skill) (file not found)
✓ MY_API_KEY found in: Project skills shared
  Path: /path/to/project/.claude/skills/.env
```

## Migration Guide

### Existing skills

1. Keep existing `find_api_key()` as fallback.
2. Add centralized resolver import:
```python
sys.path.insert(0, str(Path.home() / '.claude' / 'scripts'))
try:
    from resolve_env import resolve_env
    CENTRALIZED_RESOLVER_AVAILABLE = True
except ImportError:
    CENTRALIZED_RESOLVER_AVAILABLE = False
```
3. Update resolution logic to call resolver first, fall through to legacy logic.

### New skills

Use the centralized resolver directly — no fallback needed:
```python
from resolve_env import resolve_env

api_key = resolve_env('API_KEY_NAME', skill='my-skill')
```

## Config File Locations

| Scope | Path | Use case |
|-------|------|----------|
| User global | `~/.claude/.env` | Personal API keys, machine defaults |
| User skill | `~/.claude/skills/<skill>/.env` | Per-skill personal overrides |
| User shared | `~/.claude/skills/.env` | Shared across all skills, user scope |
| Project global | `PROJECT/.claude/.env` | Team defaults, committed to repo |
| Project skill | `PROJECT/.claude/skills/<skill>/.env` | Per-skill project overrides |

## Quick Reference

```bash
# Debug a variable
python ~/.claude/scripts/resolve_env.py VAR_NAME --verbose

# See full hierarchy for a skill
python ~/.claude/scripts/resolve_env.py --show-hierarchy --skill my-skill

# Find all definitions
python ~/.claude/scripts/resolve_env.py VAR_NAME --find-all
```
