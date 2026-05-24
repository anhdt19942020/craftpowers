# ECC Hook/Instinct System Analysis

## Executive Summary

ECC (Everything Claude Code) implements a comprehensive event-driven hook system across 45+ JavaScript/Python scripts that fire at every major Claude Code lifecycle event. The system uses a dispatcher-consolidation pattern — instead of registering 10+ individual hooks per event, a single "dispatcher" script multiplexes all sub-checks internally, avoiding spawning overhead. The **"instinct" concept** is a genuinely distinct subsystem: machine-learned behavioral directives injected at SessionStart as context, not guards. Instincts are scoped files (YAML/MD with frontmatter) discovered from `{project}/instincts/` and `{homunculus}/instincts/` directories, filtered by a 0.7 confidence threshold, and written to stdout to prepend Claude's session context. Guard rails (blocking hooks) operate entirely separately, enforcing git safety, config protection, and credential hygiene via exit code 2.

---

## System Structure

### Directory Layout

```
D:\Projects\_research\ecc\
├── hooks/
│   ├── hooks.json                     # Production hook graph (installed to ~/.claude/hooks/hooks.json)
│   ├── README.md                      # Hook catalog with tables per event type
│   └── memory-persistence/
│       ├── hooks.json                 # Reference lifecycle contract (not production)
│       └── README.md                  # Memory persistence documentation
├── scripts/hooks/                     # 45 executable scripts (Node.js + 1 Python)
│   ├── plugin-hook-bootstrap.js       # Root resolver; entry point for all inline commands
│   ├── run-with-flags.js              # Profile gate: only runs if ECC_HOOK_PROFILE allows
│   ├── pre-bash-dispatcher.js         # Entry point → bash-hook-dispatcher.js
│   ├── bash-hook-dispatcher.js        # Multiplexes all pre-Bash sub-checks
│   ├── post-bash-dispatcher.js        # Multiplexes post-Bash sub-checks
│   ├── post-edit-accumulator.js       # Accumulates edits for batch quality gate
│   ├── session-start.js               # SessionStart: context injection + instinct loading
│   ├── session-start-bootstrap.js     # Thin wrapper over session-start.js
│   ├── session-end.js                 # Stop: persist session summary to JSONL
│   ├── pre-compact.js                 # PreCompact: save state before compaction
│   ├── evaluate-session.js            # Stop: continuous learning pattern extraction
│   ├── observe-runner.js              # Pre/PostToolUse: tool observation for learning
│   ├── session-activity-tracker.js    # PostToolUse: record tool+file metrics
│   ├── block-no-verify.js             # PreToolUse Bash: block --no-verify flag
│   ├── config-protection.js           # PreToolUse Write: block linter config edits
│   ├── gateguard-fact-force.js        # PreToolUse Edit|Write|Bash: fact-forcing gate
│   ├── insaits-security-monitor.py    # PreToolUse: ML-based anomaly detection (Python)
│   ├── insaits-security-wrapper.js    # JS wrapper around insaits-security-monitor.py
│   ├── cost-tracker.js                # Stop: read transcript, write costs.jsonl
│   ├── ecc-statusline.js              # statusLine command (not in hooks.json)
│   ├── ecc-context-monitor.js         # PostToolUse: context exhaustion/cost/scope warnings
│   ├── ecc-metrics-bridge.js          # Metrics bridge file for statusline
│   ├── quality-gate.js                # PostToolUse Edit|Write|MultiEdit: run linters
│   ├── check-console-log.js           # Stop: audit modified files for console.log
│   ├── stop-format-typecheck.js       # Stop: batch Prettier + tsc after edits
│   ├── post-edit-format.js            # PostToolUse Edit: run Prettier on JS/TS files
│   ├── post-edit-typecheck.js         # PostToolUse Edit: run tsc --noEmit on .ts files
│   ├── post-edit-console-warn.js      # PostToolUse Edit: warn about console.log
│   ├── pre-bash-commit-quality.js     # PreToolUse Bash: git commit quality gate
│   ├── pre-bash-dev-server-block.js   # PreToolUse Bash: block npm run dev outside tmux
│   ├── pre-bash-git-push-reminder.js  # PreToolUse Bash: suggest PR after push
│   ├── pre-bash-tmux-reminder.js      # PreToolUse Bash: suggest tmux for long commands
│   ├── auto-tmux-dev.js               # PreToolUse Bash: auto-wrap dev server in tmux
│   ├── doc-file-warning.js            # PreToolUse Write: warn on non-standard .md files
│   ├── suggest-compact.js             # PreToolUse Edit|Write: suggest /compact at ~50 calls
│   ├── design-quality-check.js        # Quality design checks
│   ├── desktop-notify.js              # Desktop notification on events
│   ├── governance-capture.js          # Capture governance events
│   ├── mcp-health-check.js            # MCP server health monitoring
│   ├── post-bash-build-complete.js    # PostToolUse Bash: analyze build output
│   ├── post-bash-command-log.js       # PostToolUse Bash: log commands
│   ├── post-bash-pr-created.js        # PostToolUse Bash: log PR URL after gh pr create
│   ├── run-with-flags-shell.sh        # Shell wrapper for run-with-flags.js
│   ├── session-end-marker.js          # Session end marker
│   └── check-hook-enabled.js          # Utility: check if hook is enabled
└── tests/hooks/                       # 31 test files (one-to-one with scripts)
```

