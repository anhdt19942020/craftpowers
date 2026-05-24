# ECC Deep Workflow Analysis
*Researched 2026-05-24 from local clone at D:\Projects\_research\ecc*

---

## 1. Full Execution Flow: Slash Command to Output

### How slash commands work

ECC commands are plain Markdown files in `commands/`. Claude Code reads them as prompt templates when the user types the slash command. There is no router binary - the harness reads the `.md` file and injects it as a system-level instruction into the current session.

```
User types: /plan "add OAuth login"
                    |
                    v
  Claude Code reads: commands/plan.md
  (plain Markdown, no code, no dispatch table)
                    |
                    v
  The LLM receives the command content as context
  and executes the workflow described in the Markdown
```

Key design choice: **commands are prose instructions, not code**. The LLM interprets the workflow. There is no central dispatcher for commands.

### Complete /plan flow (concrete example)

```
User: /plan "add OAuth login"
  |
  v
[1] Claude Code injects commands/plan.md into context
    - Instructs model to restate requirements
    - Instructs model to identify risks
    - Instructs model to create step plan
    - Instructs model to WAIT for user confirmation before writing code
    - "Run inline by default. Do not call the Task tool or any subagent by default."
  |
  v
[2] LLM produces a plan artifact at .claude/prds/{name}.prd.md
    - Pattern grounding: grep codebase for conventions first
    - Output: phased implementation plan
    - STOPS and waits for user "yes"
  |
  v
[3] User confirms → LLM proceeds or user runs /tdd, /build-fix etc.
```

Source: `commands/plan.md`

### Agent dispatch from commands

Some commands DO spawn subagents via the Task tool. Example: `multi-workflow.md`:

```
User: /multi-workflow
  |
  v
[1] Claude reads multi-workflow command (Research → Ideation → Plan → Execute → Optimize → Review)
[2] For Execute phase with fullstack work:
      Task(subagent_type: "code-explorer")   # parallel
      Task(subagent_type: "architect")        # parallel
[3] External model calls (Codex/Gemini) via:
      run_in_background: true
      node scripts/orchestrate-worktrees.js .claude/plan/workflow.json --execute
[4] Results merged back by main Claude session
```

Source: `commands/multi-workflow.md`, `commands/multi-execute.md`

### /orchestrate command flow

The `plan-orchestrate` skill (`skills/plan-orchestrate/SKILL.md`) is ECC's most sophisticated orchestration pattern:

```
User: /orchestrate (or applies plan-orchestrate skill)
  |
  v
[Phase 0] Detect ECC install form
  - Plugin install? → {ORCH_CMD} = /everything-claude-code:orchestrate
  - Legacy install? → {ORCH_CMD} = /orchestrate
  - Agent names prefixed accordingly (plugin: "everything-claude-code:tdd-guide")
  |
  v
[Phase 1] Decompose plan document into steps
  - Look for ## Step N, ### Phase N, ordered lists, --- separators
  |
  v
[Phase 2] Tag each step and compose agent chain
  Tags: impl, build, test, db, security, docs, lookup, review, loop
  Chain rules:
  - impl + security → tdd-guide,<lang>-reviewer,security-reviewer
  - impl + db       → tdd-guide,database-reviewer,<lang>-reviewer
  - build alone     → build-error-resolver
  |
  v
[Phase 3] Emit ready-to-paste commands (generative only, never executes)
  Output: /orchestrate custom "tdd-guide,python-reviewer" "Implement auth..."
  (One line per plan step; user pastes when ready)
```

Source: `skills/plan-orchestrate/SKILL.md`

---

## 2. Skill-to-Skill Composition

### How skills are invoked

Skills are Markdown files in `skills/<name>/SKILL.md`. They are **not called programmatically**. Claude Code loads them into context when the user invokes a slash command that matches the skill, or when CLAUDE.md maps a file pattern to a skill.

From `CLAUDE.md`:
```
## Skills
| File(s)              | Skill         |
|----------------------|---------------|
| README.md            | /readme       |
| .github/workflows/*  | /ci-workflow  |

When spawning subagents, always pass conventions from the respective skill into the agent's prompt.
```

