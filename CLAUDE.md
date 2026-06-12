# mankit — Developer Guide

**mankit** is a personal Claude Code plugin (name: `man`) at `D:/projects/craftpowers`. Provides skills, agents, hooks, and commands for structured software development.

## Repo layout

```
skills/       — skill markdown files (~57 dirs)
agents/       — subagent definitions (13)
commands/     — slash command files (18)
hooks/        — Python hook scripts + profiles
scripts/      — version bump, install, eval utilities
tests/        — pytest suite for hooks/lib/
```

## Versioning

**Always bump version with every commit that changes behavior.** `man-update` compares version numbers to detect updates.

Version lives in 5 files — **always use the script, never edit manually:**

```bash
bash scripts/bump-version.sh <new-version>   # bump all 5 files
bash scripts/bump-version.sh --check         # detect drift
```

- Patch (`x.y.Z`): bug fixes, doc tweaks, small skill changes
- Minor (`x.Y.0`): new skills, new agents, new commands, new features

Bump in the same commit as the code change. Never a separate "chore: bump" commit.

> **Windows/no-jq fallback:** bump manually across: `package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`.

## Agent dispatch

| Task | `subagent_type` |
|------|----------------|
| Scout / explore | `codebase-explorer` |
| Architect / design | `architect` |
| Implement | `implementer` |
| Debug | `debugger` |
| Code review | `code-reviewer` |
| Security review | `secure-reviewer` |
| Quick fix (1-2 files) | `quick-fix` |
| Tests | `test-engineer` |
| Docs | `doc-writer` |
| Release prep | `release-prep` |
| Journal | `journal-writer` |
| Deep research | `deep-researcher` |
| Automation test | `automation-tester` |

Role → file mapping in `agents/roles.json`.

## Statusline (footer)

Auto-configured by `scripts/install.py`. Re-run if missing:

```bash
python scripts/install.py
```
