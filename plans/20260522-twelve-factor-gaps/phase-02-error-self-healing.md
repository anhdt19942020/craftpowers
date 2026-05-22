# Phase 2: Error Self-Healing

## Context

- [12-Factor #9](https://github.com/humanlayer/12-factor-agents): Compact Errors into Context Window
- Current: `subagent_stop_gate.py` blocks short output + missing Status, but retry is blind — next agent gets no error context
- Current: `stop_failure.py` logs rate-limit/auth/billing errors but doesn't feed them back

## Problem

When subagent fails (BLOCKED, crash, short output), the orchestrator retries or dispatches next agent **without injecting the failure context**. New agent repeats same mistake. No self-healing loop.

## Architecture

### Error Context Flow

```
Agent A fails
    │
    ▼
SubagentStop hook captures:
  - error message / last output
  - status (BLOCKED / short output / crash)
  - files touched
  - stack trace (if available)
    │
    ▼
Write to `.claude/agent-errors/{workflow_id}/{role}-{timestamp}.json`
    │
    ▼
Next agent dispatch:
  - Hook reads error history for this workflow
  - Compacts into ≤500 token summary
  - Injects as "Prior Attempt Context" in session start
    │
    ▼
New agent reads error context → adjusts approach
```

### Error File Format

```json
{
  "workflow_id": "impl-20260522-084800",
  "agent_role": "implementer",
  "timestamp": "2026-05-22T09:10:00Z",
  "status": "BLOCKED",
  "error_summary": "Test timeout on integration suite — jest --forceExit did not help",
  "last_output_tail": "FATAL: Cannot connect to test database...",
  "files_touched": ["src/api/routes.ts", "tests/api/routes.test.ts"],
  "attempt_number": 2
}
```

## Related Code Files

**Create:**
- `hooks/lib/error_context.py` — Error capture, storage, compaction, injection
- `tests/lib/test_error_context.py` — Unit tests

**Modify:**
- `hooks/lib/subagent_stop_gate.py:6` — On block/failure → call `capture_error()`
- `hooks/lib/session_context.py:22` — On session start → call `inject_error_context()` if errors exist for active workflow

## Implementation Steps

### Step 1: Create `hooks/lib/error_context.py`

```python
# Core functions:
# - capture_error(workflow_id, role, status, output_tail, files) -> writes error JSON
# - get_error_history(workflow_id) -> list of past errors, sorted by time
# - compact_errors(errors, max_tokens=500) -> compressed summary string
# - inject_error_context(workflow_id) -> returns formatted string for context injection
# - cleanup_errors(workflow_id) -> remove error files after workflow completes
```

Compaction strategy:
- Latest error: full detail (summary + tail + files)
- Older errors: one line each ("Attempt {n}: {role} → {status}: {summary}")
- Cap at 500 tokens total — truncate oldest first

### Step 2: Create tests

Test cases:
- Capture → read back → verify fields
- Multiple errors → compact respects 500 token limit
- Compaction prioritizes latest error (full detail preserved)
- `inject_error_context()` returns empty string when no errors
- `cleanup_errors()` removes all files for workflow
- Error file naming: no collision on rapid sequential failures

### Step 3: Integrate into `subagent_stop_gate.py`

At `evaluate()` when blocking (output too short or status missing):
```python
from hooks.lib.error_context import capture_error
from hooks.lib.workflow_state import get_state

state = get_state()
if state:
    capture_error(
        workflow_id=state["workflow_id"],
        role=agent_role,
        status="BLOCKED",
        output_tail=last_output[-500:],
        files=[]
    )
```

Also capture when status is explicitly BLOCKED or NEEDS_CONTEXT (not just gate failures).

### Step 4: Integrate into `session_context.py`

At `build_session_start_context()`:
```python
from hooks.lib.error_context import inject_error_context
from hooks.lib.workflow_state import get_state

state = get_state()
if state:
    error_ctx = inject_error_context(state["workflow_id"])
    if error_ctx:
        context += f"\n\n## Prior Attempt Context\n{error_ctx}"
```

Injection format:
```
## Prior Attempt Context
⚠️ Previous agent(s) failed on this workflow. Read before starting.

**Latest failure** (attempt 2, implementer):
Status: BLOCKED
Error: Test timeout — Cannot connect to test database
Files touched: src/api/routes.ts, tests/api/routes.test.ts

**Earlier:** Attempt 1: implementer → BLOCKED: Missing env var DB_URL
```

### Step 5: Auto-cleanup

In workflow state `transition("done")`:
- Call `cleanup_errors(workflow_id)` — remove error files
- Retain last workflow's errors for 24h (debugging), then prune

## Todo

- [ ] Create `hooks/lib/error_context.py`
- [ ] Create `tests/lib/test_error_context.py`
- [ ] Integrate into `subagent_stop_gate.py`
- [ ] Integrate into `session_context.py`
- [ ] Add cleanup call in workflow state transition
- [ ] Test end-to-end: fail agent → redispatch → verify error context injected

## Success Criteria

- Failed agent's error context appears in next agent's session start
- Error summary ≤500 tokens (context budget safe)
- Agents demonstrate adjusted approach after reading error context
- No error files leak after workflow completion
- Existing agents unaffected when no errors exist

## Risk

| Risk | Mitigation |
|------|-----------|
| Error context misleads next agent | Cap at 500 tokens, prioritize actionable info |
| Error dir grows unbounded | Auto-cleanup on workflow done + 24h TTL prune |
| Circular failure (agent keeps failing same way) | `attempt_number` tracked — orchestrator can escalate after 3 attempts |
