"""Tests for hooks/lib/teammate_idle_handler.py"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.teammate_idle_handler import handle_idle

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _task(id_, title, status="pending", deps=None, role_tags=None, priority="medium"):
    return {
        "id": id_,
        "title": title,
        "status": status,
        "dependencies": deps or [],
        "role_tags": role_tags or [],
        "priority": priority,
        "description": f"Description for {title}",
    }


def _data(agent_role="implementer", tasks=None):
    return {
        "agent_id": "agent-1",
        "agent_role": agent_role,
        "team_name": "test-team",
        "tasks": tasks or [],
    }


# ---------------------------------------------------------------------------
# No workflow state (empty tasks list)
# ---------------------------------------------------------------------------

def test_no_tasks_returns_noop():
    result = handle_idle(_data(tasks=[]))
    assert result["action"] == "noop"


# ---------------------------------------------------------------------------
# No unblocked tasks
# ---------------------------------------------------------------------------

def test_all_tasks_in_progress_returns_noop():
    tasks = [_task(1, "Task A", status="in_progress")]
    result = handle_idle(_data(tasks=tasks))
    assert result["action"] == "noop"


def test_all_tasks_completed_returns_noop():
    tasks = [_task(1, "Task A", status="completed")]
    result = handle_idle(_data(tasks=tasks))
    assert result["action"] == "noop"


def test_pending_task_with_incomplete_dep_returns_noop():
    tasks = [
        _task(1, "Task A", status="in_progress"),
        _task(2, "Task B", status="pending", deps=[1]),
    ]
    result = handle_idle(_data(tasks=tasks))
    assert result["action"] == "noop"


# ---------------------------------------------------------------------------
# Unblocked tasks exist → inject
# ---------------------------------------------------------------------------

def test_unblocked_task_returns_inject():
    tasks = [_task(1, "Task A", status="pending")]
    result = handle_idle(_data(tasks=tasks))
    assert result["action"] == "inject_tasks"


def test_inject_message_contains_task_title():
    tasks = [_task(1, "Build the widget", status="pending")]
    result = handle_idle(_data(tasks=tasks))
    assert "Build the widget" in result["message"]


def test_inject_result_contains_tasks_list():
    tasks = [_task(1, "Task A", status="pending")]
    result = handle_idle(_data(tasks=tasks))
    assert isinstance(result["tasks"], list)
    assert len(result["tasks"]) == 1


def test_pending_task_with_completed_dep_is_unblocked():
    tasks = [
        _task(1, "Task A", status="completed"),
        _task(2, "Task B", status="pending", deps=[1]),
    ]
    result = handle_idle(_data(tasks=tasks))
    assert result["action"] == "inject_tasks"
    assert result["tasks"][0]["id"] == 2


# ---------------------------------------------------------------------------
# Role filtering
# ---------------------------------------------------------------------------

def test_implementer_gets_coding_tasks():
    tasks = [
        _task(1, "Write code", status="pending", role_tags=["implementer"]),
        _task(2, "Write tests", status="pending", role_tags=["tester"]),
    ]
    result = handle_idle(_data(agent_role="implementer", tasks=tasks))
    assert result["action"] == "inject_tasks"
    ids = [t["id"] for t in result["tasks"]]
    assert 1 in ids
    assert 2 not in ids


def test_tester_gets_test_tasks():
    tasks = [
        _task(1, "Write code", status="pending", role_tags=["implementer"]),
        _task(2, "Write tests", status="pending", role_tags=["tester"]),
    ]
    result = handle_idle(_data(agent_role="tester", tasks=tasks))
    assert result["action"] == "inject_tasks"
    ids = [t["id"] for t in result["tasks"]]
    assert 2 in ids
    assert 1 not in ids


def test_tasks_with_no_role_tags_match_any_role():
    tasks = [_task(1, "Generic task", status="pending", role_tags=[])]
    result = handle_idle(_data(agent_role="reviewer", tasks=tasks))
    assert result["action"] == "inject_tasks"


# ---------------------------------------------------------------------------
# Priority ordering — lowest ID first
# ---------------------------------------------------------------------------

def test_lowest_id_first():
    tasks = [
        _task(3, "Task C", status="pending"),
        _task(1, "Task A", status="pending"),
        _task(2, "Task B", status="pending"),
    ]
    result = handle_idle(_data(tasks=tasks))
    ids = [t["id"] for t in result["tasks"]]
    assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# Max 3 tasks injected
# ---------------------------------------------------------------------------

def test_max_three_tasks_injected():
    tasks = [_task(i, f"Task {i}", status="pending") for i in range(1, 7)]
    result = handle_idle(_data(tasks=tasks))
    assert len(result["tasks"]) <= 3


# ---------------------------------------------------------------------------
# Fail-open: bad input → noop
# ---------------------------------------------------------------------------

def test_missing_keys_returns_noop():
    result = handle_idle({})
    assert result["action"] == "noop"


def test_none_tasks_returns_noop():
    result = handle_idle({"agent_id": "x", "agent_role": "implementer", "team_name": "t", "tasks": None})
    assert result["action"] == "noop"
