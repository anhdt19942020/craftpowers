---
name: event-driven-agents
description: Set up reactive agents that respond to external events via Channels (MCP push)
phase: OPERATE
---

# Event-Driven Agents

Set up Claude Code agents that react to external events pushed through Channels — MCP servers that deliver messages into active sessions without polling.

## What Are Channels?

Channels are MCP servers that push external events into a running Claude Code session. Instead of Claude polling for changes, events arrive in real-time:

- GitHub webhook fires → Channel pushes "PR opened" into session → Agent reviews
- Slack message received → Channel pushes message → Agent responds
- CI build fails → Channel pushes failure → Agent investigates

**Key difference from Routines:**
- Channels require an active local session (or long-running server)
- Routines run on Anthropic cloud independently
- Channels are real-time push; Routines are scheduled pull

## When to Use

```
Need to react to external events? → Yes
├── Real-time response needed? → Channel (event-driven)
├── Can wait for scheduled check? → Routine (cloud)
└── One-time check? → Manual or /schedule
```

**Use Channels for:**
- Auto-review PRs as they open (real-time)
- Respond to Slack messages while in a coding session
- React to CI failures immediately
- Monitor deployment health during a release
- Watch for file changes in external systems

**Do NOT use for:**
- Scheduled/periodic tasks (use Routines)
- Tasks that need to run unattended (use Routines)
- Simple polling (use /loop)

## Architecture

```
External System → Webhook → Channel MCP Server → Claude Session → Agent Response
     (GitHub)     (POST)    (localhost:PORT)      (active)        (review PR)
```

The Channel MCP server:
1. Listens for incoming webhooks/events
2. Translates them into MCP messages
3. Pushes into the active Claude session
4. Claude processes and dispatches appropriate agent

## Setup Pattern

### Step 1: Configure MCP Channel Server

Add to `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "github-events": {
      "command": "node",
      "args": ["./mcp-servers/github-channel.js"],
      "env": {
        "WEBHOOK_PORT": "3456",
        "GITHUB_SECRET": "${GITHUB_WEBHOOK_SECRET}"
      }
    }
  }
}
```

### Step 2: Set Up Webhook

Point your GitHub repo webhook to `http://your-machine:3456/webhook` with the events you want (pull_request, issues, push, etc.).

### Step 3: Configure Agent Response

In your CLAUDE.md or session, instruct Claude how to handle each event type:

```markdown
When a Channel delivers a GitHub event:
- pull_request.opened → dispatch code-reviewer for initial review
- issues.opened → dispatch codebase-explorer to find relevant files, then comment
- push to main → dispatch release-prep to verify no breaking changes
- check_run.completed (failure) → dispatch debugger to investigate
```

## Event→Agent Mapping

| Event Source | Event Type | Recommended Agent | Action |
|---|---|---|---|
| GitHub | PR opened | code-reviewer | Review diff, comment |
| GitHub | Issue opened | codebase-explorer | Find relevant files, triage |
| GitHub | CI failure | debugger | Investigate root cause |
| GitHub | Push to main | release-prep | Pre-deploy audit |
| Slack | Message | architect | Answer architecture questions |
| File system | Config changed | secure-reviewer | Security audit |

## Cost Optimization

- Channel events trigger full agent sessions — each event costs tokens
- **Filter events** at the MCP server level — don't push every commit, only PRs and failures
- **Use Sonnet** for triage agents (codebase-explorer, quick-fix)
- **Use Haiku** for simple label/comment responses
- **Debounce** rapid events (e.g., multiple pushes in quick succession)
- Set `maxTurns` on responding agents to cap cost per event

## Integration with mankit

- Agents dispatched by Channels use the same role-based agents
- `permissionMode: plan` for read-only responses (reviews, triage)
- `permissionMode: acceptEdits` for fix-and-PR responses
- Pair with `man:agent-teams` for complex multi-agent event responses
- Cost tracked by `man:cost-budgeting` session summary

## Limitations

- Requires active local session or long-running server
- MCP Channel server must be implemented (not built-in)
- Webhook endpoint must be reachable (ngrok for local dev)
- Each event triggers token spend — budget accordingly