### Skill chaining patterns

There is no `invoke_skill()` API. Skills chain via three mechanisms:

**1. Prose instruction in command Markdown** (most common):
```
# commands/feature-dev.md
After planning:
- Use the tdd-workflow skill to implement with test-driven development
- Use /build-fix if build errors occur
- Use /code-review to review completed implementation
```
The model reads this and follows the sequence naturally.

**2. plan-orchestrate emits orchestrate commands** that chain agents:
```
/orchestrate custom "tdd-guide,code-reviewer,security-reviewer" "implement X"
```
Each agent's HANDOFF output feeds the next agent as input.

**3. Subagent delegation** (Task tool):
When a command or skill tells Claude to spawn a Task, the subagent gets the skill's content passed in its prompt:
```
"When spawning subagents, always pass conventions from the respective skill into the agent's prompt."
```

### Concrete chaining example: feature development

```
/feature-dev "add payment gateway"
    |
    v
    planner agent (read-only, opus model) → plan.md
    |
    v
    tdd-guide agent → writes tests first
    |
    v
    code-reviewer agent → reviews implementation
    |
    v
    security-reviewer agent (if payment-related)
    |
    v
    /pr command → opens pull request
```

---

## 3. Agent Dispatch Patterns

### Agent format

All agents live in `agents/*.md` with YAML frontmatter:

```yaml
name: planner
description: Expert planning specialist for complex features...
             Automatically activated for planning tasks.
tools: ["Read", "Grep", "Glob"]
model: opus
```

```yaml
name: code-reviewer
description: Expert code review specialist... MUST BE USED for all code changes.
tools: ["Read", "Grep", "Glob", "Bash"]
model: sonnet
```

Key: `model` field controls which Claude model the agent runs on. Planner = opus, reviewer = sonnet, observer = haiku.

### No central dispatcher

There is no `dispatch()` function or central agent registry at runtime. Instead:

1. **Claude Code reads all `~/.claude/agents/*.md`** at startup and registers them
2. **The LLM decides which agent to invoke** based on context and CLAUDE.md rules
3. **The `rules/common/agents.md` rule** (auto-injected) tells the LLM WHEN to use each agent:

```
## Immediate Agent Usage
No user prompt needed:
1. Complex feature requests - Use **planner** agent
2. Code just written/modified - Use **code-reviewer** agent
3. Bug fix or new feature - Use **tdd-guide** agent
4. Architectural decision - Use **architect** agent
```

4. **Task tool spawns subagents** with isolated context

### Data flow between agents

Agents communicate via **handoff artifacts** (files on disk):
- Planner writes plan to `.claude/plan/*.md`
- TDD guide reads plan, writes test files
- Code reviewer reads implementation files
- Orchestration session lib (`scripts/lib/orchestration-session.js`) parses worktree status files

For worktree-parallel execution:
- Each worker writes status to `## State`, `## Branch`, `## Worktree`, `## Task File`, `## Handoff File` sections in a status markdown file
- `orchestration-session.js` parses these sections with `parseWorkerStatus()`
- Main orchestrator reads all worker statuses to coordinate

---

## 4. Hook Lifecycle

### Hook event sequence for a typical session

