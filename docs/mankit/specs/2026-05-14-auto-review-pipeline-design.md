# Auto-Review Pipeline — Design Spec
**Date:** 2026-05-14  
**Status:** Draft — pending implementation

---

## Problem

Mankit's review agents (`phap-chinh`, `tu-ma-y`) exist but are opt-in. The orchestrator must manually dispatch them after `trieu-van` finishes. In practice this means review is skipped when:
- Orchestrator forgets
- Skill doesn't explicitly remind
- Task is "small" and review feels optional

Security review (`tu-ma-y`) has no integration point in the default workflow at all.

---

## Solution

Use `SubagentStop`-equivalent hooks in `trieu-van`'s frontmatter to **guarantee** review dispatch after every implementation. Reviewers receive only `git diff` — fresh context, no implementation bias.

---

## Architecture

### Three layers of change

**Layer 1 — trieu-van.md frontmatter**

Add `hooks` block:
```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "python hooks/security_gate.py"
  PostToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "python hooks/lib/lint_on_edit.py"
  Stop:
    - matcher: ""
      hooks:
        - type: command
          command: "python hooks/lib/review_trigger.py"
```

**Layer 2 — review_trigger.py (new)**

Responsibilities:
1. Run `git diff HEAD~1` to get changes
2. Write diff + metadata to `.claude/review-handoff.md`
3. Run `security_detector.py` on diff — returns boolean
4. Dispatch `phap-chinh` with diff context (always)
5. If security detected: dispatch `tu-ma-y` with diff context (parallel)
6. Write combined findings to `.claude/review-findings.md`

**Layer 3 — reviewer agent frontmatter**

Both `phap-chinh.md` and `tu-ma-y.md` get:
```yaml
tools: Read, Grep, Glob
hooks:
  PreToolUse:
    - matcher: "Write|Edit|NotebookEdit"
      hooks:
        - type: command
          command: "echo 'reviewers are read-only' >&2 && exit 2"
```

---

## Data Flow

```
trieu-van finishes
    │
    ▼ [Stop hook]
review_trigger.py
    ├── git diff HEAD~1 → .claude/review-handoff.md
    ├── security_detector.py(diff)
    │       ├── TRUE  → dispatch tu-ma-y(diff) [parallel]
    │       └── FALSE → skip tu-ma-y
    └── dispatch phap-chinh(diff) [always, parallel]
    
phap-chinh              tu-ma-y (conditional)
    │                       │
    ▼                       ▼
.claude/review-findings-phap-chinh.md
.claude/review-findings-tu-ma-y.md
    │
    ▼
orchestrator reads findings → decides: approve / send back to trieu-van
```

---

## Security Detection Keywords

`security_detector.py` scans diff for:
```python
SENSITIVE = [
    "auth", "password", "passwd", "token", "secret",
    "crypto", "encrypt", "decrypt", "hash", "salt",
    "sql", "query", "execute", "cursor",
    "input", "request.body", "req.body", "form",
    "upload", "file_path", "filepath",
    "permission", "role", "admin",
    "session", "cookie", "jwt", "oauth",
    "subprocess", "exec", "eval", "os.system"
]
```

Match on added lines only (`+` prefix in diff). Returns `True` if any keyword found.

---

## Files Changed

| File | Action | Notes |
|------|--------|-------|
| `agents/trieu-van.md` | Edit | Add `hooks` block |
| `agents/phap-chinh.md` | Edit | Add `tools`, `hooks` block |
| `agents/tu-ma-y.md` | Edit | Add `tools`, `hooks` block |
| `hooks/lib/review_trigger.py` | Create | Main orchestration script |
| `hooks/lib/security_detector.py` | Create | Keyword scan on diff |

**Not touched:** `skills/`, `commands/`, `settings.json`, other agents, existing hook scripts.

---

## Constraints

- Reviewers **cannot** write or edit files — enforced by hard-block hook (exit 2)
- `review_trigger.py` skips dispatch if `git diff HEAD~1` is empty (no changes made)
- Parallel dispatch via Python subprocess or sequential if subprocess unavailable
- Findings written to `.claude/` (gitignored) — not committed
- `trieu-van` Stop hook fires whether task succeeded or failed — review always runs

---

## Non-Goals

- `hoang-trung` (test-engineer) NOT auto-triggered — remains manual opt-in
- `luu-bi` (release-prep) NOT auto-triggered — only before ship
- No synthesis agent — orchestrator reads findings directly
- No retry loop — if review finds issues, orchestrator decides next step

---

## Open Questions (resolved)

- **Reviewer context:** git diff only (fresh) — not conversation history ✅
- **Parallel vs sequential:** parallel (both dispatch simultaneously) ✅
- **Security trigger:** keyword detection on added lines only ✅
- **Gate strictness:** findings written to file, orchestrator decides — not hard block ✅
