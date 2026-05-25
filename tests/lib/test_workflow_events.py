"""Tests for hooks/lib/workflow_events.py"""
import sys
import os
import json
import time
import tempfile
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.workflow_events import (
    append_event,
    get_events,
    get_last_checkpoint,
    summarize_events,
    replay_from,
)
from lib.workflow_state import init_workflow


@pytest.fixture
def state_dir(tmp_path):
    """Provide a temp dir with an initialized workflow."""
    return str(tmp_path)


@pytest.fixture
def workflow_id(state_dir):
    """Initialize a workflow and return its ID."""
    init_workflow("test-wf-events", "plans/test/phase-01.md", state_dir=state_dir)
    return "test-wf-events"


# ---------------------------------------------------------------------------
# append_event / get_events — basic round-trip
# ---------------------------------------------------------------------------

def test_append_and_read_events_in_order(workflow_id, state_dir):
    append_event(workflow_id, "agent_start", {"role": "planner"}, state_dir=state_dir)
    time.sleep(0.01)
    append_event(workflow_id, "agent_done", {"role": "planner", "status": "DONE"}, state_dir=state_dir)

    events = get_events(workflow_id, state_dir=state_dir)
    assert len(events) == 2
    assert events[0]["type"] == "agent_start"
    assert events[1]["type"] == "agent_done"
    # Timestamps must be sequential (or equal within same second)
    assert events[0]["ts"] <= events[1]["ts"]


def test_event_has_required_fields(workflow_id, state_dir):
    append_event(workflow_id, "transition", {"from": "init", "to": "planning"}, state_dir=state_dir)
    events = get_events(workflow_id, state_dir=state_dir)
    assert len(events) == 1
    evt = events[0]
    assert "ts" in evt
    assert "type" in evt
    assert "data" in evt
    assert evt["type"] == "transition"
    assert evt["data"] == {"from": "init", "to": "planning"}


def test_filter_by_event_type(workflow_id, state_dir):
    append_event(workflow_id, "agent_start", {"role": "planner"}, state_dir=state_dir)
    append_event(workflow_id, "transition", {"from": "init", "to": "planning"}, state_dir=state_dir)
    append_event(workflow_id, "agent_done", {"role": "planner", "status": "DONE"}, state_dir=state_dir)

    transitions = get_events(workflow_id, event_type="transition", state_dir=state_dir)
    assert len(transitions) == 1
    assert transitions[0]["type"] == "transition"


def test_get_events_last_n(workflow_id, state_dir):
    for i in range(5):
        append_event(workflow_id, "agent_start", {"role": f"agent-{i}"}, state_dir=state_dir)

    events = get_events(workflow_id, last_n=3, state_dir=state_dir)
    assert len(events) == 3
    # last_n returns the most recent N
    assert events[-1]["data"]["role"] == "agent-4"


# ---------------------------------------------------------------------------
# get_last_checkpoint
# ---------------------------------------------------------------------------

def test_get_last_checkpoint_returns_most_recent_eligible(workflow_id, state_dir):
    append_event(workflow_id, "agent_start", {"role": "planner"}, state_dir=state_dir)
    append_event(workflow_id, "agent_done", {"role": "planner", "status": "DONE"}, state_dir=state_dir)
    append_event(workflow_id, "transition", {"from": "planning", "to": "implementing"}, state_dir=state_dir)

    cp = get_last_checkpoint(workflow_id, state_dir=state_dir)
    assert cp is not None
    # transition is later than agent_done, so it wins
    assert cp["type"] == "transition"


def test_get_last_checkpoint_skips_non_checkpoint_events(workflow_id, state_dir):
    append_event(workflow_id, "agent_start", {"role": "planner"}, state_dir=state_dir)
    append_event(workflow_id, "error", {"msg": "oops"}, state_dir=state_dir)
    append_event(workflow_id, "workflow_init", {"plan": "phase-01"}, state_dir=state_dir)

    cp = get_last_checkpoint(workflow_id, state_dir=state_dir)
    # None of the above qualify as checkpoints
    assert cp is None


