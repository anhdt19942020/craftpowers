import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.compact_hooks import pre_compact, post_compact


def test_pre_compact_includes_trigger():
    result = pre_compact({"trigger": "manual"})
    assert "manual" in result


def test_pre_compact_includes_protocol_hint():
    result = pre_compact({})
    assert "man:context-management" in result


def test_pre_compact_lists_checklist_items():
    result = pre_compact({"trigger": "auto"})
    assert "what you are doing" in result
    assert "key decisions" in result
    assert "uncommitted intent" in result


def test_pre_compact_default_trigger_when_missing():
    result = pre_compact({})
    assert "unknown" in result


def test_post_compact_includes_recovery_steps():
    result = post_compact({})
    assert "git log" in result
    assert "REQUIRED" in result


def test_post_compact_includes_protocol_hint():
    result = post_compact({})
    assert "man:session-recovery" in result


def test_post_compact_returns_string():
    result = post_compact({"anything": "ignored"})
    assert isinstance(result, str)
    assert len(result) > 0
