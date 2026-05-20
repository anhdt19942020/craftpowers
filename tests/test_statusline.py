"""Tests for hooks/lib/statusline.py."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

from lib.statusline import render, _short_model, _short_path


class TestShortModel:
    def test_full_claude_id(self):
        assert _short_model("claude-opus-4-6") == "opus-4.6"

    def test_opus_47(self):
        assert _short_model("claude-opus-4-7") == "opus-4.7"

    def test_sonnet(self):
        assert _short_model("claude-sonnet-4-6") == "sonnet-4.6"

    def test_haiku_with_date_suffix(self):
        assert _short_model("claude-haiku-4-5-20251001") == "haiku-4-5.20251001"

    def test_empty(self):
        assert _short_model("") == "unknown"

    def test_none(self):
        assert _short_model(None) == "unknown"

    def test_anthropic_prefix_stripped(self):
        assert _short_model("anthropic/claude-opus-4") == "claude-opus.4"

    def test_no_known_prefix_still_normalizes(self):
        assert _short_model("gpt-4") == "gpt.4"

    def test_no_dash_returns_as_is(self):
        assert _short_model("claude-opus") == "opus"


class TestShortPath:
    def test_deep_path(self):
        assert _short_path("D:/projects/craftpowers") == "projects/craftpowers"

    def test_backslash(self):
        assert _short_path("C:\\Users\\anhdt\\code") == "anhdt/code"

    def test_single_component(self):
        # "/root".split("/") → ["", "root"] — 2 parts, so joins last 2 → "/root"
        assert _short_path("/root") == "/root"

    def test_empty(self):
        assert _short_path("") == "?"

    def test_trailing_slash_ignored(self):
        assert _short_path("D:/projects/craftpowers/") == "projects/craftpowers"

    def test_mixed_slashes(self):
        assert _short_path("C:\\Users/anhdt\\code") == "anhdt/code"

    def test_two_part_path(self):
        assert _short_path("/home/user") == "home/user"


class TestRender:
    def test_full_data(self):
        data = {
            "model": "claude-opus-4-6",
            "context_window": {"used_percentage": 42},
            "workspace": {
                "cwd": "D:/projects/craftpowers",
                "git_branch": "main"
            }
        }
        result = render(data)
        assert "[opus-4.6]" in result
        assert "ctx:42%" in result
        assert "projects/craftpowers" in result
        assert "main" in result

    def test_no_branch(self):
        data = {
            "model": "claude-opus-4-6",
            "context_window": {"used_percentage": 10},
            "workspace": {"cwd": "/home/user/project"}
        }
        result = render(data)
        assert "⎇" not in result  # ⎇ symbol (U+2387) absent when no branch

    def test_empty_data(self):
        result = render({})
        assert "[unknown]" in result
        assert "ctx:0%" in result

    def test_zero_context(self):
        data = {
            "model": "claude-sonnet-4-6",
            "context_window": {"used_percentage": 0},
            "workspace": {"cwd": "/app", "git_branch": "feat/x"}
        }
        result = render(data)
        assert "ctx:0%" in result
        assert "feat/x" in result

    def test_full_render_exact_format(self):
        data = {
            "model": "claude-opus-4-6",
            "context_window": {"used_percentage": 42},
            "workspace": {"cwd": "D:/projects/craftpowers", "git_branch": "main"},
        }
        result = render(data)
        # │ = U+2502, 📂 = U+1F4C2, ⎇ = U+2387
        assert result == "[opus-4.6] │ ctx:42% │ \U0001f4c2 projects/craftpowers │ ⎇ main"

    def test_missing_context_window_key(self):
        data = {"model": "claude-sonnet-4-6", "workspace": {"cwd": "/a/b"}}
        result = render(data)
        assert "ctx:0%" in result

    def test_high_context_percentage(self):
        data = {
            "model": "claude-opus-4-6",
            "context_window": {"used_percentage": 99},
            "workspace": {"cwd": "/a/b"}
        }
        result = render(data)
        assert "ctx:99%" in result

    def test_branch_with_slash(self):
        data = {
            "model": "claude-opus-4-6",
            "context_window": {"used_percentage": 5},
            "workspace": {"cwd": "/a/b", "git_branch": "feature/my-feature"}
        }
        result = render(data)
        assert "feature/my-feature" in result

    def test_parts_separated_by_pipe(self):
        data = {
            "model": "claude-opus-4-6",
            "context_window": {"used_percentage": 10},
            "workspace": {"cwd": "/a/b", "git_branch": "main"}
        }
        result = render(data)
        # separator is " │ " (U+2502)
        assert " │ " in result
