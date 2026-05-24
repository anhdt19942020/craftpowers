"""Tests for project stack injection into SessionStart context."""
from unittest.mock import patch

from hooks.lib.session_context import build_session_start_context


def test_stack_context_included(tmp_path):
    """When stack is detected, context block appears in session output."""
    with patch("hooks.lib.session_context.detect_stack", return_value=["python"]):
        with patch(
            "hooks.lib.session_context.format_stack_context",
            return_value="[project-stack: python]",
        ):
            ctx = build_session_start_context(str(tmp_path))
            assert "project-stack" in ctx


def test_no_stack_no_crash(tmp_path):
    """Empty directory should not crash stack detection."""
    ctx = build_session_start_context(str(tmp_path))
    assert "EXTREMELY_IMPORTANT" in ctx


def test_stack_block_absent_when_empty(tmp_path):
    """No stacks detected → no stack block in output."""
    with patch("hooks.lib.session_context.detect_stack", return_value=[]):
        ctx = build_session_start_context(str(tmp_path))
        assert "project-stack" not in ctx


def test_stack_error_doesnt_break_context(tmp_path):
    """Stack detection error must not break session context output."""
    with patch("hooks.lib.session_context.detect_stack", side_effect=RuntimeError("fail")):
        ctx = build_session_start_context(str(tmp_path))
        assert "EXTREMELY_IMPORTANT" in ctx
        assert "You have man" in ctx
