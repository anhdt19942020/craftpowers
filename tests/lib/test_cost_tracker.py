"""Tests for cost_tracker — per-session cost record appended to costs.jsonl."""
from __future__ import annotations
import json
import pathlib
import tempfile

import pytest

from hooks.lib.cost_tracker import _model_cost, track, MODEL_COSTS, _DEFAULT_COST


# ── _model_cost ────────────────────────────────────────────────────────────────

def test_model_cost_exact_match():
    assert _model_cost("claude-sonnet-4-6") == (3.0, 15.0)


def test_model_cost_opus():
    assert _model_cost("claude-opus-4-7") == (15.0, 75.0)


def test_model_cost_haiku():
    assert _model_cost("claude-haiku-4-5") == (0.80, 4.0)


def test_model_cost_partial_match():
    # Real model IDs often have date suffix
    cost = _model_cost("claude-sonnet-4-6-20251014")
    assert cost == (3.0, 15.0)


def test_model_cost_dot_variant():
    # Allow both dash and dot separators in model names
    assert _model_cost("claude-opus-4.7") == (15.0, 75.0)


def test_model_cost_unknown_falls_back_to_default():
    assert _model_cost("gpt-4o") == _DEFAULT_COST
    assert _model_cost("") == _DEFAULT_COST
    assert _model_cost(None) == _DEFAULT_COST  # type: ignore[arg-type]


def test_model_cost_case_insensitive():
    assert _model_cost("Claude-Sonnet-4-6") == (3.0, 15.0)


# ── track ──────────────────────────────────────────────────────────────────────

def _make_track(tmp_path: pathlib.Path, monkeypatch):
    """Return a track() call that writes to tmp_path/costs.jsonl."""
    metrics_file = tmp_path / "costs.jsonl"

    def fake_metrics_path():
        tmp_path.mkdir(parents=True, exist_ok=True)
        return metrics_file

    monkeypatch.setattr("hooks.lib.cost_tracker._metrics_path", fake_metrics_path)
    return metrics_file


def test_track_returns_record_schema(tmp_path, monkeypatch):
    _make_track(tmp_path, monkeypatch)
    record = track(None, "sess-1", "claude-sonnet-4-6")
    assert "date" in record
    assert "session_id" in record
    assert "model" in record
    assert "input_tokens" in record
    assert "output_tokens" in record
    assert "estimated_usd" in record


def test_track_writes_jsonl(tmp_path, monkeypatch):
    metrics_file = _make_track(tmp_path, monkeypatch)
    track(None, "sess-2", "claude-sonnet-4-6")
    lines = metrics_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["session_id"] == "sess-2"


def test_track_appends_multiple_records(tmp_path, monkeypatch):
    metrics_file = _make_track(tmp_path, monkeypatch)
    track(None, "sess-a", "claude-sonnet-4-6")
    track(None, "sess-b", "claude-opus-4-7")
    lines = metrics_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2


def test_track_none_transcript_does_not_crash(tmp_path, monkeypatch):
    _make_track(tmp_path, monkeypatch)
    record = track(None, "", "claude-haiku-4-5")
    assert record["estimated_usd"] >= 0.0


def test_track_date_format(tmp_path, monkeypatch):
    _make_track(tmp_path, monkeypatch)
    record = track(None, "sess-date", "claude-sonnet-4-6")
    # Should be YYYY-MM-DD
    parts = record["date"].split("-")
    assert len(parts) == 3
    assert len(parts[0]) == 4  # year


def test_track_estimated_usd_non_negative(tmp_path, monkeypatch):
    _make_track(tmp_path, monkeypatch)
    record = track(None, "sess-usd", "claude-opus-4-7")
    assert record["estimated_usd"] >= 0.0
