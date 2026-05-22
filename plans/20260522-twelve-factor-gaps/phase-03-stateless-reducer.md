# Phase 3: Stateless Reducer Pattern

## Context

- [12-Factor #12](https://github.com/humanlayer/12-factor-agents): Make Your Agent a Stateless Reducer
- Depends on: Phase 1 (unified state) + Phase 2 (error context)
- Current: Agent state lives in conversation context (implicit, non-recoverable)

## Problem

Agents are stateful conversations. If session crashes mid-workflow, state is lost. Cannot replay, checkpoint, or inspect agent decisions. Cannot restart from arbitrary point.

## Design Philosophy

**Not a rewrite.** Mankit agents run inside Claude Code harness — we can't replace the core loop. Instead: externalize key decision points as checkpoints in workflow state. Agent becomes "mostly stateless" — reads state file, does work, writes new state. Not pure reducer, but close enough for practical benefits.

## Architecture

### Checkpoint Pattern

```
┌─────────────────────────────────────────┐
│ Agent Invocation                         │
│                                          │
│  1. Read workflow-state.json             │
│  2. Read error-context (if any)          │
│  3. Determine: what step am I on?        │
│  4. Execute step                         │
│  5. Write updated workflow-state.json    │
│  6. Report status                        │
└─────────────────────────────────────────┘
```

### State Transitions as Events

Each state change logged as event in workflow state:

```json
{
  "events": [
    {"ts": "09:00:00", "type": "workflow_init", "data": {"plan": "phase-01"}},
    {"ts": "09:01:00", "type": "agent_start", "data": {"role": "implementer", "task": "..."}},
    {"ts": "09:10:00", "type": "agent_done", "data": {"role": "implementer", "status": "DONE"}},
    {"ts": "09:10:01", "type": "transition", "data": {"from": "implementing", "to": "reviewing"}},
    {"ts": "09:11:00", "type": "agent_start", "data": {"role": "code-reviewer"}},
    {"ts": "09:15:00", "type": "error", "data": {"role": "code-reviewer", "error": "..."}},
    {"ts": "09:15:01", "type": "agent_retry", "data": {"role": "code-reviewer", "attempt": 2}}
  ]
}
```

### Replay Capability

From event log, any workflow can be:
- **Inspected**: "What happened at step 3?"
- **Resumed**: "Continue from last checkpoint"
- **Debugged**: "Why did reviewer fail after implementer succeeded?"

## Related Code Files

**Create:**
- `hooks/lib/workflow_events.py` — Event logging, replay, checkpoint queries
- `tests/lib/test_workflow_events.py` — Unit tests

**Modify:**
- `hooks/lib/workflow_state.py` (Phase 1) — Add `events` array, append on every `transition()` and `update_agent()`
- `hooks/lib/session_context.py` — On resume, inject last 5 events as "Recent Workflow History"
- `agents/implementer.md` — Add instruction: "Read workflow state before starting. Write checkpoint after each significant step."

## Implementation Steps

### Step 1: Create `hooks/lib/workflow_events.py`

```python
# Core functions:
# - append_event(workflow_id, event_type, data) -> appends to events array
# - get_events(workflow_id, last_n=None, event_type=None) -> filtered events
# - get_last_checkpoint(workflow_id) -> most recent agent_done or transition event
# - summarize_events(events, max_lines=5) -> compact human-readable summary
# - replay_from(workflow_id, checkpoint_ts) -> returns state at that point
```

Event types:
- `workflow_init` — workflow created
- `agent_start` — agent dispatched
- `agent_done` — agent completed (any status)
- `transition` — phase change
- `error` — error captured
- `agent_retry` — retry dispatched
- `checkpoint` — explicit save point (agent writes mid-work)

### Step 2: Create tests

Test cases:
- Append events → read back in order
- Filter by event_type
- `get_last_checkpoint()` skips non-checkpoint events
- `summarize_events()` respects max_lines
- `replay_from()` reconstructs state at given timestamp
- Empty events → graceful defaults

### Step 3: Wire into `workflow_state.py`

Every `transition()` and `update_agent()` call → auto-append event:

```python
def transition(new_phase, **context):
    # ... existing validation ...
    append_event(state["workflow_id"], "transition", {
        "from": state["phase"],
        "to": new_phase,
        **context
    })
    state["phase"] = new_phase
    _write_state(state)
```

### Step 4: Update `session_context.py`

On resume with active workflow:
```
## Recent Workflow History
09:00 workflow_init → phase-01
09:01 agent_start → implementer
09:10 agent_done → implementer: DONE
09:10 transition → implementing → reviewing
09:11 agent_start → code-reviewer (attempt 2, prior error: timeout)
```

Max 5 events. Gives agent instant orientation without reading full history.

### Step 5: Update `implementer.md`

Add to discipline section:
```markdown
## State Awareness
- On start: read `.claude/workflow-state.json` if exists — know your position in workflow
- After each significant step (file created, test passed, refactor done): 
  workflow checkpoint via status update
- On completion: report status to workflow state before final message
```

### Step 6: Add `man-replay` command (optional, stretch)

```bash
# Show workflow event timeline
/man-replay                    # current workflow
/man-replay <workflow-id>      # specific workflow
/man-replay --from <timestamp> # resume from checkpoint
```

## Todo

- [ ] Create `hooks/lib/workflow_events.py`
- [ ] Create `tests/lib/test_workflow_events.py`
- [ ] Wire events into `workflow_state.py` transitions
- [ ] Update `session_context.py` — inject recent events on resume
- [ ] Update `agents/implementer.md` — state awareness instructions
- [ ] (Stretch) Create `commands/man-replay.md`

## Success Criteria

- Every workflow produces event log
- Session resume shows last 5 events
- Can answer "what happened in this workflow?" from event log alone
- Implementer reads workflow state before starting work
- Events cap at reasonable size (prune after 100 events per workflow)

## Risk

| Risk | Mitigation |
|------|-----------|
| Event log bloats state file | Separate events into own file if >100 entries |
| Agents ignore state awareness instructions | Enforce via hook — warn if implementer doesn't read state |
| Replay from checkpoint is imperfect (side effects not captured) | Document limitation — replay = orientation, not time travel |
| Over-engineering — pure reducer not achievable in Claude harness | Explicitly "mostly stateless" — pragmatic, not purist |
