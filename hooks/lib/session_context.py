"""SessionStart context builder (ported from the bash hook `hooks/session-start`).

build_session_start_context(plugin_root, home=None) -> str

Returns the raw <EXTREMELY_IMPORTANT>...</EXTREMELY_IMPORTANT> block embedding
skills/using-man/SKILL.md plus an optional legacy-skills migration warning.
Caller is responsible for JSON-escaping and harness-specific output framing.
"""
from __future__ import annotations
import os
from pathlib import Path

try:
    from lib.workflow_state import get_summary as _get_workflow_summary
except ImportError:
    _get_workflow_summary = None

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

    workflow_line = ""
    try:
        if _get_workflow_summary:
            summary = _get_workflow_summary()
            if summary:
                workflow_line = f"\n\n<workflow-state>{summary}</workflow-state>"
    except Exception:
        pass

    # Phase 2: inject error context from prior failed agents if any exist
    error_ctx_block = ""
    try:
        from lib.error_context import inject_error_context
        from lib.workflow_state import get_state
        state = get_state()
        if state and isinstance(state, dict):
            wf_id = state.get("workflow_id", "")
            if wf_id:
                error_ctx = inject_error_context(wf_id, home=home)
                if error_ctx:
                    error_ctx_block = f"\n\n## Prior Attempt Context\n{error_ctx}"
    except Exception:
        pass  # error injection must not break session context

    return (
        "<EXTREMELY_IMPORTANT>\n"
        "You have man.\n\n"
        "**Below is the full content of your 'man:using-man' skill - your introduction to using "
        "skills. For all other skills, use the 'Skill' tool:**\n\n"
        f"{using_man}\n\n"
        f"{warning}"
        f"{workflow_line}"
        f"{error_ctx_block}\n"
        "</EXTREMELY_IMPORTANT>"
    )
