# craftpowers Quick Reference

## The Workflow

```
Idea → /man-brainstorm → /man-plan → TDD → review → /man-ship
```

---

## Skills by Phase

### Think — before any code

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `brainstorming` | "let's brainstorm", "I have an idea" | Socratic design → spec doc |
| `adversarial-design` | "stress-test my plan", "challenge this" | Relentless questioning to find gaps |
| `design-exploration` | "explore approaches", "design it twice" | 3+ radically different designs via subagents |
| `ubiquitous-language` | "create a glossary", "define domain terms" | DDD-style glossary from conversation |
| `architecture-decision-records` | "write an ADR", "find architecture improvements" | ADR proposals and deepening opportunities |

### Plan — after design

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `writing-plans` | "write an implementation plan" | 2–5 min tasks with file paths + verification steps |
| `to-prd` | "create a PRD", "write a product spec" | Conversation → GitHub issue PRD |
| `to-issues` | "break this into tickets" | Plan → independent vertical-slice GitHub issues |

### Build — during coding

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `test-driven-development` | "use TDD", "write tests first" | Enforced RED → GREEN → REFACTOR cycle |
| `subagent-driven-development` | "execute with subagents" | Per-task subagent dispatch with 2-stage review |
| `executing-plans` | "execute the plan" | Loads plan, executes all tasks with checkpoints |
| `dispatching-parallel-agents` | "run in parallel", "do these simultaneously" | Independent tasks to parallel subagents |
| `using-git-worktrees` | "create a worktree", "isolate this branch" | Isolated git worktrees for parallel feature work |
| `nodejs-patterns` | Auto-activates on Node.js, Fastify, Express code | Matteo Collina's Node.js best practices (15 rule files) |
| `websocket-patterns` | Auto-activates on WebSocket, Socket.IO code | WebSocket engineering: rooms, scaling, security (6 rule files) |

### Review — after coding

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `systematic-debugging` | "debug this", "find the root cause" | 4-phase root-cause analysis before any fix |
| `verification-before-completion` | "verify this is done", "check completion" | Requires fresh evidence before claiming complete |
| `requesting-code-review` | "review my code", "before I merge" | Dispatches code-reviewer subagent |
| `receiving-code-review` | "I got review feedback" | Technical rigor in responding to feedback |

### Ship

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `finishing-a-development-branch` | "I'm done", "ready to ship" | Verify → options → execute → clean up |

### Maintain

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `structured-refactoring` | "plan a refactor", "improve this safely" | Martin Fowler approach with tiny commits |
| `setup-pre-commit` | "set up pre-commit", "add Husky" | Lint-staged + Prettier + typecheck at commit time |
| `git-guardrails-claude-code` | "add git safety", "protect against force-push" | Hook blocking force-push, reset --hard, etc. |
| `writing-skills` | "create a skill", "edit a skill" | TDD-based process for writing new skills |

---

## Commands

| Command | Invokes | Use when |
|---------|---------|----------|
| `/man-brainstorm` | brainstorming | Starting something new |
| `/man-plan` | writing-plans | Ready to write tasks |
| `/man-fix` | systematic-debugging | Stuck on a bug |
| `/man-ship` | finishing-a-development-branch | Ready to merge |
| `/man-update` | git pull | Updating craftpowers |

---

## Agents

| Agent | Model | When to use |
|-------|-------|-------------|
| `code-reviewer` | inherit | After completing a planned step |
| `secure-reviewer` | inherit | Auth, input handling, API integrations, file uploads |
| `test-engineer` | inherit | After writing tests — check coverage and quality |
| `debugger` | inherit | Complex bugs, intermittent failures, regressions |
| `doc-writer` | haiku | READMEs, API docs, inline comments |

---

## Hooks (automatic)

| Hook | Event | What it does |
|------|-------|-------------|
| `session-start` | SessionStart | Injects craftpowers context into every session |
| `security-gate` | PreToolUse: Bash | Blocks dangerous commands (rm -rf, force-push, etc.) |
| `credential-scanner` | PostToolUse: Write/Edit | Warns on hardcoded credentials in written files |
| `context-tracker` | UserPromptSubmit | Warns when context window approaches limit |

---

## Setup

```bash
# Full setup (hooks, permissions, agents, commands, .claudeignore)
python scripts/install.py

# Verify everything works
/man-check
```

---

## Token Optimization

**Built-in:**
- `.claudeignore` — excludes build outputs, deps, logs from context (auto-created by install.py)
- Permission allowlists — ~70 rules, eliminates permission prompt round-trips
- Context checkpoints — auto-compact every 3 tasks during plan execution
- Context tracker — warns at 70% and 87% usage
- Session summary — reports token/RTK stats at end of workflow

**Companion tools (install separately):**

| Tool | Savings | Install |
|------|---------|---------|
| [RTK](https://github.com/rtk-ai/rtk) | ~60% CLI | `cargo install rtk` |
| [Context Mode](https://github.com/mksglu/context-mode) | ~98% tool output | Claude Code plugin |
| [MCPlex](https://github.com/ModernOps888/mcplex) | ~97% tool defs | MCP gateway |
| [Caveman](https://github.com/JuliusBrussee/caveman) | ~65% output | `curl install` |
| [Headroom](https://github.com/chopratejas/headroom) | ~87% reads | CLI tool |

---

## Core Principles

- **Evidence over claims** — verify before asserting completion
- **Root cause first** — never fix without tracing the cause
- **TDD everywhere** — watch the test fail before making it pass
- **Design before code** — stress-test ideas, not implementations
- **Systematic over ad-hoc** — process beats guessing
- **Surgical changes** — touch only what you must, clean up only your own mess
- **Simplicity first** — minimum code that solves the problem, nothing speculative