### Hook Registration Format

Hooks are registered in `hooks/hooks.json` as a JSON object keyed by event type. Each event entry is an array of matchers. Each entry contains:
- `matcher`: pipe-delimited tool names or glob (e.g., `"Bash"`, `"Edit|Write|MultiEdit"`, `"*"`)
- `hooks`: array of `{ type: "command", command: "...", timeout?: number }`
- `description`: human-readable label
- `id`: stable hook ID for disabling via `ECC_DISABLED_HOOKS`

The `command` field always uses an inline Node.js bootstrap pattern that self-resolves `CLAUDE_PLUGIN_ROOT`:

```js
node -e "const p=require('path');const r=(()=>{
  var e=process.env.CLAUDE_PLUGIN_ROOT;
  if(e&&e.trim())return e.trim();
  // ... search ~/.claude/plugins/ for ecc or everything-claude-code
  return d
})();
const s=p.join(r,'scripts/hooks/plugin-hook-bootstrap.js');
process.env.CLAUDE_PLUGIN_ROOT=r;
process.argv.splice(1,0,s);
require(s)
" node scripts/hooks/pre-bash-dispatcher.js
```

This allows the hook to work whether installed as `~/.claude` direct, `~/.claude/plugins/ecc/`, or from the marketplace cache.

---

## Hook Event Types — Full Catalog

### PreToolUse

| Hook ID | Matcher | Script | Blocking | Behavior |
|---------|---------|--------|----------|----------|
| `pre:bash:dispatcher` | `Bash` | `pre-bash-dispatcher.js` → `bash-hook-dispatcher.js` | Yes (exit 2) | Multiplexes: dev-server-block, tmux-reminder, git-push-reminder, commit-quality, block-no-verify, gateguard |
| `pre:write:doc-file-warning` | `Write` | `doc-file-warning.js` | No (warns) | Warns if writing non-standard `.md`/`.txt` file outside docs/ or skills/ |
| `pre:edit-write:suggest-compact` | `Edit\|Write` | `suggest-compact.js` | No (warns) | Every ~50 tool calls suggests manual `/compact` |
| `pre:edit-write:gateguard-fact-force` | `Edit\|Write` | `gateguard-fact-force.js` | Yes (exit 2) | Forces fact investigation before edits: list importers, affected APIs, data schemas, quote instruction |
| `pre:edit-write:config-protection` | `Edit\|Write` | `config-protection.js` | Yes (exit 2) | Blocks modification of existing linter/formatter config files |
| `pre:observe:continuous-learning` | `*` (all tools) | `observe-runner.js` | No | Records tool intent for continuous learning signals |

Sub-hooks dispatched by `bash-hook-dispatcher.js`:
- **`pre-bash-dev-server-block.js`** — Blocks `npm run dev`, `yarn dev`, `pnpm dev` etc. outside a tmux session (exit 2)
- **`pre-bash-tmux-reminder.js`** — Warns to use tmux for long-running commands (`npm test`, `cargo build`, `docker`)
- **`pre-bash-git-push-reminder.js`** — Suggests creating a PR after `git push`
- **`pre-bash-commit-quality.js`** — Runs quality gate on `git commit`: lints staged files, validates commit message format, detects console.log/debugger/secrets (exit 2 on critical)
- **`block-no-verify.js`** — Blocks `--no-verify`, `-c core.hooksPath=` on any git command (exit 2)
- **`gateguard-fact-force.js`** (Bash context) — For destructive Bash commands: demands targets list, rollback plan, quote instruction

