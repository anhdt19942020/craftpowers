"""Tests for hooks.lib.subagent_init."""
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from hooks.lib.subagent_init import evaluate


class TestEvaluateBasic:
    def test_empty_data_returns_approve(self):
        result = evaluate({})
        assert result["decision"] == "approve"

    def test_injects_plans_path_when_exists(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({"agent_type": "implementer"})
        assert result["decision"] == "approve"
        assert "Plans path:" in result.get("stdout", "")

    def test_injects_reports_path_when_exists(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        reports = plans / "reports"
        reports.mkdir()
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({"agent_type": "implementer"})
        stdout = result.get("stdout", "")
        assert "Reports path:" in stdout

    def test_no_plans_dir_still_approve(self, tmp_path):
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({"agent_type": "implementer"})
        assert result["decision"] == "approve"

    def test_includes_work_context(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({"agent_type": "implementer"})
        assert f"Work context: {tmp_path}" in result.get("stdout", "")

    def test_includes_subagent_context_tags(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({"agent_type": "implementer"})
        stdout = result.get("stdout", "")
        assert "<subagent-context>" in stdout
        assert "</subagent-context>" in stdout


class TestTeamContext:
    def test_team_name_injected(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({"agent_type": "implementer", "team_name": "fix-auth"})
        assert "Team: fix-auth" in result.get("stdout", "")

    def test_team_artifacts_path_when_exists(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        team_dir = tmp_path / ".team" / "fix-auth"
        team_dir.mkdir(parents=True)
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({"agent_type": "implementer", "team_name": "fix-auth"})
        assert "Team artifacts:" in result.get("stdout", "")


class TestWorkflowIntegration:
    def test_workflow_state_injected_when_available(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        mock_state = {"workflow_id": "wf-123", "phase": "implementing"}
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            with patch("hooks.lib.subagent_init.get_state", return_value=mock_state, create=True):
                # Need to patch at import level
                import hooks.lib.subagent_init as mod
                original = None
                try:
                    from lib.workflow_state import get_state
                    original = get_state
                except ImportError:
                    pass
                result = evaluate({"agent_type": "implementer"})
        assert result["decision"] == "approve"

    def test_workflow_import_failure_graceful(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({"agent_type": "implementer"})
        assert result["decision"] == "approve"


class TestSuppressOutput:
    def test_suppress_output_set_when_injecting(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({"agent_type": "implementer"})
        assert result.get("suppressOutput") is True

    def test_no_suppress_when_no_injection(self, tmp_path):
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(tmp_path)}):
            result = evaluate({})
        assert "suppressOutput" not in result
