import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.subagent_stop_gate import evaluate


def test_allows_stop_with_substantive_output():
    ok, reason = evaluate({"output": "Task completed successfully with all tests passing."})
    assert ok is True
    assert reason == ""


def test_allows_stop_when_output_missing():
    ok, reason = evaluate({})
    assert ok is True


def test_allows_stop_when_output_empty_string():
    ok, reason = evaluate({"output": ""})
    assert ok is True


def test_blocks_stop_when_output_too_short():
    ok, reason = evaluate({"output": "Done."})
    assert ok is False
    assert "too short" in reason.lower() or "continue" in reason.lower()


def test_blocks_implementer_without_status():
    ok, reason = evaluate({
        "agent_type": "trieu-van",
        "output": "I finished implementing the feature and all tests pass."
    })
    assert ok is False
    assert "Status:" in reason or "DONE" in reason


def test_allows_implementer_with_done_status():
    ok, reason = evaluate({
        "agent_type": "trieu-van",
        "output": "Implemented the feature.\n\nStatus: DONE\nSummary: All tests pass."
    })
    assert ok is True


def test_allows_implementer_with_blocked_status():
    ok, reason = evaluate({
        "agent_type": "implementer",
        "output": "Could not proceed.\n\nStatus: BLOCKED\nSummary: Missing credentials."
    })
    assert ok is True


def test_allows_non_implementer_without_status():
    ok, reason = evaluate({
        "agent_type": "researcher",
        "output": "Found relevant documentation about the topic."
    })
    assert ok is True


def test_uses_last_assistant_message_fallback():
    ok, reason = evaluate({"last_assistant_message": "x"})
    assert ok is False