### PostToolUse

| Hook ID | Matcher | Script | Blocking | Behavior |
|---------|---------|--------|----------|----------|
| `post:bash:dispatcher` | `Bash` | `post-bash-dispatcher.js` | No | Multiplexes: build-analysis, PR logger |
| `post:edit-write:quality-gate` | `Edit\|Write\|MultiEdit` | `quality-gate.js` | No | Runs ESLint/linters on edited files (async, non-blocking background) |
| `post:edit:format` | `Edit` | `post-edit-format.js` | No | Auto-formats JS/TS with Prettier |
| `post:edit:typecheck` | `Edit` | `post-edit-typecheck.js` | No | Runs `tsc --noEmit` on `.ts`/`.tsx` edits |
| `post:edit:console-warn` | `Edit` | `post-edit-console-warn.js` | No (warns) | Warns about `console.log` in edited files |
| `post:observe:continuous-learning` | `*` | `observe-runner.js` | No | Records tool result for learning signals |
| `post:session-activity-tracker` | `*` | `session-activity-tracker.js` | No | Records tool+file activity for ECC2 metrics |
| `post:ecc-context-monitor` | `*` | `ecc-context-monitor.js` | No (warns) | Injects agent warnings on context exhaustion, cost spikes, scope creep, tool loops |

**PostToolUseFailure** (distinct event): A catch-all `matcher: "*"` hook also handles tool failures.

### Stop (after each assistant response)

| Hook ID | Script | Behavior |
|---------|--------|----------|
| `stop:cost-tracker` | `cost-tracker.js` | Reads transcript JSONL, sums token usage, appends row to `~/.claude/metrics/costs.jsonl` |
| `stop:session-end` | `session-end.js` | Extracts session summary (user messages, tools used, files modified), writes `*-session.tmp` file |
| `stop:evaluate-session` | `evaluate-session.js` | Continuous learning: if session has 10+ user messages, signals Claude to extract reusable patterns |
| `stop:format-typecheck` | `stop-format-typecheck.js` | Batch Prettier + tsc run after accumulated edits |
| `stop:check-console-log` | `check-console-log.js` | Audits all modified files in session for `console.log` statements |

### SessionStart

| Hook ID | Script | Mode | Behavior |
|---------|--------|------|----------|
| `session:start` | `session-start-bootstrap.js` → `session-start.js` | `startup\|resume\|clear\|compact` | Loads bounded prior session context (up to 8000 chars by default), injects instincts, learned skills, project type, package manager info via stdout |

Modes come from `payload.hookName` (`SessionStart:startup`, `SessionStart:resume`, etc.) or `payload.source` field.

### PreCompact

| Hook ID | Script | Behavior |
|---------|--------|----------|
| `pre:compact` | `pre-compact.js` | Persists session state before context compaction so it survives the window truncation |

### SessionEnd (distinct from Stop)

| Hook ID | Script | Behavior |
|---------|--------|----------|
| `session:end` | `session-end.js` | Persists session-end summaries when transcript metadata is available |

### Input/Output Contract (all hooks)

- **stdin**: Claude Code passes a JSON object: `{ tool_name, tool_input, session_id, transcript_path, cwd, hook_event_name, ... }`
- **stdout**: Passed back to Claude as `hookSpecificOutput` — used by SessionStart to inject context; other hooks typically pass stdin through unchanged (exit 0)
- **stderr**: Shown to Claude as warning text without blocking
- **exit code 0**: Allow / pass-through
- **exit code 2**: Block the tool call (PreToolUse only); Claude sees the stderr message
- **MAX_STDIN**: All JS hooks cap at 1MB (`1024 * 1024` bytes); truncated payloads fail closed

---

## "Instinct" Concept

### Definition

An **instinct** is a behavioral directive stored as a YAML/Markdown file with frontmatter that gets injected into Claude's session context at `SessionStart`. Unlike hooks (which are event-driven guards), instincts are **passive nudges** — they do not block or modify tool calls, they shape Claude's priors by prepending directive text to the session.

### How It Differs from a Hook

