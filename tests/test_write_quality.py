"""Tests for write-time quality enforcement hook."""
from unittest.mock import patch

from hooks.lib.write_quality import _is_config_file, evaluate


def test_disabled_by_default():
    result = evaluate("Write", "test.py")
    assert result["decision"] == "ok"
    assert result["messages"] == []


def test_config_file_blocked():
    with patch("hooks.lib.write_quality.get_config", return_value={
        "write_quality": {"enabled": True, "block_config_edit": True}
    }):
        result = evaluate("Write", ".eslintrc.json")
        assert result["decision"] == "block"
        assert "Blocked" in result["reason"]


def test_config_file_not_blocked_when_disabled():
    with patch("hooks.lib.write_quality.get_config", return_value={
        "write_quality": {"enabled": True, "block_config_edit": False}
    }):
        with patch("hooks.lib.write_quality.detect_stack", return_value=[]):
            result = evaluate("Write", ".eslintrc.json")
            assert result["decision"] == "ok"


def test_is_config_file_positive():
    assert _is_config_file(".eslintrc.json") is True
    assert _is_config_file("biome.json") is True
    assert _is_config_file("ruff.toml") is True
    assert _is_config_file(".prettierrc") is True


def test_is_config_file_negative():
    assert _is_config_file("app.py") is False
    assert _is_config_file("README.md") is False
    assert _is_config_file("main.go") is False


def test_non_code_file_skipped():
    with patch("hooks.lib.write_quality.get_config", return_value={
        "write_quality": {"enabled": True}
    }):
        result = evaluate("Write", "README.md")
        assert result["decision"] == "ok"


def test_unknown_extension_skipped():
    with patch("hooks.lib.write_quality.get_config", return_value={
        "write_quality": {"enabled": True}
    }):
        result = evaluate("Write", "Makefile")
        assert result["decision"] == "ok"


def test_empty_file_path_skipped():
    with patch("hooks.lib.write_quality.get_config", return_value={
        "write_quality": {"enabled": True}
    }):
        result = evaluate("Write", "")
        assert result["decision"] == "ok"


def test_stack_mismatch_skipped():
    """Python file but no python in detected stack → skip."""
    with patch("hooks.lib.write_quality.get_config", return_value={
        "write_quality": {"enabled": True, "block_config_edit": False, "auto_format": True, "auto_lint": True}
    }):
        with patch("hooks.lib.write_quality.detect_stack", return_value=["node"]):
            result = evaluate("Write", "app.py")
            assert result["decision"] == "ok"
