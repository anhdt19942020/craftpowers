"""Tests for hooks.lib.skill_telemetry."""
from __future__ import annotations
import json
import os
from unittest.mock import patch

import pytest


def test_detect_slash_command():
    from hooks.lib.skill_telemetry import detect_invoked_skills
    skills = detect_invoked_skills("/man-plan let's plan the feature")
    assert skills == ["man-plan"]


def test_detect_command_name_tag():
    from hooks.lib.skill_telemetry import detect_invoked_skills
    text = "<command-name>writing-plans</command-name> some other text"
    skills = detect_invoked_skills(text)
    assert skills == ["writing-plans"]


def test_detect_multiple_slash_commands():
    from hooks.lib.skill_telemetry import detect_invoked_skills
    text = "/man-plan then /man-ship"
    skills = detect_invoked_skills(text)
    assert set(skills) == {"man-plan", "man-ship"}


def test_detect_no_skills():
    from hooks.lib.skill_telemetry import detect_invoked_skills
    skills = detect_invoked_skills("just a normal message")
    assert skills == []


def test_detect_empty_string():
    from hooks.lib.skill_telemetry import detect_invoked_skills
    assert detect_invoked_skills("") == []


def test_detect_none():
    from hooks.lib.skill_telemetry import detect_invoked_skills
    assert detect_invoked_skills(None) == []


def test_log_skill_appends_jsonl(tmp_path):
    from hooks.lib.skill_telemetry import log_skill
    jsonl_path = tmp_path / "telemetry.jsonl"
    log_skill("man-plan", session_id="sess-1", root=".", jsonl_path=str(jsonl_path), summary_path=str(tmp_path / "summary.json"))
    log_skill("man-plan", session_id="sess-1", root=".", jsonl_path=str(jsonl_path), summary_path=str(tmp_path / "summary.json"))
    lines = jsonl_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    entry = json.loads(lines[0])
    assert entry["skill"] == "man-plan"
    assert entry["session_id"] == "sess-1"
    assert "ts" in entry
    assert "lines" in entry


def test_log_skill_updates_summary(tmp_path):
    from hooks.lib.skill_telemetry import log_skill
    jsonl_path = tmp_path / "telemetry.jsonl"
    summary_path = tmp_path / "summary.json"
    log_skill("man-plan", session_id="s1", root=".", jsonl_path=str(jsonl_path), summary_path=str(summary_path))
    log_skill("man-plan", session_id="s1", root=".", jsonl_path=str(jsonl_path), summary_path=str(summary_path))
    log_skill("brainstorming", session_id="s1", root=".", jsonl_path=str(jsonl_path), summary_path=str(summary_path))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["man-plan"] == 2
    assert summary["brainstorming"] == 1


def test_log_skill_missing_parent_dir_is_safe(tmp_path):
    from hooks.lib.skill_telemetry import log_skill
    # Parent dir does not exist — should not raise
    bad_path = str(tmp_path / "nonexistent" / "telemetry.jsonl")
    bad_summary = str(tmp_path / "nonexistent" / "summary.json")
    # Should fail silently
    log_skill("man-plan", session_id="s1", root=".", jsonl_path=bad_path, summary_path=bad_summary)


def test_log_skill_malformed_summary_recovers(tmp_path):
    from hooks.lib.skill_telemetry import log_skill
    jsonl_path = tmp_path / "telemetry.jsonl"
    summary_path = tmp_path / "summary.json"
    # Write corrupted summary
    summary_path.write_text("NOT JSON!!!", encoding="utf-8")
    # Should recover, not raise
    log_skill("man-plan", session_id="s1", root=".", jsonl_path=str(jsonl_path), summary_path=str(summary_path))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["man-plan"] == 1


def test_estimate_skill_lines_returns_int(tmp_path):
    from hooks.lib.skill_telemetry import estimate_skill_lines
    # Non-existent skill returns 0
    result = estimate_skill_lines("no-such-skill", root=str(tmp_path))
    assert result == 0


def test_estimate_skill_lines_counts_real_file(tmp_path):
    from hooks.lib.skill_telemetry import estimate_skill_lines
    skill_dir = tmp_path / "skills" / "my-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("line1\nline2\nline3\n", encoding="utf-8")
    result = estimate_skill_lines("my-skill", root=str(tmp_path))
    assert result == 3


def test_get_session_summary_empty(tmp_path):
    from hooks.lib.skill_telemetry import get_session_summary
    jsonl_path = tmp_path / "telemetry.jsonl"
    # No file yet — should return empty dict
    result = get_session_summary("sess-abc", jsonl_path=str(jsonl_path))
    assert result == {}


def test_get_session_summary_filters_by_session(tmp_path):
    from hooks.lib.skill_telemetry import log_skill, get_session_summary
    jsonl_path = tmp_path / "telemetry.jsonl"
    summary_path = tmp_path / "summary.json"
    log_skill("man-plan", session_id="sess-1", root=".", jsonl_path=str(jsonl_path), summary_path=str(summary_path))
    log_skill("man-plan", session_id="sess-1", root=".", jsonl_path=str(jsonl_path), summary_path=str(summary_path))
    log_skill("brainstorming", session_id="sess-2", root=".", jsonl_path=str(jsonl_path), summary_path=str(summary_path))
    result = get_session_summary("sess-1", jsonl_path=str(jsonl_path))
    assert result == {"man-plan": 2}


def test_format_session_skills_message():
    from hooks.lib.skill_telemetry import format_session_skills_message
    counts = {"writing-plans": 2, "brainstorming": 1}
    msg = format_session_skills_message(counts, total_skills=42)
    assert "writing-plans (2x)" in msg
    assert "brainstorming (1x)" in msg
    # 2 unique skills used, not sum of invocations
    assert "2 of 42" in msg


def test_format_session_skills_message_empty():
    from hooks.lib.skill_telemetry import format_session_skills_message
    msg = format_session_skills_message({}, total_skills=42)
    assert msg == ""