| Dimension | Hook | Instinct |
|-----------|------|----------|
| Trigger | Tool event (PreToolUse, PostToolUse, etc.) | SessionStart only |
| Effect | Can block (exit 2), modify, or warn | Advice injection into context only |
| Persistence | Runs every tool call | Loaded once per session |
| Authorship | Shipped with ECC (JS scripts) | User-created / machine-learned |
| Format | Node.js / Python scripts | YAML/MD frontmatter files |
| Storage | `scripts/hooks/` | `{project}/instincts/` or `{homunculus}/instincts/` |

### Configuration

Instinct files use frontmatter + Markdown body:

```yaml
---
id: no-mock-data
confidence: 0.85
---
## Action
Never use mock or fake data in tests — always test against real database fixtures.
```

Fields:
- `id`: stable identifier (deduplication key)
- `confidence`: float 0.0–1.0; only instincts above `0.7` threshold are injected
- Body `## Action` section: the injected text

### Storage Directories

```
{homunculus}/instincts/personal/     # Global instincts (user preference)
{homunculus}/instincts/inherited/    # Global instincts (inherited/propagated)
{projectDir}/instincts/personal/     # Project-scoped instincts (higher priority)
{projectDir}/instincts/inherited/    # Project-scoped inherited instincts
```

Where `{homunculus}` is the ECC observer data dir (`~/.claude/ecc/observer/` or similar).

### Injection Behavior

From `session-start.js` (lines 30–397):
- `INSTINCT_CONFIDENCE_THRESHOLD = 0.7`
- `MAX_INJECTED_INSTINCTS = 6` (top 6 by confidence)
- Project-scoped instincts override global instincts with same `id`
- Sorted: confidence descending, project before global, then by id
- Output format: `Active instincts:\n- [project 85%] Never use mock data...\n- [global 72%] ...`

### Is It Real or Branding?

**Genuinely distinct concept**, not branding. The instinct system:
1. Has its own file format (not skills, not rules)
2. Has a confidence scoring system (suggests ML-generated or user-rated)
3. Has a deduplication and scoping hierarchy
4. Injected separately from session summaries and learned skills
5. Works alongside a separate `evaluate-session.js` that extracts session patterns and could generate new instinct files

The name "instinct" is intentional: these are conditioned reflexes, not explicit instructions.

---

## Guard Rails

### Destructive Command Blocking

**`gateguard-fact-force.js`** detects and blocks destructive operations:

Detected patterns (from JS tokenizer):
- `rm -rf`, `rm -fr`, `rm -Rf` (combined and split flag forms)
- `git reset --hard`, `git checkout --`, `git clean -f`, `git push --force` (not `--force-with-lease`), `git commit --amend`, `git rm -rf`
- `dd` commands with `if=` targeting disks
- SQL DML: `DROP TABLE`, `DELETE FROM`, `TRUNCATE`
- Subshell detection: `$(rm -rf)` and backtick substitutions are also scanned

When destructive command detected, demands from Claude:
1. List all files/data to be modified or deleted
2. Write one-line rollback procedure
3. Quote the user's current instruction verbatim

For Edit/Write, separately demands: list importers, affected API, data schemas, quote instruction.

### Git Safety

**`block-no-verify.js`** — Blocks bypass flags on any git command supporting `--no-verify`:
- Commands: `commit`, `push`, `merge`, `cherry-pick`, `rebase`, `am`
- Flags: `--no-verify`, `-c core.hooksPath=`
- Exit code 2 with `BLOCKED:` message
- Shell tokenizer handles quoted strings, escaped chars, combined short flags (e.g., `-nam`)
- Does NOT block `--force-with-lease` on push (considered safe)

**`pre-bash-commit-quality.js`** — Runs before `git commit`:
- Lints staged files
- Validates commit message via `-m/--message` flag parsing
- Detects `console.log`, `debugger`, secret patterns in staged content
- Exit code 2 on critical issues, 0 with warning on non-critical

### Config Protection

**`config-protection.js`** — Blocks editing existing linter/formatter configs:

