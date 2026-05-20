"""Tests for hooks/lib/statusline.py."""
import re
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

from lib.statusline import (
    render, _short_model, _short_path, _colored_bar, _context_color,
    _format_countdown, _quota_section,
    RESET, GREEN, YELLOW, RED, DIM,
)


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


class TestQuota:
    def test_quota_section_with_both_windows(self):
        data = {
            "rate_limits": {
                "five_hour": {"used_percentage": 35, "resets_at": None},
                "seven_day": {"used_percentage": 18, "resets_at": None},
            }
        }
        section = _quota_section(data)
        assert section is not None
        plain = _strip_ansi(section)
        assert "5h 35%" in plain
        assert "wk 18%" in plain
        assert "⌛" in section

    def test_quota_section_five_hour_only(self):
        data = {
            "rate_limits": {
                "five_hour": {"used_percentage": 50},
            }
        }
        section = _quota_section(data)
        assert section is not None
        plain = _strip_ansi(section)
        assert "5h 50%" in plain
        assert "wk" not in plain

    def test_quota_section_no_rate_limits(self):
        assert _quota_section({}) is None
        assert _quota_section({"rate_limits": None}) is None

    def test_quota_section_empty_rate_limits(self):
        assert _quota_section({"rate_limits": {}}) is None

    def test_format_countdown_unix_timestamp(self):
        import time
        future = time.time() + 5400  # 1h30m from now
        cd = _format_countdown(future)
        assert "1h" in cd
        assert "m)" in cd

    def test_format_countdown_iso_string(self):
        from datetime import datetime, timedelta, timezone
        future = (datetime.now(timezone.utc) + timedelta(hours=1, minutes=30)).isoformat()
        cd = _format_countdown(future)
        assert "1h" in cd
        assert "m)" in cd

    def test_format_countdown_past(self):
        assert _format_countdown("2020-01-01T00:00:00+00:00") == ""

    def test_format_countdown_none(self):
        assert _format_countdown(None) == ""

    def test_render_includes_quota(self):
        data = {
            "model": {"display_name": "Opus 4.6"},
            "context_window": {"used_percentage": 30},
            "workspace": {"cwd": "/a/b"},
            "rate_limits": {
                "five_hour": {"used_percentage": 40},
                "seven_day": {"used_percentage": 20},
            },
        }
        plain = _strip_ansi(render(data))
        assert "5h 40%" in plain
        assert "wk 20%" in plain

    def test_render_no_quota_when_missing(self):
        data = {
            "model": {"display_name": "Opus 4.6"},
            "context_window": {"used_percentage": 30},
            "workspace": {"cwd": "/a/b"},
        }
        plain = _strip_ansi(render(data))
        assert "⌛" not in plain

    def test_quota_with_countdown(self):
        import time
        data = {
            "rate_limits": {
                "five_hour": {
                    "used_percentage": 60,
                    "resets_at": time.time() + 3600,
                },
            }
        }
        section = _quota_section(data)
        plain = _strip_ansi(section)
        assert "5h 60%" in plain
        assert "m)" in plain
