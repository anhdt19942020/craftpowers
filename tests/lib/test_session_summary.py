import json
from hooks.lib.session_summary import estimate_tokens, format_tokens, context_pct, build_summary

def test_format_tokens():
    assert format_tokens(500) == "500"
    assert format_tokens(1500) == "1.5K"
    assert format_tokens(2_000_000) == "2.0M"

def test_context_pct_caps_at_100():
    assert context_pct(400_000) == 100
    assert context_pct(100_000) == 50

def test_estimate_tokens_splits_input_output(tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text(
        json.dumps({"message": {"role": "assistant", "content": "a" * 400}}) + "\n"
        + json.dumps({"message": {"role": "user", "content": "b" * 800}}) + "\n",
        encoding="utf-8",
    )
    inp, out = estimate_tokens(str(t))
    assert out == 100   # 400 / 4
    assert inp == 200   # 800 / 4

def test_build_summary_uses_injected_rtk_runner(tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text(json.dumps({"message": {"role": "user", "content": "hi"}}) + "\n", encoding="utf-8")
    summary = build_summary(str(t), rtk_runner=lambda: "12,345 tokens")
    assert "Session Summary" in summary
    assert "12,345 tokens" in summary

def test_build_summary_handles_no_rtk(tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text(json.dumps({"message": {"role": "user", "content": "hi"}}) + "\n", encoding="utf-8")
    summary = build_summary(str(t), rtk_runner=lambda: None)
    assert "N/A" in summary