Protected files include: `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `prettier.config.*`, `biome.json*`, `.ruff.toml`, `ruff.toml`, `.shellcheckrc`, `.stylelintrc*`, `.markdownlint*`

- Allows first-time creation (ENOENT check) — only blocks modifications
- Fails closed on stat errors (EACCES, EPERM, ELOOP) — treats as existing
- Uses `lstatSync` to catch dangling symlinks

### Credential/Secret Protection

**`insaits-security-monitor.py`** — Python hook using the `insa-its` SDK:
- Detection categories: credential exposure (API keys, tokens, passwords), prompt injection, hallucination indicators, behavioral anomalies (context loss, semantic drift), tool description divergence, shorthand/jargon drift
- Reads stdin JSON, extracts tool input content, runs InsAIts anomaly detection locally
- Only CRITICAL severity events block (exit 2); others write to stderr
- Writes audit events to `.insaits_audit_session.jsonl` for forensic tracing
- Opt-in: requires `ECC_ENABLE_INSAITS=1` and `pip install insa-its`
- `INSAITS_FAIL_MODE=open` (default): continues on SDK errors; `closed` blocks on errors

**`pre-bash-commit-quality.js`** also scans staged content for secret patterns before commit.

### Cost Controls

**`cost-tracker.js`** (Stop hook):
- Reads `transcript_path` from stdin, parses JSONL, sums all assistant turn token usage
- Appends one row to `~/.claude/metrics/costs.jsonl` per Stop event (cumulative per session)
- Rate table: Haiku ($0.80/$4.0 in/out per 1M), Sonnet ($3.00/$15.0), Opus ($15.00/$75.0)
- Cache pricing: creation 1.25x input rate, read 0.1x input rate

**`ecc-context-monitor.js`** (PostToolUse):
- Injects warnings into Claude's response when context nears exhaustion
- Also monitors cost anomalies, scope creep, tool loops

**`suggest-compact.js`** (PreToolUse Edit|Write):
- Warns every ~50 tool calls to run `/compact`

### Profile-Based Disabling

Hooks can be disabled without editing `hooks.json`:
- `ECC_HOOK_PROFILE=minimal|standard|strict` — each hook declares which profiles it runs under (via `run-with-flags.js` argument `minimal,standard,strict`)
- `ECC_DISABLED_HOOKS=pre:bash:block-no-verify,pre:edit-write:gateguard-fact-force` — comma-separated hook IDs to skip

---

## Hook Implementation Patterns

### Language Split

- **JavaScript (Node.js)**: 44/45 scripts — all security, quality, and lifecycle hooks
- **Python**: 1 script (`insaits-security-monitor.py`) — ML-based anomaly detection

### Context Passing

All hooks receive context identically:
```
stdin → JSON payload → { tool_name, tool_input, session_id, transcript_path, cwd, ... }
```

Key fields accessed:
- `tool_input.command` — for Bash hooks
- `tool_input.file_path` — for Write/Edit hooks
- `transcript_path` — for Stop/SessionEnd hooks (read JSONL for token counting)
- `session_id` — sanitized via `sanitizeSessionId()` for file paths

### Result Return

Scripts return results in two ways:

**Inline execution via `run-with-flags.js`**:
```js
// Script exports module.exports.run(inputOrRaw, options)
// run() returns { exitCode, stderr, stdout? }
// run-with-flags.js calls run() in-process — avoids 50-100ms spawnSync overhead
```

**Subprocess via legacy path**:
```
exit code → shell exit status
stderr → warning shown to Claude
stdout → passed as hookSpecificOutput to Claude
```

### Bootstrap Pattern

`plugin-hook-bootstrap.js` is the universal entry point for all installed hooks. It:
1. Reads stdin raw (via `fs.readFileSync(0, 'utf8')`)
2. Path-traversal checks the target script (no `../` escapes from root)
3. Finds appropriate shell binary (bash.exe, bash, sh, in priority order)
4. Spawns target script as Node.js child process with `CLAUDE_PLUGIN_ROOT` env
5. Passes stdin raw, proxies stdout/stderr/exit code

### Error Handling Philosophy

- **Fail closed** on ambiguous errors (config-protection, insaits in `closed` mode)
- **Fail open** on optional integrations (insaits default `open` mode, missing optional deps)
- **MAX_STDIN truncation**: truncated payloads → immediate exit 2 for security hooks; exit 0 for informational hooks
- Hooks never throw to the Claude Code runtime — all errors are caught and converted to exit codes

---

## Testing Strategy

### Test Infrastructure

31 test files in `tests/hooks/` — one-to-one with hook scripts. Tests use:
- Node.js built-in `assert` module
- `spawnSync` to run hook scripts as real subprocesses (full integration)
- Feeds synthetic `tool_input` JSON via stdin
- Asserts exit code and stderr content

### Test Pattern (from `block-no-verify.test.js`)

```js
function runHook(input, env = {}) {
  const result = spawnSync('node', [runner, 
    'pre:bash:block-no-verify', 
    'scripts/hooks/block-no-verify.js', 
    'minimal,standard,strict'
  ], {
    input: JSON.stringify(input),
    encoding: 'utf8',
    env: { ...process.env, ECC_HOOK_PROFILE: 'standard', ...env },
    timeout: 15000
  });
  return { code: result.status, stdout: result.stdout, stderr: result.stderr };
}

