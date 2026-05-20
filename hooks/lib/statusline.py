"""Statusline renderer — formats session metadata for Claude Code footer."""
from __future__ import annotations
import json
import sys


def _short_model(model: str) -> str:
    m = (model or "unknown").lower()
    for prefix in ("claude-", "anthropic/"):
        if m.startswith(prefix):
            m = m[len(prefix):]
    idx = m.rfind("-")
    return m[:idx] + "." + m[idx + 1:] if idx >= 0 else m


def _short_path(cwd: str) -> str:
    if not cwd:
        return "?"
    parts = cwd.replace("\\", "/").rstrip("/").split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else parts[-1]


def render(data: dict) -> str:
    model = _short_model(data.get("model", ""))
    ctx_pct = data.get("context_window", {}).get("used_percentage", 0)
    ws = data.get("workspace", {})
    cwd = _short_path(ws.get("cwd", ""))
    branch = ws.get("git_branch", "")

    parts = [
        f"[{model}]",
        f"ctx:{ctx_pct}%",
        f"📂 {cwd}",
    ]
    if branch:
        parts.append(f"⎇ {branch}")

    return " │ ".join(parts)


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
