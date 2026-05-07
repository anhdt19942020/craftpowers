# craftpowers

**A complete software development methodology for AI coding agents** — combining the battle-tested workflows of [Superpowers](https://github.com/obra/superpowers) with the craft-focused skills from [Matt Pocock](https://github.com/mattpocock/skills), plus automated security hooks and specialized agents.

> *Your coding agent doesn't just write code — it thinks, plans, stress-tests, builds with TDD, reviews its own work, and ships safely.*

---

## What craftpowers does for you

Most AI coding agents jump straight to writing code. craftpowers changes that. It gives your agent a **complete development process** — the same discipline a senior engineer follows, enforced automatically:

- **Reads your docs first** — scans `docs/**/*.md` for existing specs, architecture notes, and feature documentation before brainstorming or planning, so it doesn't re-ask questions already answered or contradict decisions already made
- **Thinks before coding** — asks what you actually need, stress-tests the design, explores multiple approaches
- **Plans in small steps** — breaks work into 2-5 minute tasks with file paths, verification steps, and clear acceptance criteria
- **Builds with TDD** — writes the test first, watches it fail, then makes it pass
- **Reviews its own work** — dispatches specialized subagents for code review, security audit, and test quality
- **Guards against mistakes** — blocks dangerous commands, detects hardcoded credentials, warns when context is running low
- **Keeps docs in sync** — after implementation, updates existing documentation in-place to match the new code (no changelog bloat, just accurate docs)
- **Ships cleanly** — verifies tests pass, chooses the right merge strategy, cleans up branches

---

## The Workflow

```
 Idea → Brainstorm → Plan → Build → Review → Ship
  │         │          │       │        │       │
  │    stress-test   tasks   TDD    agents   verify
  │    explore       PRD    code    secure   merge
  │    ADR           issues  test   debug    cleanup
```

| Phase | What happens | Key skills |
|-------|-------------|------------|
| **Think** | Refine ideas, challenge assumptions, explore alternatives | brainstorming, adversarial-design, design-exploration |
| **Plan** | Break into tasks, create PRDs, file GitHub issues | writing-plans, to-prd, to-issues |
| **Build** | TDD cycle, subagent dispatch, parallel execution | test-driven-development, subagent-driven-development, executing-plans |
| **Review** | Code review, security audit, debug, verify completion | requesting-code-review, systematic-debugging, verification-before-completion |
| **Ship** | Merge strategy, cleanup, branch management | finishing-a-development-branch |
| **Maintain** | Refactoring, pre-commit hooks, architecture records | structured-refactoring, architecture-decision-records |

---

## What's Inside

### 25 Skills

Skills are behavioral instructions that shape how your agent works. They activate automatically based on context or when you invoke them directly.

<details>
<summary><b>Think</b> — before any code</summary>

| Skill | What it does |
|-------|-------------|
| **brainstorming** | Socratic design refinement — asks questions one at a time, proposes 2-3 approaches, validates design section by section |
| **adversarial-design** | Stress-tests your design by relentlessly questioning every decision before you commit |
| **design-exploration** | Spawns 3+ subagents to create radically different designs, then compares trade-offs |
| **ubiquitous-language** | Extracts a DDD-style glossary from the conversation — standardizes domain language before coding |
| **architecture-decision-records** | Captures architectural decisions as ADRs — finds improvement opportunities and documents the "why" |

</details>

<details>
<summary><b>Plan</b> — after design</summary>

| Skill | What it does |
|-------|-------------|
| **writing-plans** | Creates implementation plans with 2-5 minute tasks, exact file paths, code snippets, and verification steps |
| **to-prd** | Converts conversation context into a structured PRD and submits it as a GitHub issue |
| **to-issues** | Decomposes a plan into independent vertical-slice GitHub issues |

</details>

<details>
<summary><b>Build</b> — during coding</summary>

| Skill | What it does |
|-------|-------------|
| **test-driven-development** | Enforces RED → GREEN → REFACTOR. Deletes code written before tests exist |
| **subagent-driven-development** | Dispatches a subagent per task with two-stage review (spec compliance + code quality) |
| **executing-plans** | Loads the plan document and executes all tasks with checkpoints |
| **dispatching-parallel-agents** | Runs independent tasks concurrently via parallel subagents |
| **using-git-worktrees** | Creates isolated git worktrees for parallel feature development |
| **nodejs-patterns** | Node.js best practices from Matteo Collina (Fastify creator): async, streams, error handling, testing, TypeScript type stripping, caching, profiling, graceful shutdown — 15 rule files |
| **websocket-patterns** | WebSocket/Socket.IO engineering: rooms, namespaces, presence, scaling with Redis, sticky sessions, security, rate limiting, Fastify integration — 6 rule files |

</details>

<details>
<summary><b>Review</b> — after coding</summary>

| Skill | What it does |
|-------|-------------|
| **systematic-debugging** | 4-phase root-cause analysis: understand → hypothesize → trace → confirm |
| **verification-before-completion** | Requires fresh evidence (test output, screenshots) before claiming a task is done |
| **requesting-code-review** | Pre-review checklist and dispatches code-reviewer subagent |
| **receiving-code-review** | Structured process for responding to review feedback with technical rigor |

</details>

<details>
<summary><b>Ship & Maintain</b></summary>

| Skill | What it does |
|-------|-------------|
| **finishing-a-development-branch** | Verify tests → choose merge/PR/keep/discard → execute → clean up worktree |
| **structured-refactoring** | Martin Fowler approach: interview → tiny commits → GitHub issues |
| **setup-pre-commit** | Installs Husky pre-commit hooks with lint-staged, type checking, and tests |
| **git-guardrails-claude-code** | Adds hooks to block dangerous git commands before execution |
| **writing-skills** | TDD-based process for creating and testing new skills |
| **using-man** | Meta skill — teaches the agent how to discover and use all other skills |

</details>

---

### 5 Agents

Specialized subagents that are dispatched automatically when relevant, or invoked directly.

| Agent | Purpose | When it activates |
|-------|---------|-------------------|
| **code-reviewer** | Reviews code changes against the implementation plan | After completing a planned step |
| **secure-reviewer** | OWASP Top 10 security audit (injection, auth, crypto, access control) | When touching auth, input handling, APIs, file uploads |
| **test-engineer** | Evaluates test coverage, quality, isolation, and assertion strength | After writing or modifying tests |
| **debugger** | 5-phase systematic root-cause analysis | Complex bugs, intermittent failures, regressions |
| **doc-writer** | Generates README, API docs, inline comments (runs on Haiku for cost efficiency) | When documentation is needed |

---

### 4 Hooks (automatic protection)

Hooks run automatically in the background — no action needed from you.

| Hook | Trigger | What it does |
|------|---------|-------------|
| **session-start** | Every new session | Injects craftpowers context so the agent knows its skills are available |
| **security-gate** | Before any Bash command | Blocks dangerous commands: `rm -rf`, force-push, `DROP TABLE`, `chmod 777`, `curl \| bash`, fork bombs, and 11 more patterns |
| **credential-scanner** | After every Write/Edit | Scans written code for hardcoded credentials (AWS keys, API tokens, private keys, passwords) with false-positive filtering |
| **context-tracker** | Every user message | Estimates context window usage and warns at 70% (yellow) and 87% (critical) so you can `/compact` before losing context |

---

### Commands

Quick-access shortcuts for common workflows:

| Command | What it does |
|---------|-------------|
| `/man-brainstorm` | Start the brainstorming → design → spec workflow |
| `/man-plan` | Write an implementation plan from a design |
| `/man-fix` | Start systematic debugging for a bug |
| `/man-ship` | Finish a branch — verify, merge, cleanup |
| `/man-update` | Update man: pull latest → reinstall → verify |
| `/man-check` | Health check: verify all hooks, agents, permissions are working |

---

## Installation

### Option 1: Plugin install (recommended)

```bash
/install-plugin https://github.com/anhdt19942020/craftpowers
```

Then run the full setup:

```bash
python scripts/install.py
```

### Option 2: Clone directly

```bash
git clone https://github.com/anhdt19942020/craftpowers ~/.claude/plugins/man
python ~/.claude/plugins/man/scripts/install.py
```

### What install.py does

The install script is **idempotent** — safe to run multiple times. It configures:

1. **Hooks** — writes security-gate, credential-scanner, and context-tracker to `~/.claude/settings.json`
2. **Permissions** — adds ~70 safe permission rules (git read ops, test runners, build tools) to reduce interruption prompts
3. **Agents** — links `~/.claude/agents/` → `craftpowers/agents/` (junction on Windows, symlink on Unix)
4. **Commands** — links `~/.claude/commands/` → `craftpowers/commands/`
5. **`.claudeignore`** — creates a template to exclude build outputs, dependencies, logs, and lock files from context (saves tokens every session)

### Verify your setup

After installing, restart Claude Code and run:

```
/man-check
```

This runs 22 checks across 6 categories: installation, settings, hook scripts, hook paths, agents, and hook smoke tests. Every check should show `[PASS]`.

### Updating

```
/man-update
```

Pulls the latest code, re-runs install, and verifies everything works.

---

## Platform Support

craftpowers works with multiple AI coding tools:

| Platform | Status | Notes |
|----------|--------|-------|
| **Claude Code** | Full support | Skills, hooks, agents, commands |
| **Cursor** | Skills only | Via plugin system |
| **Gemini CLI** | Skills + tool mapping | Automatic via GEMINI.md |
| **Copilot CLI** | Skills + tool mapping | See `references/copilot-tools.md` |
| **Codex** | Skills + tool mapping | See `references/codex-tools.md` |
| **OpenCode** | Skills only | Via plugin system |

---

## Token Optimization

craftpowers includes several built-in token-saving features:

- **`.claudeignore`** — auto-generated by `install.py`, excludes `node_modules/`, `dist/`, `*.log`, lock files, and other low-signal content from context
- **Permission allowlists** — ~70 pre-approved rules eliminate permission prompt round-trips
- **Context checkpoints** — executing-plans and subagent-driven-development auto-compact at natural breakpoints (every 3 tasks or after long review loops)
- **Context tracker hook** — warns at 70% and 87% context usage so you can `/compact` before auto-compaction
- **Session summary** — reports token usage and RTK savings at the end of each workflow

### Recommended companion tools

These external tools stack with craftpowers for additional savings:

| Tool | Savings | What it does |
|------|---------|-------------|
| [RTK](https://github.com/rtk-ai/rtk) | ~60% CLI output | Compresses command output before it enters context |
| [Context Mode](https://github.com/mksglu/context-mode) | ~98% tool output | Routes large outputs to sandbox, only summaries enter context |
| [MCPlex](https://github.com/ModernOps888/mcplex) | ~97% tool definitions | Hides MCP tools behind 3 meta-tools, loads on-demand |
| [Caveman](https://github.com/JuliusBrussee/caveman) | ~65% output | Enforces terse, filler-free responses |
| [Headroom](https://github.com/chopratejas/headroom) | ~87% compression | Lossless compression of everything the agent reads |

Combined stack: **~58% total savings** — makes the 200K context window function like ~350K.

---

## Philosophy

- **Design before code** — stress-test ideas before committing to an implementation
- **Test-Driven Development** — write the test first, always
- **Systematic over ad-hoc** — process beats guessing
- **Evidence over claims** — verify with real output before asserting completion
- **Craft over vibe** — deliberate technique, not vibe coding

---

## Quick Reference

See [`QUICK_REFERENCE.md`](./QUICK_REFERENCE.md) for a one-page lookup of all skills, agents, commands, and hooks.

---

## Credits

craftpowers is built on the foundation of:

- **[Jesse Vincent](https://blog.fsck.com)** & **[Prime Radiant](https://primeradiant.com)** — creator of [Superpowers](https://github.com/obra/superpowers), the methodology and workflow foundation
- **[Matt Pocock](https://github.com/mattpocock)** — creator of [skills](https://github.com/mattpocock/skills), the craft-focused toolset for software quality
- **[Matteo Collina](https://github.com/mcollina)** — creator of [mcollina/skills](https://github.com/mcollina/skills), Node.js best practices (Fastify creator, Node.js TSC member)
- **[Jeff Allan](https://github.com/Jeffallan)** — creator of [claude-skills](https://github.com/Jeffallan/claude-skills), WebSocket engineer skill

If craftpowers is useful to you, please consider:
- Star [Superpowers](https://github.com/obra/superpowers)
- Star [mattpocock/skills](https://github.com/mattpocock/skills)
- Star [mcollina/skills](https://github.com/mcollina/skills)
- [Sponsor Jesse Vincent](https://github.com/sponsors/obra)

---

## License

MIT License — see [LICENSE](./LICENSE) for details.