// Tests verify:
assert.strictEqual(r.code, 0, 'allows plain git commit');
assert.strictEqual(r.code, 2, 'blocks --no-verify');
assert.ok(r.stderr.includes('BLOCKED'), 'stderr contains BLOCKED');
```

All tests run through `run-with-flags.js` — same path as production. No mocking of the hook framework itself.

### Integration Tests

`tests/integration/` exists (contents not fully read). Also `tests/hooks/hooks.test.js` likely tests the hook graph schema.

`tests/hooks/test_insaits_security_monitor.py` — Python test file matching the Python hook.

---

## Key Design Decisions

### 1. Dispatcher Consolidation

Rather than 10 separate `Bash` matchers, all pre-Bash checks go through one `pre-bash-dispatcher.js` → `bash-hook-dispatcher.js`. This avoids spawning N processes per Bash call and gives a single place to short-circuit.

### 2. In-Process Execution via `module.exports.run()`

Hooks that export `run()` are called in-process by `run-with-flags.js` instead of via `spawnSync`. The comment in `config-protection.js` explicitly cites "~50-100ms spawnSync overhead" as the motivation.

### 3. Profile Gating

Three profiles (minimal, standard, strict) allow users to dial how aggressive the hook system is. `run-with-flags.js` checks `ECC_HOOK_PROFILE` against each hook's declared profiles before executing.

### 4. Fact-Forcing over Permission Gates

`gateguard-fact-force.js` is philosophically different from a "are you sure?" prompt (which LLMs answer "yes"). It forces Claude to produce concrete evidence: importers, rollback plans, affected APIs. The investigation process itself creates awareness.

### 5. Instinct Confidence Scoring

The 0.7 threshold and max-6 cap prevent instinct injection from overwhelming Claude's context. Project scope overrides global, ensuring per-project fine-tuning. The system is designed for machine-generated instincts (from `evaluate-session.js` patterns) as well as user-authored ones.

### 6. Root Resolution Bootstrap

The inline bootstrap in every command entry in `hooks.json` searches multiple plugin install locations (`~/.claude/plugins/ecc/`, `~/.claude/plugins/cache/ecc/...`). This makes hooks portable across manual install, plugin manager, and marketplace cache paths.

---

## Comparison with Craftpowers

### Craftpowers Hook Architecture (`D:\Projects\craftpowers\hooks\`)

Craftpowers implements its own hook system with similar coverage but different technology choices:

| Dimension | ECC | Craftpowers |
|-----------|-----|-------------|
| Language | JavaScript (Node.js) primary | Python primary |
| Hook file count | 45 scripts | ~25 scripts |
| Registration | `hooks/hooks.json` (plugin installed) | `hooks/hooks.json` (local project) |
| Event types used | PreToolUse, PostToolUse, PostToolUseFailure, Stop, SessionStart, PreCompact, SessionEnd | SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, ConfigChange, PermissionRequest, PreCompact, PostCompact, SubagentStop, StopFailure, WorktreeCreate |
| Additional events | None beyond Claude Code standard | `SubagentStop`, `StopFailure`, `WorktreeCreate`, `UserPromptSubmit`, `ConfigChange`, `PermissionRequest` — hooks unique to Craftpowers' use of newer Claude Code event types |
| Instinct system | Yes — file-based confidence-scored behavioral injection | No equivalent |
| Dispatcher pattern | Yes (pre-bash-dispatcher consolidates) | One Python script per event (`pre_tool_use.py`, `post_tool_use.py`, etc.) |
| Profile gating | `ECC_HOOK_PROFILE` + `ECC_DISABLED_HOOKS` | `.man.json` per-project config |
| Config protection | ESLint/Prettier/Biome/Ruff file blocking | `config_change_gate.py` — blocks config changes via `ConfigChange` event |
| Security scanning | `insaits-security-monitor.py` (ML SDK) | `security-gate.py`, `credential-scanner.py` (custom patterns) |
| Cost tracking | `cost-tracker.js` reads transcript JSONL | No equivalent (context-tracker.py tracks context budget, not cost) |
| Continuous learning | `evaluate-session.js` + `observe-runner.js` | No equivalent |
| Test coverage | 31 test files, subprocess integration tests | No dedicated tests/hooks/ directory found |

### Craftpowers-Specific Events Not in ECC

Craftpowers uses `SubagentStop`, `StopFailure`, `WorktreeCreate`, `UserPromptSubmit`, `ConfigChange`, and `PermissionRequest` events — indicating it uses a newer or extended version of the Claude Code hook API. ECC's `hooks.json` only registers against the 5 standard events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `SessionStart`, `PreCompact`).

### Craftpowers Hooks Directory Structure

```
hooks/
├── hooks.json                    # Event registry (Python command paths)
├── claude/                       # Event handlers (thin dispatch wrappers)
│   ├── pre_tool_use.py           # PreToolUse dispatcher
│   ├── post_tool_use.py          # PostToolUse dispatcher
│   ├── session_start.py          # SessionStart
│   ├── stop.py                   # Stop
│   ├── user_prompt_submit.py     # UserPromptSubmit
│   ├── config_change_gate.py     # ConfigChange
│   ├── permission_request_gate.py # PermissionRequest
│   ├── subagent_stop_gate.py     # SubagentStop
│   ├── stop_failure.py           # StopFailure
│   ├── worktree_provision.py     # WorktreeCreate
│   └── compact_hooks.py          # PreCompact + PostCompact
└── lib/                          # Shared Python modules
    ├── security_gate.py          # Security checks
    ├── credential_scanner.py     # Credential detection
    ├── config_change_gate.py     # Config protection logic
    ├── session_summary.py        # Session persistence
    ├── context_tracker.py        # Context budget monitoring
    ├── workflow_state.py         # Workflow state management
    └── ...