```
[SESSION START]
    SessionStart hook fires
        → scripts/hooks/session-start.js runs
        → Reads previous session .tmp file (*.session.tmp)
        → Reads instincts from ~/.claude/homunculus/instincts/
        → Reads learned skills from ~/.claude/skills/
        → Writes assembled context to stdout (injected into Claude's context)
        → Max 8000 chars injected (configurable via ECC_SESSION_START_MAX_CHARS)

[USER SENDS MESSAGE / TOOL USE BEGINS]
    PreToolUse: Bash matcher → pre-bash-dispatcher.js
        Hook chain (sequential, each can block with exitCode != 0):
        1. pre:bash:block-no-verify    (minimal,standard,strict) - blocks --no-verify
        2. pre:bash:auto-tmux-dev      (all profiles) - tmux dev server management
        3. pre:bash:tmux-reminder      (standard,strict) - reminds about tmux
        4. pre:bash:git-push-reminder  (standard,strict) - warns before push
        5. pre:bash:commit-quality     (strict) - validates commit message
        6. pre:bash:gateguard-fact-force (standard,strict) - blocks hallucinated facts

    PreToolUse: Write matcher → doc-file-warning.js
        Warns about non-standard documentation files (exit 0, warns only)

    PreToolUse: Edit|Write matcher → config-protection.js
        Blocks edits to protected config files

    [TOOL EXECUTES]

    PostToolUse: Edit matcher → post-edit-accumulator.js
        Records edited JS/TS file paths for batch processing at Stop

    PostToolUse: Edit|Write → post-edit-format.js (standard,strict)
        Auto-formats with Biome (check --write) or Prettier

    PostToolUse: Edit → post-edit-typecheck.js (strict)
        Runs tsc type check on edited files

    PostToolUse: Bash → post-bash-dispatcher.js
        1. post:bash:command-log-audit  - logs commands for audit trail
        2. post:bash:command-log-cost   - logs for cost tracking
        3. post:bash:pr-created         (standard,strict) - detects PR creation
        4. post:bash:build-complete     (standard,strict) - detects build success

[CONTINUOUS OBSERVATION - parallel to all tool use]
    PreToolUse + PostToolUse → observe.sh (continuous-learning-v2)
        Writes observations.jsonl with tool use events
        Background Haiku agent analyzes patterns → creates/updates instinct files
        (Skipped for subagent sessions: agent_id present → exit 0)

[CLAUDE RESPONDS - Stop event]
    Stop hook fires
    → stop-format-typecheck.js (standard,strict)
       Batch formats all JS/TS files edited this response
    → suggest-compact.js
       Suggests /compact when context is high

[COMPACTION]
    PreCompact hook fires
    → pre-compact.js
       Saves current context snapshot before compaction

[SESSION ENDS]
    Stop hook (final)
    → session-end.js / evaluate-session.js
       Extracts session summary from transcript
       Writes *.session.tmp file with:
         - User messages summary
         - Files modified
         - Tools used
         - Git branch
         - Stats
       This file is read by session-start.js next session
```

### Hook profile gating

Source: `scripts/lib/hook-flags.js`

```
ECC_HOOK_PROFILE=minimal|standard|strict  (default: standard)
ECC_DISABLED_HOOKS=comma,separated,ids    (override-disable specific hooks)
```

Hooks declare which profiles they run on via `profiles: 'minimal,standard,strict'`. The dispatcher calls `isHookEnabled(hook.id, { profiles: hook.profiles })` before executing each hook.

### PreCompact hook

```
PreCompact hook fires before /compact
    → Saves current work state
    → session-start.js detects "compact" mode on next session
    → Injects note: "session ended at compaction. Any task descriptions,
      skill invocations, or ARGUMENTS-bearing slash skill should be
      re-triggered, not replayed from history."
```

---

## 5. Config and Orchestration Files

### Central wiring files

| File | Purpose |
|------|---------|
| `hooks/hooks.json` | Main hooks.json - all hook registrations for Claude Code |
| `manifests/install-profiles.json` | Named install profiles (minimal/core/developer/security/research/full) |
| `manifests/install-modules.json` | Module definitions: which skill paths each module contains |
| `manifests/install-components.json` | User-facing component IDs mapped to modules |
| `schemas/hooks.schema.json` | JSON schema for hook validation |
| `schemas/install-profiles.schema.json` | JSON schema for profiles |
| `agent.yaml` | gitagent export manifest (skill catalog + preferred model) |
| `SOUL.md` | Identity/philosophy document loaded into context |
| `CLAUDE.md` | Project instructions + skill-to-file mapping |

