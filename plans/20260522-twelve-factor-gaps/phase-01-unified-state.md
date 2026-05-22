# Phase 1: Unified Workflow State

## Context

- [12-Factor #5](https://github.com/humanlayer/12-factor-agents): Unify Execution State and Business State
- Current state scattered across: `.claude/review-handoff.md`, `.claude/review-trigger.json`, `~/.claude/compact-snapshots/`, TaskList API, `.team/` directories

## Problem

No single source of truth for "where is this workflow". Recovery after crash/compact requires piecing together multiple files. Team coordination relies on implicit state (file existence) rather than explicit state machine.

## Architecture

### State File: `.claude/workflow-state.json`

```json
{
  "workflow_id": "impl-20260522-084800",
  "created_at": "2026-05-22T08:48:00Z",
  "updated_at": "2026-05-22T09:15:00Z",
  "phase": "implementing",
  "plan_ref": "plans/20260522-twelve-factor-gaps/phase-01-unified-state.md",
  "agents": [
    {
      "role": "implementer",
      "task": "Add workflow state lib",
      "status": "DONE",
      "started_at": "2026-05-22T08:50:00Z",
      "finished_at": "2026-05-22T09:10:00Z",
      "error": null
    },
    {
      "role": "code-reviewer",
      "task": "Review implementer output",
      "status": "in_progress",
      "started_at": "2026-05-22T09:12:00Z",
      "finished_at": null,
      "error": null
    }
  ],
  "execution": {
    "current_step": 3,
    "total_steps": 5,
    "retry_count": 0,
    "blocked_reason": null
  },
  "context": {
    "branch": "feat/unified-state",
    "files_modified": ["hooks/lib/workflow_state.py"],
    "test_status": "passing"
  }
}
```

### State Machine

```
init → planning → implementing → reviewing → testing → done
                      │                          │
                      ├── blocked ◄──────────────┤
                      │                          │
                      └── failed ◄───────────────┘
```

## Related Code Files

**Create:**
- `hooks/lib/workflow_state.py` — State read/write/transition library
- `tests/lib/test_workflow_state.py` — Unit tests

**Modify:**
- `hooks/lib/review_trigger.py:80` — `write_handoff()` → also update workflow state
- `hooks/lib/subagent_stop_gate.py:6` — `evaluate()` → update agent status in workflow state
- `hooks/lib/session_context.py:22` — `build_session_start_context()` → inject workflow state summary on resume

## Implementation Steps

### Step 1: Create `hooks/lib/workflow_state.py`

```python
# Core functions:
# - init_workflow(workflow_id, plan_ref) -> creates state file
# - get_state() -> reads current state (returns None if no active workflow)
# - transition(new_phase, **context) -> validates transition, updates state
# - register_agent(role, task) -> adds agent entry
# - update_agent(role, status, error=None) -> updates agent status
# - get_summary() -> one-line human-readable summary for context injection
```

Key design decisions:
- File lock via `fcntl.flock` (or `msvcrt.locking` on Windows) for concurrent agent writes
- Invalid transitions raise `WorkflowStateError` (not silent ignore)
- `get_summary()` returns max 3 lines — optimized for context window injection

### Step 2: Create tests

Test cases:
- Init → read back → verify fields
- Valid transition chain: init → planning → implementing → reviewing → done
- Invalid transition: init → done (should raise)
- Concurrent agent registration (2 agents, no corruption)
- `get_summary()` output format
- Graceful degrade when no state file exists

### Step 3: Integrate into `review_trigger.py`

At `write_handoff()` (~line 80):
- After writing review-handoff.md, call `update_agent("implementer", "DONE")`
- Call `transition("reviewing")`
- Keep existing review-handoff.md for backward compatibility

### Step 4: Integrate into `subagent_stop_gate.py`

At `evaluate()` (~line 6):
- On subagent completion, call `update_agent(role, status)` with extracted status
- On block (output too short), call `update_agent(role, "BLOCKED", error=reason)`

### Step 5: Integrate into `session_context.py`

At `build_session_start_context()` (~line 22):
- If workflow state exists, append `get_summary()` to context
- Summary format: `"Workflow {id}: {phase} | Step {n}/{total} | Last agent: {role} → {status}"`

## Todo

- [ ] Create `hooks/lib/workflow_state.py` with state machine
- [ ] Create `tests/lib/test_workflow_state.py`
- [ ] Integrate into `review_trigger.py`
- [ ] Integrate into `subagent_stop_gate.py`
- [ ] Integrate into `session_context.py`
- [ ] Run tests, verify backward compat

## Success Criteria

- Single `workflow-state.json` tracks entire workflow lifecycle
- Session resume shows workflow summary in first message
- Existing agents work unchanged (backward compat)
- All tests pass

## Risk

| Risk | Mitigation |
|------|-----------|
| File lock contention on Windows | Use `msvcrt.locking`, test on Windows |
| State file grows unbounded | Cap agent history at 20 entries, rotate |
| Breaking existing hooks | All integrations additive, wrapped in try/except |