```

Craftpowers' Python-based approach produces cleaner per-module separation vs ECC's JS-first dispatcher pattern. ECC's instinct system, cost tracking via transcript parsing, and continuous learning pattern extraction have no Craftpowers equivalent and represent ECC's most differentiated features.

---

## Sources

All findings are from direct file reads of `D:\Projects\_research\ecc\` (accessed 2026-05-24):

1. `D:\Projects\_research\ecc\hooks\README.md` — Hook catalog, event table, installation instructions
2. `D:\Projects\_research\ecc\hooks\hooks.json` — Production hook graph with full command inlining
3. `D:\Projects\_research\ecc\hooks\memory-persistence\hooks.json` — Lifecycle contract reference
4. `D:\Projects\_research\ecc\hooks\memory-persistence\README.md` — Memory persistence documentation
5. `D:\Projects\_research\ecc\scripts\hooks\block-no-verify.js` — Git bypass blocking
6. `D:\Projects\_research\ecc\scripts\hooks\config-protection.js` — Linter config protection
7. `D:\Projects\_research\ecc\scripts\hooks\cost-tracker.js` — Session cost tracking
8. `D:\Projects\_research\ecc\scripts\hooks\gateguard-fact-force.js` — Destructive command gate
9. `D:\Projects\_research\ecc\scripts\hooks\insaits-security-monitor.py` — ML security monitoring
10. `D:\Projects\_research\ecc\scripts\hooks\session-start.js` — SessionStart + instinct injection
11. `D:\Projects\_research\ecc\scripts\hooks\session-end.js` — Session summary persistence
12. `D:\Projects\_research\ecc\scripts\hooks\evaluate-session.js` — Continuous learning
13. `D:\Projects\_research\ecc\scripts\hooks\ecc-statusline.js` — Statusline command
14. `D:\Projects\_research\ecc\scripts\hooks\pre-bash-dispatcher.js` — Bash hook multiplexer
15. `D:\Projects\_research\ecc\scripts\hooks\plugin-hook-bootstrap.js` — Universal entry point
16. `D:\Projects\_research\ecc\scripts\hooks\run-with-flags.js` — Profile gate + in-process runner
17. `D:\Projects\_research\ecc\tests\hooks\block-no-verify.test.js` — Hook test pattern
18. `D:\Projects\craftpowers\hooks\hooks.json` — Craftpowers hook registry (comparison)
