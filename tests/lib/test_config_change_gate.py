import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.config_change_gate import evaluate


def test_allows_empty_changes():
    ok, reason = evaluate({})
    assert ok is True
    assert reason == ""


def test_allows_safe_permission():
    ok, reason = evaluate({"changes": {"permissions": {"allow": ["Bash(git *)"]}}})
    assert ok is True


def test_blocks_bash_wildcard():
    ok, reason = evaluate({"changes": {"permissions": {"allow": ["Bash(*)"]}}})
    assert ok is False
    assert "Bash(*)" in reason


def test_blocks_write_wildcard():
    ok, reason = evaluate({"changes": {"permissions": {"allow": ["Write(*)"]}}})
    assert ok is False
    assert "Write(*)" in reason


def test_blocks_security_gate_hook_removal():
    ok, reason = evaluate({"changes": {"hooks_removed": ["security-gate"]}})
    assert ok is False
    assert "security-gate" in reason


def test_blocks_credential_scanner_hook_removal():
    ok, reason = evaluate({"changes": {"hooks_removed": ["credential-scanner"]}})
    assert ok is False
    assert "credential-scanner" in reason


def test_allows_non_security_hook_removal():
    ok, reason = evaluate({"changes": {"hooks_removed": ["some-other-hook"]}})
    assert ok is True


def test_blocks_edit_wildcard():
    ok, reason = evaluate({"changes": {"permissions": {"allow": ["Edit(*)"]}}})
    assert ok is False
