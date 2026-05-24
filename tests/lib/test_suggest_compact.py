"""Tests for suggest_compact — tool-call counter that nudges /compact at phase boundaries."""
from __future__ import annotations
import os
import uuid

import pytest

from hooks.lib.suggest_compact import evaluate, THRESHOLD, REMIND_INTERVAL


def _unique_session(monkeypatch) -> str:
    """Give each test its own session ID so state files don't bleed between tests."""
    sid = f"test-{uuid.uuid4().hex[:8]}"
    monkeypatch.setenv("CLAUDE_SESSION_ID", sid)
    return sid


# ── Below threshold ────────────────────────────────────────────────────────────

def test_returns_none_below_threshold(monkeypatch):
    _unique_session(monkeypatch)
    for _ in range(THRESHOLD - 1):
        result = evaluate()
    assert result is None


def test_first_call_returns_none(monkeypatch):
    _unique_session(monkeypatch)
    assert evaluate() is None


# ── At threshold ───────────────────────────────────────────────────────────────

def test_returns_message_at_threshold(monkeypatch):
    _unique_session(monkeypatch)
    result = None
    for _ in range(THRESHOLD):
        result = evaluate()
    assert result is not None
    assert "/compact" in result


def test_message_includes_call_count(monkeypatch):
    _unique_session(monkeypatch)
    result = None
    for _ in range(THRESHOLD):
        result = evaluate()
    assert str(THRESHOLD) in result


# ── After suggestion: cooldown ─────────────────────────────────────────────────

def test_no_repeat_within_remind_interval(monkeypatch):
    _unique_session(monkeypatch)
    for _ in range(THRESHOLD):
        evaluate()
    # Calls within REMIND_INTERVAL should be silent
    for _ in range(REMIND_INTERVAL - 1):
        result = evaluate()
    assert result is None


def test_suggests_again_after_remind_interval(monkeypatch):
    _unique_session(monkeypatch)
    for _ in range(THRESHOLD):
        evaluate()
    # Exhaust the cooldown
    result = None
    for _ in range(REMIND_INTERVAL):
        result = evaluate()
    assert result is not None
    assert "/compact" in result


# ── State persistence ──────────────────────────────────────────────────────────

def test_state_persists_across_calls(monkeypatch):
    _unique_session(monkeypatch)
    # Run half the threshold, then finish in a separate batch
    for _ in range(THRESHOLD // 2):
        evaluate()
    result = None
    for _ in range(THRESHOLD - THRESHOLD // 2):
        result = evaluate()
    assert result is not None
