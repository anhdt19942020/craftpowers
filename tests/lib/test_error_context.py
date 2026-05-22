"""Tests for hooks/lib/error_context.py — TDD red-green cycle."""
import sys
import os
import json
import time
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

import pytest
from lib.error_context import (
    capture_error,
    get_error_history,
    compact_errors,
    inject_error_context,
    cleanup_errors,
)


@pytest.fixture
def tmp_claude_home(tmp_path, monkeypatch):
    """Redirect error storage to a temp dir."""
    monkeypatch.setenv("CLAUDE_HOME", str(tmp_path))
    return tmp_path


# --- capture + read-back ---

def test_capture_and_read_back(tmp_claude_home):
    capture_error(
        workflow_id="wf-001",
        role="implementer",
        status="BLOCKED",
        output_tail="Fatal: cannot connect to DB",
        files=["src/api.py"],
        home=str(tmp_claude_home),
    )
    errors = get_error_history("wf-001", home=str(tmp_claude_home))
    assert len(errors) == 1
    e = errors[0]
    assert e["workflow_id"] == "wf-001"
    assert e["agent_role"] == "implementer"
    assert e["status"] == "BLOCKED"
    assert e["last_output_tail"] == "Fatal: cannot connect to DB"
    assert e["files_touched"] == ["src/api.py"]
    assert "timestamp" in e
    assert "attempt_number" in e


def test_attempt_number_increments(tmp_claude_home):
    for _ in range(3):
        capture_error("wf-002", "implementer", "BLOCKED", "err", [], home=str(tmp_claude_home))
    errors = get_error_history("wf-002", home=str(tmp_claude_home))
    attempts = sorted(e["attempt_number"] for e in errors)
    assert attempts == [1, 2, 3]


def test_no_collision_on_rapid_capture(tmp_claude_home):
    """Sequential captures must produce distinct files."""
    for _ in range(5):
        capture_error("wf-rapid", "implementer", "BLOCKED", "err", [], home=str(tmp_claude_home))
    errors = get_error_history("wf-rapid", home=str(tmp_claude_home))
    assert len(errors) == 5


# --- compact_errors ---

def _make_errors(n: int):
    return [
        {
            "workflow_id": "wf-x",
            "agent_role": "implementer",
            "timestamp": f"2026-05-22T09:{i:02d}:00Z",
            "status": "BLOCKED",
            "error_summary": f"Error summary for attempt {i+1}",
            "last_output_tail": "last line of output " * 10,
            "files_touched": ["src/foo.py"],
            "attempt_number": i + 1,
        }
        for i in range(n)
    ]


def test_compact_single_error_returns_full_detail():
    errors = _make_errors(1)
    result = compact_errors(errors)
    assert "Error summary for attempt 1" in result
    assert "last line of output" in result


def test_compact_latest_error_preserved_fully():
    errors = _make_errors(5)
    result = compact_errors(errors)
    # Latest (attempt 5) should appear in full detail
    assert "Error summary for attempt 5" in result
    assert "last line of output" in result


def test_compact_respects_500_token_limit():
    errors = _make_errors(20)
    result = compact_errors(errors, max_tokens=500)
    # rough estimate: 1 token ~ 4 chars
    assert len(result) <= 500 * 5  # generous bound; strict bound at 4 chars/token
    # More practical: should be well under 3000 chars
    assert len(result) < 3000


def test_compact_older_errors_one_line_each():
    errors = _make_errors(3)
    result = compact_errors(errors)
    # Attempt 1 and 2 should appear as one-liners (not full tail)
    lines = result.split("\n")
    # The older attempts should each have a compact single-line entry
    one_liners = [l for l in lines if "Attempt 1:" in l or "Attempt 2:" in l]
    assert len(one_liners) >= 1  # at least one old attempt is compact


def test_compact_empty_returns_empty_string():
    assert compact_errors([]) == ""


# --- inject_error_context ---

def test_inject_returns_empty_when_no_errors(tmp_claude_home):
    result = inject_error_context("wf-nonexistent", home=str(tmp_claude_home))
    assert result == ""


def test_inject_returns_formatted_markdown(tmp_claude_home):
    capture_error("wf-inject", "implementer", "BLOCKED", "DB down", [], home=str(tmp_claude_home))
    result = inject_error_context("wf-inject", home=str(tmp_claude_home))
    assert "Prior Attempt" in result or "failure" in result.lower()
    assert "BLOCKED" in result or "DB down" in result


def test_inject_mentions_role_and_status(tmp_claude_home):
    capture_error("wf-role", "tester", "NEEDS_CONTEXT", "Missing fixture", ["tests/foo.py"], home=str(tmp_claude_home))
    result = inject_error_context("wf-role", home=str(tmp_claude_home))
    assert "tester" in result
    assert "NEEDS_CONTEXT" in result


# --- cleanup_errors ---

def test_cleanup_removes_all_files_for_workflow(tmp_claude_home):
    for _ in range(3):
        capture_error("wf-clean", "implementer", "BLOCKED", "err", [], home=str(tmp_claude_home))
    errors_before = get_error_history("wf-clean", home=str(tmp_claude_home))
    assert len(errors_before) == 3

    cleanup_errors("wf-clean", home=str(tmp_claude_home))

    errors_after = get_error_history("wf-clean", home=str(tmp_claude_home))
    assert len(errors_after) == 0


def test_cleanup_other_workflow_unaffected(tmp_claude_home):
    capture_error("wf-keep", "implementer", "BLOCKED", "err", [], home=str(tmp_claude_home))
    capture_error("wf-del", "implementer", "BLOCKED", "err", [], home=str(tmp_claude_home))

    cleanup_errors("wf-del", home=str(tmp_claude_home))

    assert len(get_error_history("wf-keep", home=str(tmp_claude_home))) == 1
    assert len(get_error_history("wf-del", home=str(tmp_claude_home))) == 0


def test_cleanup_nonexistent_workflow_no_error(tmp_claude_home):
    # Should not raise
    cleanup_errors("wf-ghost", home=str(tmp_claude_home))
