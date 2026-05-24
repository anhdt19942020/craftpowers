"""Tests for hook profile system."""
from unittest.mock import patch
from hooks.lib.hook_profiles import get_active_profile, is_gate_active, PROFILES


def test_default_profile():
    with patch.dict("os.environ", {}, clear=True):
        with patch("hooks.lib.hook_profiles.get_config", return_value={}):
            assert get_active_profile() == "standard"


def test_env_overrides_config():
    with patch.dict("os.environ", {"MAN_HOOK_PROFILE": "minimal"}):
        assert get_active_profile() == "minimal"


def test_env_strict():
    with patch.dict("os.environ", {"MAN_HOOK_PROFILE": "strict"}):
        assert get_active_profile() == "strict"


def test_invalid_env_falls_back_to_standard():
    with patch.dict("os.environ", {"MAN_HOOK_PROFILE": "turbo"}):
        with patch("hooks.lib.hook_profiles.get_config", return_value={}):
            assert get_active_profile() == "standard"


def test_config_overrides_default():
    with patch.dict("os.environ", {}, clear=True):
        with patch("hooks.lib.hook_profiles.get_config", return_value={"hook_profile": "minimal"}):
            assert get_active_profile() == "minimal"


def test_minimal_disables_naming():
    with patch("hooks.lib.hook_profiles.get_active_profile", return_value="minimal"):
        assert is_gate_active("naming_gate") is False
        assert is_gate_active("security_gate") is True


def test_strict_enables_write_quality():
    with patch("hooks.lib.hook_profiles.get_active_profile", return_value="strict"):
        assert is_gate_active("write_quality") is True


def test_standard_disables_write_quality():
    with patch("hooks.lib.hook_profiles.get_active_profile", return_value="standard"):
        assert is_gate_active("write_quality") is False


def test_all_profiles_have_security():
    for name, gates in PROFILES.items():
        assert gates["security_gate"] is True, f"{name} must have security_gate"


def test_all_profiles_have_privacy():
    for name, gates in PROFILES.items():
        assert gates["privacy_gate"] is True, f"{name} must have privacy_gate"
