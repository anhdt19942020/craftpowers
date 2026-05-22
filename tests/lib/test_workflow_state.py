"""Tests for hooks/lib/workflow_state.py"""
import sys, os
import json
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.workflow_state import (
    init_workflow,
    get_state,
    transition,
    register_agent,
    update_agent,
    get_summary,
    WorkflowStateError,
)


@pytest.fixture
def state_dir(tmp_path):
    """Provide a temp dir for .claude/workflow-state.json."""
    return str(tmp_path)


def test_init_creates_state_file(state_dir):
    init_workflow("test-wf-001", "plans/test/phase-01.md", state_dir=state_dir)
    state_file = Path(state_dir) / "workflow-state.json"
    assert state_file.exists()


def test_init_fields(state_dir):
    init_workflow("test-wf-001", "plans/test/phase-01.md", state_dir=state_dir)
    state = get_state(state_dir=state_dir)
    assert state["workflow_id"] == "test-wf-001"
    assert state["plan_ref"] == "plans/test/phase-01.md"
    assert state["phase"] == "init"
    assert "created_at" in state
    assert "updated_at" in state
    assert state["agents"] == []
    assert state["execution"]["current_step"] == 0
    assert state["execution"]["retry_count"] == 0
    assert state["execution"]["blocked_reason"] is None


def test_get_state_returns_none_when_no_file(state_dir):
    result = get_state(state_dir=state_dir)
    assert result is None


def test_valid_transition_chain(state_dir):
    init_workflow("test-wf-002", "plans/test.md", state_dir=state_dir)
    transition("planning", state_dir=state_dir)
    assert get_state(state_dir=state_dir)["phase"] == "planning"
    transition("implementing", state_dir=state_dir)
    assert get_state(state_dir=state_dir)["phase"] == "implementing"
    transition("reviewing", state_dir=state_dir)
    assert get_state(state_dir=state_dir)["phase"] == "reviewing"
    transition("done", state_dir=state_dir)
    assert get_state(state_dir=state_dir)["phase"] == "done"


def test_invalid_transition_raises(state_dir):
    init_workflow("test-wf-003", "plans/test.md", state_dir=state_dir)
    with pytest.raises(WorkflowStateError):
        transition("done", state_dir=state_dir)


def test_register_agent(state_dir):
    init_workflow("test-wf-004", "plans/test.md", state_dir=state_dir)
    register_agent("implementer", "Add workflow state lib", state_dir=state_dir)
    state = get_state(state_dir=state_dir)
    assert len(state["agents"]) == 1
    agent = state["agents"][0]
    assert agent["role"] == "implementer"
    assert agent["task"] == "Add workflow state lib"
    assert agent["status"] == "in_progress"
    assert "started_at" in agent
    assert agent["finished_at"] is None
    assert agent["error"] is None


def test_update_agent(state_dir):
    init_workflow("test-wf-005", "plans/test.md", state_dir=state_dir)
    register_agent("implementer", "Do stuff", state_dir=state_dir)
    update_agent("implementer", "DONE", state_dir=state_dir)
    state = get_state(state_dir=state_dir)
    agent = state["agents"][0]
    assert agent["status"] == "DONE"
    assert agent["finished_at"] is not None


def test_update_agent_with_error(state_dir):
    init_workflow("test-wf-006", "plans/test.md", state_dir=state_dir)
    register_agent("implementer", "Do stuff", state_dir=state_dir)
    update_agent("implementer", "BLOCKED", error="output too short", state_dir=state_dir)
    state = get_state(state_dir=state_dir)
    agent = state["agents"][0]
    assert agent["status"] == "BLOCKED"
    assert agent["error"] == "output too short"


def test_get_summary_format(state_dir):
    init_workflow("test-wf-007", "plans/test.md", state_dir=state_dir)
    transition("implementing", state_dir=state_dir)
    register_agent("implementer", "Do stuff", state_dir=state_dir)
    update_agent("implementer", "DONE", state_dir=state_dir)
    summary = get_summary(state_dir=state_dir)
    assert "test-wf-007" in summary
    assert "implementing" in summary
    assert "implementer" in summary
    assert "DONE" in summary
    # Must be max 3 lines
    lines = [l for l in summary.splitlines() if l.strip()]
    assert len(lines) <= 3


def test_get_summary_returns_empty_when_no_state(state_dir):
    result = get_summary(state_dir=state_dir)
    assert result == ""


def test_transition_to_blocked(state_dir):
    init_workflow("test-wf-008", "plans/test.md", state_dir=state_dir)
    transition("planning", state_dir=state_dir)
    transition("blocked", state_dir=state_dir)
    state = get_state(state_dir=state_dir)
    assert state["phase"] == "blocked"


def test_transition_to_failed(state_dir):
    init_workflow("test-wf-009", "plans/test.md", state_dir=state_dir)
    transition("planning", state_dir=state_dir)
    transition("implementing", state_dir=state_dir)
    transition("failed", state_dir=state_dir)
    state = get_state(state_dir=state_dir)
    assert state["phase"] == "failed"
