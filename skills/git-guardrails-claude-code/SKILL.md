---
name: git-guardrails-claude-code
description: Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code.
---

# Setup Git Guardrails

Sets up a PreToolUse hook that intercepts and blocks dangerous git commands before Claude executes them.

## What Gets Blocked
- git push (all variants including --force)
- git reset --hard
- git clean -f / git clean -fd
- git branch -D
- git checkout . / git restore .

When blocked, Claude sees a message telling it that it does not have authority to access these commands.

## Steps

### 1. Ask scope
Ask the user: install for this project only (.claude/settings.json) or all projects (~/.claude/settings.json)?

### 2. Copy the hook script
The bundled script is at: scripts/block-dangerous-git.sh
Copy it to .claude/hooks/ (project) or ~/.claude/hooks/ (global). Make it executable with chmod +x.

### 3. Add hook to settings
Add a PreToolUse hook with matcher "Bash" pointing to the script path.
If settings file already exists, merge into existing hooks.PreToolUse array.

### 4. Ask about customization
Ask if user wants to add or remove any patterns from the blocked list. Edit the copied script accordingly.

### 5. Verify
Run: echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
Should exit with code 2 and print a BLOCKED message to stderr.
