"""Tests for hooks.lib.project_config — per-project .man.json config loader."""
import json
import os
import sys
import tempfile

import pytest

# Ensure repo root on path
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from hooks.lib.project_config import (
    get_config,
    get_hook_config,
    is_hook_enabled,
    reset_cache,
    _deep_merge,
    _DEFAULTS,
)


@pytest.fixture(autouse=True)
def _clean_cache():
    """Reset config cache before each test."""
    reset_cache()
    yield
    reset_cache()


@pytest.fixture
def config_dir(tmp_path, monkeypatch):
    """Create temp dir with .man.json and set as plugin root."""
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_path))
    return tmp_path


def _write_config(config_dir, data):
    path = config_dir / ".man.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class TestGetConfig:
    def test_defaults_when_no_file(self, config_dir):
        cfg = get_config()
        assert cfg["coding_level"] == 3
        assert cfg["hooks"]["naming_gate"] is True
        assert cfg["hooks"]["simplify_gate"] == {"warn": 500, "block": 1000}

    def test_merge_with_user_config(self, config_dir):
        _write_config(config_dir, {"coding_level": 5, "test_command": "pytest -x"})
        cfg = get_config()
        assert cfg["coding_level"] == 5
        assert cfg["test_command"] == "pytest -x"
        assert cfg["hooks"]["naming_gate"] is True  # default preserved

    def test_deep_merge_hooks(self, config_dir):
        _write_config(config_dir, {
            "hooks": {"simplify_gate": {"warn": 300, "block": 800}}
        })
        cfg = get_config()
        assert cfg["hooks"]["simplify_gate"]["warn"] == 300
        assert cfg["hooks"]["simplify_gate"]["block"] == 800
        assert cfg["hooks"]["naming_gate"] is True  # untouched

    def test_disable_hook(self, config_dir):
        _write_config(config_dir, {"hooks": {"naming_gate": False}})
        cfg = get_config()
        assert cfg["hooks"]["naming_gate"] is False
        assert cfg["hooks"]["privacy_gate"] is True

    def test_caching_by_mtime(self, config_dir):
        path = _write_config(config_dir, {"coding_level": 1})
        cfg1 = get_config()
        cfg2 = get_config()
        assert cfg1["coding_level"] == 1
        assert cfg1 is cfg2  # same cached object

    def test_cache_invalidation_on_mtime_change(self, config_dir):
        path = _write_config(config_dir, {"coding_level": 1})
        cfg1 = get_config()
        assert cfg1["coding_level"] == 1

        import time
        time.sleep(0.05)
        _write_config(config_dir, {"coding_level": 4})
        os.utime(str(config_dir / ".man.json"), (9999999, 9999999))
        cfg2 = get_config()
        assert cfg2["coding_level"] == 4

    def test_force_reload(self, config_dir):
        _write_config(config_dir, {"coding_level": 2})
        get_config()
        _write_config(config_dir, {"coding_level": 5})
        cfg = get_config(force_reload=True)
        assert cfg["coding_level"] == 5

    def test_invalid_json_returns_defaults(self, config_dir):
        path = config_dir / ".man.json"
        path.write_text("{invalid json", encoding="utf-8")
        cfg = get_config()
        assert cfg == _DEFAULTS

    def test_non_dict_json_returns_defaults(self, config_dir):
        _write_config(config_dir, [1, 2, 3])
        cfg = get_config()
        assert cfg == _DEFAULTS

    def test_extra_keys_preserved(self, config_dir):
        _write_config(config_dir, {"custom_key": "custom_value"})
        cfg = get_config()
        assert cfg["custom_key"] == "custom_value"
        assert cfg["coding_level"] == 3  # default still there


class TestIsHookEnabled:
    def test_enabled_by_default(self, config_dir):
        assert is_hook_enabled("naming_gate") is True

    def test_disabled_explicitly(self, config_dir):
        _write_config(config_dir, {"hooks": {"naming_gate": False}})
        assert is_hook_enabled("naming_gate") is False

    def test_dict_config_means_enabled(self, config_dir):
        _write_config(config_dir, {"hooks": {"simplify_gate": {"warn": 100}}})
        assert is_hook_enabled("simplify_gate") is True

    def test_unknown_hook_defaults_true(self, config_dir):
        assert is_hook_enabled("nonexistent_hook") is True


class TestGetHookConfig:
    def test_returns_dict_config(self, config_dir):
        _write_config(config_dir, {"hooks": {"simplify_gate": {"warn": 200, "block": 600}}})
        cfg = get_hook_config("simplify_gate")
        assert cfg["warn"] == 200
        assert cfg["block"] == 600

    def test_returns_empty_for_bool_hook(self, config_dir):
        _write_config(config_dir, {"hooks": {"naming_gate": True}})
        cfg = get_hook_config("naming_gate")
        assert cfg == {}

    def test_returns_empty_for_missing_hook(self, config_dir):
        cfg = get_hook_config("nonexistent")
        assert cfg == {}


class TestDeepMerge:
    def test_flat_merge(self):
        result = _deep_merge({"a": 1, "b": 2}, {"b": 3, "c": 4})
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self):
        base = {"x": {"a": 1, "b": 2}}
        overlay = {"x": {"b": 3, "c": 4}}
        result = _deep_merge(base, overlay)
        assert result == {"x": {"a": 1, "b": 3, "c": 4}}

    def test_overlay_replaces_non_dict(self):
        result = _deep_merge({"x": {"a": 1}}, {"x": "string"})
        assert result == {"x": "string"}

    def test_base_unchanged(self):
        base = {"a": 1}
        _deep_merge(base, {"a": 2})
        assert base == {"a": 1}


class TestPrivacyPatterns:
    def test_extra_patterns_from_config(self, config_dir):
        _write_config(config_dir, {"privacy_patterns": ["*.vault", "*.keystore"]})
        cfg = get_config()
        assert cfg["privacy_patterns"] == ["*.vault", "*.keystore"]

    def test_empty_patterns_default(self, config_dir):
        cfg = get_config()
        assert cfg["privacy_patterns"] == []
