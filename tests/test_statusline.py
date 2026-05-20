"""Tests for hooks/lib/statusline.py."""
import re
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

from lib.statusline import render, _short_model, _short_path, _colored_bar, _context_color, RESET, GREEN, YELLOW, RED


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


class TestShortModel:
    def test_dict_display_name(self):
        assert _short_model({"display_name": "Opus 4.6"}) == "Opus 4.6"

    def test_dict_fallback(self):
        assert _short_model({}) == "Claude"

    def test_string_claude_id(self):
        assert _short_model("claude-opus-4-6") == "opus-4.6"

    def test_string_sonnet(self):
        assert _short_model("claude-sonnet-4-6") == "sonnet-4.6"

    def test_empty(self):
        assert _short_model("") == "unknown"

    def test_none(self):
        assert _short_model(None) == "unknown"

    def test_no_dash(self):
        assert _short_model("claude-opus") == "opus"


class TestShortPath:
    def test_forward_slashes(self):
        result = _short_path("D:/projects/craftpowers")
        assert "D:/projects/craftpowers" in result

    def test_backslash_converted(self):
        result = _short_path("C:\\Users\\anhdt\\code")
        assert "\\" not in result

    def test_empty(self):
        assert _short_path("") == "?"

    def test_home_collapsed(self):
        home = os.path.expanduser("~")
        result = _short_path(os.path.join(home, "projects", "test"))
        assert result.startswith("~/")


class TestColoredBar:
    def test_low_percentage(self):
        bar = _strip_ansi(_colored_bar(20))
        assert bar.count("▰") == 2
        assert bar.count("▱") == 10

    def test_full(self):
        bar = _strip_ansi(_colored_bar(100))
        assert bar.count("▰") == 12
        assert bar.count("▱") == 0

    def test_zero(self):
        bar = _strip_ansi(_colored_bar(0))
        assert bar.count("▰") == 0
        assert bar.count("▱") == 12

    def test_high_uses_red(self):
        bar = _colored_bar(90)
        assert RED in bar

    def test_mid_uses_yellow(self):
        bar = _colored_bar(75)
        assert YELLOW in bar

    def test_low_uses_green(self):
        bar = _colored_bar(20)
        assert GREEN in bar


class TestContextColor:
    def test_low(self):
        assert _context_color(20) == GREEN

    def test_mid(self):
        assert _context_color(75) == YELLOW

    def test_high(self):
        assert _context_color(90) == RED

    def test_boundary_70(self):
        assert _context_color(70) == YELLOW

    def test_boundary_85(self):
        assert _context_color(85) == RED


class TestRender:
    def test_dict_model(self):
        data = {
            "model": {"display_name": "Opus 4.6"},
            "context_window": {"used_percentage": 42},
            "workspace": {"current_dir": "D:/projects/craftpowers"},
        }
        plain = _strip_ansi(render(data))
        assert "Opus 4.6" in plain
        assert "42%" in plain
        assert "craftpowers" in plain

    def test_string_model(self):
        data = {
            "model": "claude-opus-4-6",
            "context_window": {"used_percentage": 10},
            "workspace": {"cwd": "/home/user/project"},
        }
        plain = _strip_ansi(render(data))
        assert "opus-4.6" in plain

    def test_zero_context_no_bar(self):
        data = {
            "model": {"display_name": "Sonnet 4.6"},
            "context_window": {"used_percentage": 0},
            "workspace": {"cwd": "/app"},
        }
        plain = _strip_ansi(render(data))
        assert "▰" not in plain

    def test_empty_data(self):
        plain = _strip_ansi(render({}))
        assert "unknown" in plain

    def test_icons_present(self):
        data = {
            "model": {"display_name": "Opus 4.6"},
            "context_window": {"used_percentage": 20},
            "workspace": {"current_dir": "D:/projects/test"},
        }
        result = render(data)
        assert "🤖" in result
        assert "📁" in result

    def test_progress_bar_in_output(self):
        data = {
            "model": {"display_name": "Opus 4.6"},
            "context_window": {"used_percentage": 50},
            "workspace": {"cwd": "/a/b"},
        }
        result = render(data)
        assert "▰" in result
        assert "50%" in _strip_ansi(result)

    def test_sections_separated_by_double_space(self):
        data = {
            "model": {"display_name": "Opus 4.6"},
            "context_window": {"used_percentage": 10},
            "workspace": {"cwd": "/a/b"},
        }
        plain = _strip_ansi(render(data))
        assert "  " in plain
