"""Tests for conversation analyzer — post-session instinct candidate generator."""
import json
import tempfile
from pathlib import Path

from hooks.lib.conversation_analyzer import (
    _slugify,
    analyze_corrections,
    analyze_transcript_file,
    run_analysis,
    write_candidate,
)


def test_detects_negative_correction():
    transcript = "fix the login\nassistant: I'll mock the DB\nno, don't do that, use real DB"
    results = analyze_corrections(transcript)
    assert len(results) >= 1
    assert any(r["type"] == "negative" for r in results)


def test_detects_positive_confirmation():
    transcript = "assistant: I'll use integration tests\nyes, exactly, that's what I wanted"
    results = analyze_corrections(transcript)
    assert len(results) >= 1
    assert any(r["type"] == "positive" for r in results)


def test_detects_directive():
    transcript = "user: always use pnpm instead of npm in this project"
    results = analyze_corrections(transcript)
    assert len(results) >= 1
    assert any(r["type"] == "directive" for r in results)


def test_empty_transcript():
    results = analyze_corrections("")
    assert results == []


def test_no_patterns():
    transcript = "Please implement the login feature with OAuth2"
    results = analyze_corrections(transcript)
    assert results == []


def test_slugify_basic():
    assert _slugify("No, don't do that!") == "no-don-t-do-that"


def test_slugify_empty():
    assert _slugify("") == ""


def test_slugify_max_length():
    long_text = "a" * 100
    assert len(_slugify(long_text)) <= 50


def test_write_candidate():
    with tempfile.TemporaryDirectory() as d:
        candidate = {
            "type": "negative",
            "trigger_line": "no don't mock the DB",
            "context": "some context here",
            "confidence": 0.5,
        }
        path = write_candidate(candidate, project_root=d)
        assert path is not None
        assert "candidates" in path
        assert Path(path).exists()
        content = Path(path).read_text()
        assert "confidence: 0.5" in content
        assert "HUMAN REVIEW REQUIRED" in content


def test_run_analysis_creates_files():
    with tempfile.TemporaryDirectory() as d:
        transcript = "no, don't do that\nalways use pnpm instead"
        paths = run_analysis(transcript, project_root=d)
        assert len(paths) >= 1
        for p in paths:
            assert Path(p).exists()


def test_analyze_transcript_file_jsonl():
    with tempfile.TemporaryDirectory() as d:
        transcript_path = Path(d) / "session.jsonl"
        entries = [
            {"message": {"role": "user", "content": "always use pnpm instead of npm"}},
            {"message": {"role": "assistant", "content": "Sure, I'll use pnpm"}},
        ]
        with open(transcript_path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        results = analyze_transcript_file(str(transcript_path))
        assert len(results) >= 1
        assert any(r["type"] == "directive" for r in results)


def test_analyze_nonexistent_file():
    results = analyze_transcript_file("/nonexistent/path/session.jsonl")
    assert results == []
