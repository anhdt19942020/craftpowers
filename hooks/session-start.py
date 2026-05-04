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
    "CRAFTPOWERS SKILL RULE — READ BEFORE FOLLOWING ANY SKILL CHECKLIST:\n\n"
    "Domain knowledge skills are KNOWLEDGE REFERENCES, NOT implementation skills. "
    "They are NEVER blocked by brainstorming's HARD-GATE or any other process skill restriction.\n\n"
    "Domain knowledge skills: websocket-patterns, nodejs-patterns, laravel-patterns, "
    "nestjs-expert, prisma-expert, typescript-expert, react-patterns, tailwind-patterns.\n\n"
    "RULE: When the topic matches a domain knowledge skill, invoke it IMMEDIATELY — "
    "at the same time as (or right after) the process skill, before reading any checklist.\n\n"
    "EXAMPLES:\n"
    "- Topic mentions socket/WebSocket/Socket.IO/real-time → invoke websocket-patterns NOW\n"
    "- Topic mentions Node.js/Express/Fastify/streams → invoke nodejs-patterns NOW\n"
    "- Topic mentions Laravel/PHP → invoke laravel-patterns NOW\n\n"
    "Red flag: 'websocket-patterns is an implementation skill, HARD-GATE blocks it' — WRONG. "
    "It is a knowledge reference. Invoke it now."
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
