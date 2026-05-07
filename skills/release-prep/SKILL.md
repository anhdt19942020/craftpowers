---
name: release-prep
description: Pre-deploy audit. Detects stack (Node / Python / migrations / Docker), loads matching rules, runs checklist, drafts changelog from git diff. Read-only. Returns a Pre-Ship Report with pass/warning/block sections. Run after tests pass and before /man-ship.
---

# Release Prep

Audit the current branch for deploy-time issues that automated tests do not catch:
new env vars without `.env.example` updates, lock-file drift, destructive
migrations, breaking API changes, missing image tag bumps.

## Workflow

1. **Detect stack(s).** Run these checks in parallel and load each matching rule
   file from `rules/`:

   | Signal | Rule file |
   |--------|-----------|
   | `package.json` exists | `rules/node.md` |
   | `requirements.txt` or `pyproject.toml` exists | `rules/python.md` |
   | `prisma/`, `drizzle/`, `migrations/`, `alembic/` exists | `rules/migrations.md` |
   | `Dockerfile` or `docker-compose.yml` exists | `rules/docker.md` |

   Multiple stacks can apply — load all that match.

2. **Run each rule's checklist** against the current branch's diff vs the main
   branch (`git diff main..HEAD`).

3. **Draft a changelog** from `git log main..HEAD --oneline`, grouped by
   conventional-commit type (feat / fix / chore / docs / refactor / test / build).

4. **Aggregate the report.**

## Output format

Return exactly this:

```
## Pre-Ship Report

### Pass (n)
- <check>

### Warning (n)
- <check> — <why this is a warning, not a block>

### Block (n)
- <check> — <how to fix>

### Changelog draft
**feat:**
- <line>
**fix:**
- <line>
...
```

## Hard refusals

- Never push, deploy, merge, tag, or release.
- Never edit files. Audit only.
- If asked to fix a block item, respond: "Out of scope — release-prep audits, it does not edit. Run the fix yourself or dispatch a different agent."

## Notes for the dispatcher

- The `release-prep` agent is the canonical entry point. It loads this skill and the matching rule files.
- If no stack signals match, return a single-line report: `No stack detected — nothing to audit.`