### hooks/hooks.json structure

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "node ... pre-bash-dispatcher.js" }] },
      { "matcher": "Write", "hooks": [{ "type": "command", "command": "node ... doc-file-warning.js" }] },
      { "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "node ... config-protection.js" }] }
    ],
    "PostToolUse": [
      { "matcher": "Edit", "hooks": [...] },
      ...
    ],
    "Stop": [ { "hooks": [{ "type": "command", "command": "node ... stop-format-typecheck.js" }] } ],
    "SessionStart": [ { "hooks": [{ "type": "command", "command": "node ... session-start.js" }] } ],
    "PreCompact": [ { "hooks": [{ "type": "command", "command": "node ... pre-compact.js" }] } ]
  }
}
```

The hook commands use a self-resolving bootstrap pattern:
```javascript
// Inline bootstrap (every hook command starts with this):
const r = (() => {
  // 1. Check CLAUDE_PLUGIN_ROOT env var
  // 2. Walk ~/.claude/plugins/marketplaces/ to find ECC
  // 3. Fallback to ~/.claude/
})();
process.argv.splice(1, 0, path.join(r, 'scripts/hooks/plugin-hook-bootstrap.js'));
require(s) // loads the actual hook script
```

This makes hooks location-independent — they work from any install path.

---

## 6. Install/Profile System

### Install CLI

Entry point: `scripts/ecc.js` (CLI) → `scripts/install-apply.js` (runtime)

```
node scripts/ecc.js install --profile developer --target claude
```

Supported targets:
- `claude` → installs to `~/.claude/` (global)
- `claude-project` → installs to `./.claude/` (per-project)
- `cursor`, `codex`, `gemini`, `opencode`, `codebuddy`, `joycode`, `qwen`, `zed`

### Profile resolution chain

```
--profile developer
    |
    v
manifests/install-profiles.json
    "developer": {
      "modules": ["rules-core", "agents-core", "commands-core",
                  "hooks-runtime", "platform-configs", "workflow-quality",
                  "framework-language", "database", "orchestration"]
    }
    |
    v
manifests/install-modules.json
    Each module defines:
    - id: "framework-language"
    - kind: "skills"
    - paths: ["skills/android-clean-architecture", "skills/angular-developer", ...]
    - targets: ["claude", "cursor", "codex", ...]
    - dependencies: ["rules-core", "agents-core", ...]
    - cost: "medium"
    - stability: "stable"
    |
    v
Target adapter (scripts/lib/install-targets/claude-home.js etc.)
    Copies files to correct location for target
    Records installed files in SQLite state store (install-state.js)
