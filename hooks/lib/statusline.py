"""Statusline renderer — formats session metadata for Claude Code footer."""
from __future__ import annotations
import json
import os
import subprocess
import sys
import time

RESET = "\x1b[0m"
DIM = "\x1b[2m"
CLEAR = "\x1b[22m\x1b[39m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
MAGENTA = "\x1b[35m"
CYAN = "\x1b[36m"
RED = "\x1b[31m"


def _color(text: str, code: str) -> str:
    return f"{CLEAR}{code}{text}{RESET}{CLEAR}"


def _context_color(pct: int) -> str:
    if pct >= 85:
        return RED
    if pct >= 70:
        return YELLOW
    return GREEN


def _colored_bar(pct: int, width: int = 12) -> str:
    clamped = max(0, min(100, pct))
    filled = round(clamped / 100 * width)
    empty = width - filled
    color = _context_color(pct)
    return f"{CLEAR}{color}{'▰' * filled}{CLEAR}{DIM}{'▱' * empty}{RESET}{CLEAR}"


def _short_model(model) -> str:
    if isinstance(model, dict):
        return model.get("display_name", "Claude")
    m = str(model or "unknown").lower()
    for prefix in ("claude-", "anthropic/"):
        if m.startswith(prefix):
            m = m[len(prefix):]
    parts = m.rsplit("-", 1)
    return f"{parts[0]}.{parts[1]}" if len(parts) == 2 else m


def _short_path(cwd: str) -> str:
    if not cwd:
        return "?"
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        cwd = "~" + cwd[len(home):]
    return cwd.replace("\\", "/")


def _git_info(cwd: str) -> dict | None:
    if not cwd:
        return None
    try:
        def _run(cmd: list[str]) -> str:
            r = subprocess.run(
                cmd, capture_output=True, text=True, cwd=cwd, timeout=3,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            return r.stdout.strip() if r.returncode == 0 else ""

        branch = _run(["git", "symbolic-ref", "--short", "HEAD"])
        if not branch:
            branch = _run(["git", "rev-parse", "--short", "HEAD"])
        if not branch:
            return None

        unstaged = len([l for l in _run(["git", "diff", "--name-only"]).splitlines() if l])
        staged = len([l for l in _run(["git", "diff", "--cached", "--name-only"]).splitlines() if l])

        ab = _run(["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
        ahead, behind = 0, 0
        if ab:
            parts = ab.split()
            if len(parts) == 2:
                ahead, behind = int(parts[0]), int(parts[1])

        return {"branch": branch, "unstaged": unstaged, "staged": staged, "ahead": ahead, "behind": behind}
    except Exception:
        return None


def _format_countdown(resets_at) -> str:
    if not resets_at:
        return ""
    try:
        from datetime import datetime, timezone
        if isinstance(resets_at, (int, float)):
            remaining = int(resets_at - time.time())
        else:
            reset_time = datetime.fromisoformat(str(resets_at).replace("Z", "+00:00"))
            remaining = int((reset_time - datetime.now(timezone.utc)).total_seconds())
        if remaining <= 0 or remaining > 18000:
            return ""
        h, m = remaining // 3600, (remaining % 3600) // 60
        return f"({h}h{m:02d}m)" if h else f"({m}m)"
    except Exception:
        return ""


def _quota_section(data: dict) -> str | None:
    rl = data.get("rate_limits")
    if not rl:
        return None
    windows = []
    fh = rl.get("five_hour", {})
    if isinstance(fh.get("used_percentage"), (int, float)):
        pct = round(fh["used_percentage"])
        cd = _format_countdown(fh.get("resets_at"))
        windows.append(f"5h {pct}%{' ' + cd if cd else ''}")
    sd = rl.get("seven_day", {})
    if isinstance(sd.get("used_percentage"), (int, float)):
        pct = round(sd["used_percentage"])
        cd = _format_countdown(sd.get("resets_at"))
        windows.append(f"wk {pct}%{' ' + cd if cd else ''}")
    if not windows:
        return None
    text = "  ".join(windows)
    return f"⌛ {_color(text, DIM)}"


def render(data: dict) -> str:
    model_name = _short_model(data.get("model", ""))
    ctx_pct = 0
    cw = data.get("context_window", {})
    if isinstance(cw.get("used_percentage"), (int, float)):
        ctx_pct = round(cw["used_percentage"])

    ws = data.get("workspace", {})
    cwd = ws.get("current_dir") or ws.get("cwd", "")
    git = _git_info(cwd)

    parts = [f"🤖 {_color(model_name, CYAN)}"]

    if ctx_pct > 0:
        pct_color = _context_color(ctx_pct)
        parts.append(f"{_colored_bar(ctx_pct)} {_color(f'{ctx_pct}%', pct_color)}")

    quota = _quota_section(data)
    if quota:
        parts.append(quota)

    parts.append(f"📁 {_color(_short_path(cwd), YELLOW)}")

    if git and git["branch"]:
        branch_part = f"🌿 {_color(git['branch'], MAGENTA)}"
        indicators = []
        if git["unstaged"] > 0:
            indicators.append(str(git["unstaged"]))
        if git["staged"] > 0:
            indicators.append(f"+{git['staged']}")
        if git["ahead"] > 0:
            indicators.append(f"{git['ahead']}↑")
        if git["behind"] > 0:
            indicators.append(f"{git['behind']}↓")
        if indicators:
            branch_part += f" {_color('(' + ', '.join(indicators) + ')', YELLOW)}"
        parts.append(branch_part)

    return "  ".join(parts)


def main() -> None:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
        line = render(data)
        if line:
            sys.stdout.write(line)
    except Exception:
        pass
