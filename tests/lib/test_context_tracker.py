import json
from hooks.lib.context_tracker import estimate_tokens, context_warning

def _write_transcript(path, messages):
    path.write_text("\n".join(json.dumps({"message": {"role": r, "content": c}}) for r, c in messages), encoding="utf-8")

def test_estimate_tokens_missing_file_is_zero(tmp_path):
    assert estimate_tokens(str(tmp_path / "nope.jsonl")) == 0
    assert estimate_tokens(None) == 0

def test_estimate_tokens_counts_chars_over_four(tmp_path):
    t = tmp_path / "t.jsonl"
    _write_transcript(t, [("user", "a" * 400), ("assistant", "b" * 400)])
    assert estimate_tokens(str(t)) == 200  # 800 chars / 4

def test_no_warning_below_threshold(tmp_path):
    t = tmp_path / "t.jsonl"
    _write_transcript(t, [("user", "x" * 4000)])  # ~1000 tokens
    assert context_warning(str(t), model="claude-opus-4-7") is None

def test_warning_at_warn_threshold(tmp_path):
    t = tmp_path / "t.jsonl"
    _write_transcript(t, [("user", "x" * (150_000 * 4))])  # ~150k tokens
    msg = context_warning(str(t), model="claude-sonnet-4-6")
    assert msg is not None
    assert "/compact" in msg
    assert "context-tracker" in msg

def test_critical_message_at_high_usage(tmp_path):
    t = tmp_path / "t.jsonl"
    _write_transcript(t, [("user", "x" * (180_000 * 4))])  # ~180k tokens
    msg = context_warning(str(t), model="claude-sonnet-4-6")
    assert "now" in msg.lower()