def test_get_last_checkpoint_recognizes_checkpoint_event_type(workflow_id, state_dir):
    append_event(workflow_id, "checkpoint", {"note": "mid-task save"}, state_dir=state_dir)

    cp = get_last_checkpoint(workflow_id, state_dir=state_dir)
    assert cp is not None
    assert cp["type"] == "checkpoint"


# ---------------------------------------------------------------------------
# summarize_events
# ---------------------------------------------------------------------------

def test_summarize_events_respects_max_lines(workflow_id, state_dir):
    for i in range(10):
        append_event(workflow_id, "agent_done", {"role": f"agent-{i}"}, state_dir=state_dir)

    events = get_events(workflow_id, state_dir=state_dir)
    summary = summarize_events(events, max_lines=3)
    lines = [l for l in summary.strip().split("\n") if l.strip()]
    assert len(lines) <= 3


def test_summarize_events_format(workflow_id, state_dir):
    append_event(workflow_id, "transition", {"from": "init", "to": "planning"}, state_dir=state_dir)
    events = get_events(workflow_id, state_dir=state_dir)
    summary = summarize_events(events)
    # Format: "HH:MM {event_type} → {detail}"
    assert "transition" in summary
    assert "→" in summary
    # Should include HH:MM time prefix
    import re
    assert re.search(r'\d{2}:\d{2}', summary)


def test_summarize_events_empty_returns_empty_string():
    result = summarize_events([])
    assert result == ""


# ---------------------------------------------------------------------------
# replay_from
# ---------------------------------------------------------------------------

def test_replay_from_returns_events_from_checkpoint(workflow_id, state_dir):
    append_event(workflow_id, "agent_start", {"role": "planner"}, state_dir=state_dir)
    time.sleep(0.01)
    append_event(workflow_id, "transition", {"from": "init", "to": "planning"}, state_dir=state_dir)
    time.sleep(0.01)
    append_event(workflow_id, "agent_done", {"role": "planner", "status": "DONE"}, state_dir=state_dir)

    all_events = get_events(workflow_id, state_dir=state_dir)
    checkpoint_ts = all_events[1]["ts"]  # transition event

    replayed = replay_from(workflow_id, checkpoint_ts, state_dir=state_dir)
    assert isinstance(replayed, dict)
    events_after = replayed.get("events", [])
    # Should include transition and agent_done (events >= checkpoint_ts)
    assert len(events_after) >= 1
    types = [e["type"] for e in events_after]
    assert "agent_done" in types


def test_replay_from_empty_when_no_events(workflow_id, state_dir):
    result = replay_from(workflow_id, "2099-01-01T00:00:00Z", state_dir=state_dir)
    assert result["events"] == []


# ---------------------------------------------------------------------------
# Empty/graceful defaults
# ---------------------------------------------------------------------------

def test_get_events_empty_workflow(workflow_id, state_dir):
    events = get_events(workflow_id, state_dir=state_dir)
    assert events == []


def test_get_last_checkpoint_empty_workflow(workflow_id, state_dir):
    cp = get_last_checkpoint(workflow_id, state_dir=state_dir)
    assert cp is None


def test_get_events_nonexistent_workflow(state_dir):
    events = get_events("nonexistent-wf", state_dir=state_dir)
    assert events == []


# ---------------------------------------------------------------------------
# Cap at 100 events — oldest pruned
# ---------------------------------------------------------------------------

def test_events_capped_at_100(workflow_id, state_dir):
    for i in range(110):
        append_event(workflow_id, "agent_start", {"seq": i}, state_dir=state_dir)

    events = get_events(workflow_id, state_dir=state_dir)
    assert len(events) == 100
    # Oldest (seq 0-9) pruned, newest (seq 10-109) kept
    seqs = [e["data"]["seq"] for e in events]
    assert 0 not in seqs
    assert 109 in seqs
