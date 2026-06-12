# Wave 2-3 Skills Overview

Added in commit b612d3a: effort-tuning opusplan, cloud-routines skill, event-driven-agents skill.

---

## cloud-routines

Cloud Routines are autonomous Claude Code sessions that run on Anthropic's infrastructure on a cron schedule or triggered by GitHub webhooks — no local machine required. Configure at `claude.ai/code/routines` by connecting a GitHub repo, writing a prompt, and setting a trigger. Each execution is a fresh full Claude Code session billed per run. Use for recurring unattended automation: daily PR triage, weekly dependency audits, nightly test runs, auto-triage of new issues. Unlike local `/schedule`, Routines survive machine sleep/shutdown and can be triggered by external events. Cost scales with frequency and prompt complexity — keep prompts focused and use Sonnet for mechanical tasks.

**Use when:** Work must run unattended, on a schedule, or triggered by GitHub events without a local machine online.

---

## event-driven-agents

Event-Driven Agents react in real-time to external events pushed into an active Claude Code session via Channel MCP servers. A Channel MCP server listens for webhooks (GitHub, Slack, CI systems), translates them into MCP messages, and pushes them into your running session — no polling required. Each incoming event dispatches the appropriate agent (e.g., PR opened → code-reviewer, CI failure → debugger). Requires an active local session or long-running server and a publicly reachable webhook endpoint (use ngrok for local dev). Cost is per-event since each trigger starts an agent session — filter events at the MCP server level and debounce rapid bursts.

**Use when:** Real-time reaction to external events is needed while a session is active (PR review as PRs open, CI failure investigation as it happens).

---

## agent-teams

Agent Teams orchestrate multiple full Claude Code sessions that coordinate through a shared task list, each with its own context window and git worktree. The lead session spawns teammates, assigns task ownership, and synthesizes results. Best for work where teammates must communicate — cross-layer features (frontend + backend + tests each owning separate directories), multi-perspective code review (security + performance + coverage running in parallel), or competing-hypothesis debugging. Requires `agentTeams: true` in `.claude/settings.json` (experimental). Cost is roughly `(N teammates + 1) × single session` — always ask before spawning, never auto-spawn. When tasks are independent with no communication needed, use subagents (`dispatching-parallel-agents`) instead — they are 3-4x cheaper.

**Use when:** Parallel workers need to communicate or own distinct file trees; cross-layer features, multi-angle review, or parallel hypothesis investigation.

---

## How They Relate

```
Unattended / scheduled          → cloud-routines
Real-time event reaction        → event-driven-agents
  (while session is active)
Coordinated parallel sessions   → agent-teams
  (workers talk to each other)
Independent parallel tasks      → dispatching-parallel-agents (not Wave 2-3)
```

Cloud Routines and Event-Driven Agents are complementary **operating** patterns: Routines for scheduled/pull work, Channels for real-time/push work. Agent Teams is a **build** pattern for complex parallelism. Routines and Channels can both dispatch Agent Teams for complex responses (e.g., a PR webhook triggers a three-reviewer team). All three integrate with the existing Tam Quốc utility agents and mankit skills.