```

### State tracking

ECC uses a SQLite state store (`scripts/lib/install-state.js`) to track:
- Which files were installed
- Which profile/modules were used
- Enables `doctor` (detect drift) and `repair` (restore missing files) commands

---

## 7. Instinct Injection Flow

### The instinct lifecycle

```
[Session activity]
    observe.sh fires on every PreToolUse + PostToolUse
        → Reads stdin JSON (tool_name, tool_input, session_id)
        → Detects project: git remote URL / repo path hash → project_id
        → Appends to projects/<hash>/observations.jsonl
        → Scrubs secrets from tool I/O before writing
    
    Guards to prevent self-observation:
        - CLAUDE_CODE_ENTRYPOINT must be cli|sdk-ts|claude-desktop
        - ECC_HOOK_PROFILE != minimal
        - ECC_SKIP_OBSERVE != 1
        - agent_id must be absent (subagents don't observe)
    
    Background Haiku agent (observer.md, runs via start-observer.sh)
        → Reads observations.jsonl
        → Detects patterns: user corrections, error resolutions, repeated workflows
        → Decides: project-scoped or global?
        → Writes YAML instinct files to:
            Project: ~/.local/share/ecc-homunculus/projects/<hash>/instincts/personal/
            Global:  ~/.claude/homunculus/instincts/personal/

[Next session - SessionStart hook]
    session-start.js: summarizeActiveInstincts(observerContext)
        
        Reads from 4 directories:
        1. ~/.claude/homunculus/instincts/personal/   (global personal)
        2. ~/.claude/homunculus/instincts/inherited/  (global inherited/curated)
        3. projects/<hash>/instincts/personal/         (project personal)
        4. projects/<hash>/instincts/inherited/        (project inherited)
        
        Deduplication: project-scoped beats global when same id
        Filtering: confidence >= 0.7 (INSTINCT_CONFIDENCE_THRESHOLD)
        Limit: top 6 instincts (MAX_INJECTED_INSTINCTS)
        
        Sort: by confidence DESC, then project-scope first, then id
        
        Output format injected to stdout:
        "Active instincts:
        - [project 85%] grep-before-edit: always grep before modifying
        - [global 75%] validate-user-input: validate all user input"
```

### Instinct YAML format

```yaml
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.8
domain: code-style
source: session-observation
scope: project
project_id: a1b2c3d4e5f6
project_name: my-app

# Prefer Functional Style

## Action
Use functional patterns over classes when appropriate.

## Evidence
- Observed 5 instances of functional pattern preference
- User corrected class-based approach to functional on 2025-01-15
```

Source: `skills/continuous-learning-v2/SKILL.md`, `scripts/hooks/session-start.js`

### Learned skills injection

In addition to instincts, session-start.js also injects summaries of learned skills:
```
Available learned skills:
Reference only; apply a learned skill only when it is relevant to the current user request.
- my-custom-skill (My Custom Skill): Brief description...
```

---

## 8. Key Differentiators vs "Simple Skill File Loaded into Context"

### 1. Persistent cross-session memory

Simple approach: skills reset every session.

ECC approach:
- `session-end.js` writes `*.session.tmp` → captures user messages, files modified, tools used, git branch
- `session-start.js` reads it next session → injects summary (up to 8000 chars) as if continuing from where left off
- **Worktree-aware**: only injects sessions from the same worktree/project, not contaminating other projects

### 2. Instinct learning loop

Simple approach: static prompts.

ECC approach: every tool use is observed, patterns extracted by Haiku background agent, confidence-weighted instincts fed back on next session start. The system literally improves its own behavior over time from usage.

### 3. Profile-gated hook enforcement

Simple approach: instructions in CLAUDE.md (LLM can ignore ~20%).

ECC philosophy (from chief-of-staff agent): "Hooks over prompts for reliability: LLMs forget instructions ~20% of the time. PostToolUse hooks enforce checklists at the tool level — the LLM physically cannot skip them."

Concrete: Stop hook runs `stop-format-typecheck.js` regardless of whether Claude remembered to format. The hook does it deterministically.

### 4. Multi-model orchestration

Commands like `multi-execute.md` route to the right model:
- Frontend/UI/CSS → Gemini (design authority)
- Backend/logic → Codex (reasoning authority)
- Fullstack → parallel calls with `run_in_background: true`
- Claude integrates diffs from both models

### 5. Agent-chain composition (plan-orchestrate)

The skill decomposes a plan document into tagged steps, selects agent chains per step based on semantic tags (impl, build, test, db, security), and emits ready-to-execute `/orchestrate custom` commands. This converts unstructured plans into typed, agent-routed pipelines without human chain-composition work.

### 6. Selective install with state tracking

Simple approach: copy all files everywhere.

ECC approach: SQLite-backed state store, profile → module → path resolution, `doctor` detects drift, `repair` restores, `auto-update` reinstalls. Supports 12+ harness targets with target-specific adapters.

### 7. Hook profile gating

Three profiles (minimal/standard/strict) let users choose enforcement level:
- `minimal`: no hooks, for low-context setups
- `standard`: format, push reminders, PR detection
- `strict`: commit quality, type checking, console.log detection

---

## 9. Flow Diagrams

### Session lifecycle

```
SessionStart
    │
    ├─ Read *.session.tmp (previous session summary)
    ├─ Read instincts (project + global, confidence >= 0.7, top 6)
    ├─ Read learned skills (~/.claude/skills/)
    └─ Write assembled context to stdout → injected into Claude

    [Session running]
    │
    ├─ PreToolUse:Bash → block-no-verify, tmux, gateguard, commit-quality
    ├─ PreToolUse:Write → doc-file-warning
    ├─ PreToolUse:Edit|Write → config-protection
    ├─ [Tool executes]
    ├─ PostToolUse:Edit → accumulator, format (biome/prettier), typecheck
    ├─ PostToolUse:Bash → command-log, pr-detected, build-complete
    └─ [Observe hook: all PreToolUse+PostToolUse → observations.jsonl]
    
    Stop (each response)
    │
    ├─ Batch format+typecheck all edited JS/TS this response
    └─ suggest-compact if context high

    Stop (session end)
    │
    └─ session-end.js extracts summary → writes *.session.tmp
       Background: Haiku reads observations → writes instinct YAML
```

### Install resolution

```
ecc install --profile developer --target claude
    │
    ├─ install-profiles.json → module list
    ├─ install-modules.json  → file paths per module
    ├─ install-targets/claude-home.js → copy logic
    └─ install-state.js → SQLite record of installed files
```

### Agent chain execution

```
/orchestrate custom "planner,tdd-guide,code-reviewer" "implement OAuth"
    │
    ├─ planner reads requirements, writes plan
    ├─ HANDOFF: plan content passed to tdd-guide
    ├─ tdd-guide writes tests, writes implementation
    ├─ HANDOFF: code passed to code-reviewer
    └─ code-reviewer returns review
```

---

## 10. Patterns Worth Adapting for Mankit

| ECC Pattern | What it does | Adaptation for Mankit |
|-------------|-------------|----------------------|
| Hook profile gating (`minimal/standard/strict`) | Per-env enforcement levels | Add `ECC_HOOK_PROFILE`-equivalent to mankit hooks |
| SessionStart instinct injection | Learned behaviors fed back each session | Mankit already has SubagentStart injection; could add instinct layer |
| Stop → session-end summary | Cross-session memory without external DB | File-based session summaries per project |
| plan-orchestrate skill | Auto-compose agent chains from plan docs | Mankit `/man-cook` could emit orchestrate chains |
| Batch Stop format+typecheck | Format once at response end, not per-edit | Accumulate edited files, batch at Stop |
| observe.sh multi-layer guards | Prevent subagents observing themselves | Mankit hooks should check agent_id before firing |
| Self-resolving CLAUDE_PLUGIN_ROOT bootstrap | Hooks work from any install path | Mankit's hook resolver could use same walk-up pattern |
| SQLite install state | Track installed files, detect drift | Mankit could add `man-doctor` via state store |

---

## Sources

All findings from direct file reads of `D:\Projects\_research\ecc`:

| File | Content |
|------|---------|
| `hooks/hooks.json` | All hook registrations |
| `manifests/install-profiles.json` | 6 profiles: minimal, core, developer, security, research, full |
| `manifests/install-modules.json` | ~20 modules with paths, targets, dependencies |
| `manifests/install-components.json` | User-facing component IDs |
| `scripts/hooks/session-start.js` | SessionStart hook: instinct + session injection |
| `scripts/hooks/session-end.js` | Stop hook: session summary extraction |
| `scripts/hooks/bash-hook-dispatcher.js` | Pre/post-bash hook chain runner |
| `scripts/lib/hook-flags.js` | Profile gating logic |
| `scripts/lib/orchestration-session.js` | Worktree status parsing |
| `scripts/ecc.js` | CLI entry point |
| `scripts/install-apply.js` | Installer runtime |
| `skills/continuous-learning-v2/SKILL.md` | Instinct learning system |
| `skills/continuous-learning-v2/hooks/observe.sh` | Observation hook |
| `skills/plan-orchestrate/SKILL.md` | Agent chain composition |
| `skills/agentic-os/SKILL.md` | Multi-agent OS architecture |
| `agents/planner.md` | Planner agent (opus) |
| `agents/code-reviewer.md` | Reviewer agent (sonnet) |
| `agents/chief-of-staff.md` | Chief of staff (key design principle comments) |
| `commands/plan.md` | /plan command |
| `commands/multi-workflow.md` | Multi-model workflow |
| `commands/multi-execute.md` | Multi-model execution |
| `rules/common/agents.md` | Agent dispatch rules |
| `rules/common/hooks.md` | Hook system rules |
| `CLAUDE.md` | Architecture overview |
| `SOUL.md` | Identity + philosophy |
