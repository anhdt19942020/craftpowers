#!/usr/bin/env python3
"""
SessionStart hook: Inject domain knowledge skill priority supplement.
Runs after the official superpowers plugin's session-start hook.
Output: additionalContext injected into every session.
"""
import json
import os
import sys

SUPPLEMENT = (
    "SKILL PRIORITY SUPPLEMENT (craftpowers): "
    "Domain knowledge skills (websocket-patterns, nodejs-patterns, laravel-patterns, "
    "nestjs-expert, prisma-expert, etc.) load CONCURRENTLY with process skills — "
    "not deferred to implementation phase. "
    "Examples: brainstorming about WebSockets → invoke brainstorming + websocket-patterns simultaneously. "
    "Debugging a Node.js issue → invoke systematic-debugging + nodejs-patterns simultaneously. "
    "Red flag: 'I already loaded a process skill, domain skills come later' — this is wrong. Load them now."
)

def main():
    # Detect platform from environment
    # Claude Code sets CLAUDE_PLUGIN_ROOT, Cursor sets CURSOR_PLUGIN_ROOT
    cursor = os.environ.get("CURSOR_PLUGIN_ROOT", "")
    claude = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    copilot = os.environ.get("COPILOT_CLI", "")

    if cursor:
        output = {"additional_context": SUPPLEMENT}
    elif claude and not copilot:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": SUPPLEMENT,
            }
        }
    else:
        output = {"additionalContext": SUPPLEMENT}

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
