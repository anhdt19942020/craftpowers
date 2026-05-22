"""Tests for hooks.lib.simplify_gate."""
from __future__ import annotations
import subprocess
from unittest.mock import patch, MagicMock

from hooks.lib.simplify_gate import evaluate


def _mock_git_stat(lines: int):
    """Return a mock CompletedProcess for git diff --stat HEAD with N changed lines."""
    # git diff --stat output ends with a summary line like:
    # " 3 files changed, 120 insertions(+), 5 deletions(-)"
    output = f" 3 files changed, {lines} insertions(+), 0 deletions(-)\n"
    return MagicMock(stdout=output, returncode=0)


# --- Non-trigger messages ---

def test_non_trigger_returns_allow():
    result = evaluate("please review this code")
    assert result["decision"] == "allow"


def test_question_returns_allow():
    result = evaluate("what does this function do?")
    assert result["decision"] == "allow"


# --- Trigger detection ---

def test_commit_trigger_small_diff_allow():
    with patch("subprocess.run", return_value=_mock_git_stat(50)):
        result = evaluate("commit the changes")
    assert result["decision"] == "allow"
    assert result["diff_lines"] == 50


def test_commit_trigger_600_lines_warn():
    with patch("subprocess.run", return_value=_mock_git_stat(600)):
        result = evaluate("commit my work")
    assert result["decision"] == "warn"
    assert result["diff_lines"] == 600
    assert "600" in result["reason"]


def test_commit_trigger_1200_lines_block():
    with patch("subprocess.run", return_value=_mock_git_stat(1200)):
        result = evaluate("commit everything")
    assert result["decision"] == "block"
    assert result["diff_lines"] == 1200
    assert "1200" in result["reason"]


def test_push_trigger_block():
    with patch("subprocess.run", return_value=_mock_git_stat(1100)):
        result = evaluate("push to origin main")
    assert result["decision"] == "block"


def test_ship_trigger_warn():
    with patch("subprocess.run", return_value=_mock_git_stat(750)):
        result = evaluate("ship it!")
    assert result["decision"] == "warn"


def test_merge_trigger_block():
    with patch("subprocess.run", return_value=_mock_git_stat(1500)):
        result = evaluate("merge the branch now")
    assert result["decision"] == "block"


def test_man_ship_slash_command():
    with patch("subprocess.run", return_value=_mock_git_stat(200)):
        result = evaluate("/man-ship")
    assert result["decision"] == "allow"
    assert result["diff_lines"] == 200


def test_man_ship_slash_command_large():
    with patch("subprocess.run", return_value=_mock_git_stat(1001)):
        result = evaluate("/man-ship")
    assert result["decision"] == "block"


# --- Fail-open on timeout ---

def test_git_timeout_returns_allow():
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
        result = evaluate("commit the changes")
    assert result["decision"] == "allow"


def test_git_error_returns_allow():
    with patch("subprocess.run", side_effect=Exception("git not found")):
        result = evaluate("push to remote")
    assert result["decision"] == "allow"
