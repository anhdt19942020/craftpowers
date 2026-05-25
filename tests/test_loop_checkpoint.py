"""Tests for loop checkpoint module."""
import json
import pytest
from pathlib import Path
from hooks.lib.loop_checkpoint import (
    start_loop,
    record_iteration,
    get_checkpoint,
    get_status_summary,
    clear_checkpoint,
)


def test_start_loop_creates_file(tmp_path):
    cp = start_loop("loop-1", "fix failing tests", state_dir=str(tmp_path))
    assert (tmp_path / "loop-checkpoint.json").exists()
    assert cp["loop_id"] == "loop-1"
    assert cp["task"] == "fix failing tests"
    assert cp["status"] == "running"
    assert cp["current_iteration"] == 0
    assert cp["iterations"] == []


def test_start_loop_overwrites_existing(tmp_path):
    start_loop("old-loop", "old task", state_dir=str(tmp_path))
    start_loop("new-loop", "new task", state_dir=str(tmp_path))
    cp = get_checkpoint(state_dir=str(tmp_path))
    assert cp["loop_id"] == "new-loop"


def test_get_checkpoint_returns_none_when_missing(tmp_path):
    assert get_checkpoint(state_dir=str(tmp_path)) is None


def test_get_checkpoint_raises_on_corrupt_file(tmp_path):
    (tmp_path / "loop-checkpoint.json").write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="corrupt"):
        get_checkpoint(state_dir=str(tmp_path))


def test_record_iteration_fail(tmp_path):
    start_loop("l1", "run tests", state_dir=str(tmp_path))
    cp = record_iteration("fail", notes="5 tests failing", state_dir=str(tmp_path))
    assert cp["current_iteration"] == 1
    assert cp["iterations"][0]["result"] == "fail"
    assert cp["status"] == "running"


def test_record_iteration_pass_marks_done(tmp_path):
    start_loop("l1", "run tests", state_dir=str(tmp_path))
    record_iteration("fail", state_dir=str(tmp_path))
    cp = record_iteration("pass", state_dir=str(tmp_path))
    assert cp["status"] == "done"
    assert cp["current_iteration"] == 2


def test_record_iteration_max_iterations(tmp_path):
    start_loop("l1", "task", max_iterations=2, state_dir=str(tmp_path))
    record_iteration("fail", state_dir=str(tmp_path))
    cp = record_iteration("fail", state_dir=str(tmp_path))
    assert cp["status"] == "max_iterations_reached"


def test_record_iteration_raises_without_start(tmp_path):
    with pytest.raises(FileNotFoundError):
        record_iteration("pass", state_dir=str(tmp_path))


def test_get_status_summary(tmp_path):
    start_loop("l1", "fix bug", state_dir=str(tmp_path))
    record_iteration("fail", state_dir=str(tmp_path))
    record_iteration("pass", state_dir=str(tmp_path))
    summary = get_status_summary(state_dir=str(tmp_path))
    assert "l1" in summary
    assert "Pass: 1" in summary
    assert "Fail: 1" in summary


def test_get_status_summary_empty_when_no_checkpoint(tmp_path):
    assert get_status_summary(state_dir=str(tmp_path)) == ""


def test_clear_checkpoint(tmp_path):
    start_loop("l1", "task", state_dir=str(tmp_path))
    clear_checkpoint(state_dir=str(tmp_path))
    assert get_checkpoint(state_dir=str(tmp_path)) is None


def test_clear_checkpoint_noop_when_missing(tmp_path):
    clear_checkpoint(state_dir=str(tmp_path))  # should not raise


def test_atomic_write_no_partial_read(tmp_path):
    start_loop("l1", "task", state_dir=str(tmp_path))
    cp_file = tmp_path / "loop-checkpoint.json"
    raw = json.loads(cp_file.read_text())
    assert "loop_id" in raw
    assert "iterations" in raw
