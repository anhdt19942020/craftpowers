"""SessionStart context builder (ported from the bash hook `hooks/session-start`).

build_session_start_context(plugin_root, home=None) -> str

Returns the raw <EXTREMELY_IMPORTANT>...</EXTREMELY_IMPORTANT> block embedding
skills/using-man/SKILL.md plus an optional legacy-skills migration warning.
Caller is responsible for JSON-escaping and harness-specific output framing.
"""
from __future__ import annotations
import os
from pathlib import Path

# Warning text ported verbatim from hooks/session-start bash script.
_LEGACY_WARNING = (
    "\n\n<important-reminder>IN YOUR FIRST REPLY AFTER SEEING THIS MESSAGE YOU MUST TELL THE USER:"
    "⚠️ **WARNING:** Superpowers now uses Claude Code's skills system. Custom skills in "
    "~/.config/superpowers/skills will not be read. Move custom skills to ~/.claude/skills "
    "instead. To make this message go away, remove ~/.config/superpowers/skills</important-reminder>"
)


def build_session_start_context(plugin_root: str, home: str | None = None) -> str:
    home = home or os.path.expanduser("~")

    skill_path = Path(plugin_root) / "skills" / "using-man" / "SKILL.md"
    try:
        # bash hook used $(cat ...) which strips trailing newlines — match that
        # so the injected block is byte-identical across harnesses.
        using_man = skill_path.read_text(encoding="utf-8").rstrip("\n")
    except Exception:
        using_man = "Error reading using-man skill"

    warning = ""
    if (Path(home) / ".config" / "superpowers" / "skills").is_dir():
        warning = _LEGACY_WARNING

    return (
        "<EXTREMELY_IMPORTANT>\n"
        "You have man.\n\n"
        "**Below is the full content of your 'man:using-man' skill - your introduction to using "
        "skills. For all other skills, use the 'Skill' tool:**\n\n"
        f"{using_man}\n\n"
        f"{warning}\n"
        "</EXTREMELY_IMPORTANT>"
    )
