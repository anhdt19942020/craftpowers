# ECC-Inspired Improvement Proposals for Craftpowers

**Date:** 2026-05-24
**Based on:** ECC reverse engineering analysis (3 research reports + synthesis)

## Summary

- **12 total proposals:** 4 quick wins, 4 medium effort, 4 strategic
- **Estimated total effort:** 40-80 hours
- **Highest-impact proposals:** Instinct System (P1), Behavioral Compliance Testing (P2), Dispatcher Consolidation (P3)

---

## Quick Wins (implement now — each < 4 hours)

### Proposal 1: Universal Prompt Defense Baseline for Agents

**What:** Add a standardized security preamble to all 14 Craftpowers agent definitions — an 8-10 bullet block covering prompt injection defense, credential handling, destructive action awareness, and output sanitization.

**Why:** ECC puts this in every single agent (60/60). It's defense-in-depth: even if a skill or hook fails, the agent itself has security awareness baked in. Craftpowers agents currently have no standardized security layer.

**ECC Reference:** Every agent in `agents/*.md` starts with a `## Prompt Defense Baseline` section containing 8 bullets.

**Priority:** P0 (must-have — low effort, high security value)
**Effort:** S (< 4h) — write template once, apply to 14 agents
**Impact:** Security hardening across all agent dispatches. Prevents credential leaks, prompt injection, and destructive actions at the agent level.

**Implementation Sketch:** Create a shared security preamble template. Prepend it to the body of every agent `.md` file. Include: never expose credentials, validate file paths before write, refuse destructive git commands unless explicitly instructed, never execute user-provided code without sandboxing, flag suspicious tool inputs.

---

### Proposal 2: Catalog CI Tests

**What:** Add automated tests that verify: (a) number of skill directories matches documented count, (b) every SKILL.md has required frontmatter fields, (c) every agent `.md` has required frontmatter, (d) `roles.json` references only agents that exist on disk.

**Why:** ECC has `catalog.test.js` (count parity) and `command-frontmatter.test.js` (schema validation). These catch drift between code and docs — a common problem as skill/agent count grows. Craftpowers has no equivalent.

**ECC Reference:** `tests/catalog.test.js`, `tests/command-frontmatter.test.js`

**Priority:** P1 (should-have — catches drift early)
**Effort:** S (< 4h) — simple test file, run in CI
**Impact:** Prevents broken skill/agent references, missing frontmatter, doc drift. Scales with skill count.

**Implementation Sketch:** Write a test file (`tests/catalog.test.ts` or `.js`) that: globs `skills/*/SKILL.md`, counts them, compares to documented count; parses each SKILL.md frontmatter for required fields (`name`, `description`); globs `agents/*.md`, parses frontmatter; loads `roles.json`, verifies every referenced agent file exists.

---

### Proposal 3: Gateguard Fact-Forcing for Destructive Actions

**What:** Upgrade Craftpowers' destructive command blocking from "block and warn" to "demand evidence before allowing." When a destructive action is detected (`rm -rf`, `git reset --hard`, `DROP TABLE`, etc.), instead of just blocking, require the agent to provide: (1) specific targets, (2) rollback plan, (3) verbatim user instruction quote.

**Why:** ECC's `gateguard-fact-force.js` is smarter than a simple blocker — it forces the agent to prove it understands what it's destroying and that the user actually asked for it. This catches hallucinated destructive actions that a simple confirmation dialog wouldn't catch.

**ECC Reference:** `scripts/hooks/gateguard-fact-force.js` — detects `rm -rf`, `git reset --hard`, `git checkout --`, `git clean -f`, `git push --force`, `DROP TABLE`, `DELETE FROM`, `TRUNCATE`, `dd` to disks. Also handles subshell patterns.

**Priority:** P0 (must-have — direct safety improvement)
**Effort:** S (< 4h) — modify existing hook script
**Impact:** Stronger safety gate for destructive operations. Evidence-based approval > confirmation dialog.

**Implementation Sketch:** Modify the existing PreToolUse hook to detect destructive patterns (ECC's regex list is a good starting point). On detection, return a stderr message demanding: target files/tables, rollback method, exact user instruction. Block (exit 2) until evidence is provided.

---

### Proposal 4: Cost Tracking via Transcript Parsing

**What:** Add a Stop hook that parses the session transcript JSONL, sums token usage by model, and appends to a `~/.claude/metrics/costs.jsonl` file. Expose via a `/man-costs` skill.

**Why:** ECC's `cost-tracker.js` gives users visibility into per-session token costs. Craftpowers has no cost visibility — users have no idea how much a session costs until they check the Anthropic dashboard.

**ECC Reference:** `scripts/hooks/cost-tracker.js` — reads transcript at every Stop event, sums tokens by model, applies rates (Sonnet $3/$15 per 1M).

**Priority:** P1 (should-have — user value)
**Effort:** S (< 4h) — single hook script + simple skill
**Impact:** Users see cost per session, per day, per week. Enables cost budgeting and optimization decisions.

**Implementation Sketch:** Add a Stop hook that reads `transcript_path` from stdin JSON, parses JSONL for `usage` fields, sums `input_tokens` and `output_tokens` by model, applies current pricing, appends to metrics file. Create simple `/man-costs` skill to display.

---

## Medium Effort (next sprint — each 4h-2d)

### Proposal 5: Instinct System — Behavioral Priors

**What:** Implement an instinct system: YAML/MD files with confidence scores that get injected into session context at SessionStart. Instincts are passive behavioral nudges (not guards), scoped per-project and per-user.

**Why:** This is ECC's most novel innovation. Instincts fill a gap between rules (static, always-on) and hooks (event-driven, blocking). They're learned behavioral preferences — "this project prefers integration tests over mocks" or "always check TypeScript strict mode." No Craftpowers equivalent exists.

**ECC Reference:** 
- Format: `instincts/{personal,inherited}/*.md` with `id`, `confidence` frontmatter
- Injection: `session-start.js` reads instincts, filters by 0.7 confidence threshold, caps at 6, sorts by confidence × scope priority
- Output: Prepended to session context as `Active instincts:\n- [project 85%] ...`

**Priority:** P0 (must-have — highest novelty, genuine innovation)
**Effort:** M (1-2 days) — instinct file format, SessionStart injection logic, management skill
**Impact:** Sessions become personalized and project-aware without manual configuration. System learns over time.

**Implementation Sketch:**
1. Define instinct file format (YAML frontmatter: `id`, `confidence`, `scope`)
2. Add instinct discovery in SessionStart hook: scan `{project}/instincts/` and `~/.claude/instincts/`
3. Filter by confidence threshold (0.7), cap at 6, sort by confidence
4. Output as `Active instincts:` block via stdout
5. Create `/man-instinct` skill to create, list, edit, delete instincts
6. (Future) Auto-generate instincts from session evaluation

---

### Proposal 6: Behavioral Compliance Testing for Skills

**What:** Build a `skill-comply` equivalent: a tool that programmatically tests whether agents actually follow skill instructions. Generate scenarios, run `claude -p` with the skill loaded, capture tool traces, and use LLM classification to determine compliance.

**Why:** ECC's `skill-comply` is the most advanced skill quality mechanism we've seen. Craftpowers' `man-eval` requires human A/B evaluation — it doesn't scale. As Craftpowers grows past 50 skills, automated compliance testing becomes essential.

**ECC Reference:** `scripts/skill-comply/` — Python tool that generates scenarios per skill, runs `claude -p`, captures traces, LLM-classifies compliance rate.

**Priority:** P1 (should-have — quality at scale)
**Effort:** M (1-2 days) — scenario generator, test runner, compliance classifier
**Impact:** Automated skill quality validation. Catches skill regressions. Enables confident skill updates.

**Implementation Sketch:**
1. For each skill, extract `## When to Use` and key behavioral requirements
2. Generate 3-5 test scenarios per skill (adversarial + golden path)
3. Run `claude -p "scenario text"` with skill loaded
4. Capture tool trace (which tools called, in what order)
5. LLM-classify: did the agent follow the skill's instructions?
6. Output compliance report with pass/fail per scenario

---

### Proposal 7: Hook Dispatcher Consolidation

**What:** Consolidate multiple PreToolUse hooks into a single dispatcher script that multiplexes all sub-checks internally, instead of spawning separate processes per hook.

**Why:** ECC's `pre-bash-dispatcher.js` runs 5+ checks in a single process spawn. Craftpowers spawns a separate Python process per hook registration. At high tool-call frequency, this adds 50-100ms × N hooks overhead per tool call.

**ECC Reference:** `scripts/hooks/pre-bash-dispatcher.js` — single entry point, internally dispatches to dev-server-block, tmux-reminder, commit-quality, block-no-verify, gateguard checks.

**Priority:** P1 (should-have — performance)
**Effort:** M (4h-1d) — refactor existing hooks into dispatcher pattern
**Impact:** Reduced per-tool-call latency. More responsive agent experience. Scales better as hook count grows.

**Implementation Sketch:**
1. Create `pre_tool_use_dispatcher.py` that imports all existing PreToolUse checks as functions
2. Single stdin parse, single JSON load
3. Run all checks sequentially in-process
4. Return first blocking result (exit 2) or pass (exit 0)
5. Update `hooks.json` to register single dispatcher instead of N individual hooks

---

### Proposal 8: Conversation Analyzer Meta-Agent

**What:** Create a `conversation-analyzer` agent that watches completed session transcripts and suggests: new instincts, hook rules, skill improvements, and workflow optimizations.

**Why:** ECC's `conversation-analyzer` is the most novel meta-agent with no Craftpowers equivalent. It enables the system to learn from its own behavior — identifying patterns, failures, and improvement opportunities from real usage.

**ECC Reference:** `agents/conversation-analyzer.md` — analyzes conversation history, emits suggested hook rules and behavioral patterns.

**Priority:** P2 (nice-to-have — high novelty but requires instinct system first)
**Effort:** M (1-2 days) — agent definition + analysis prompts + output format
**Impact:** System self-improvement. Discovers patterns humans miss. Feeds instinct generation pipeline.

**Implementation Sketch:**
1. Define `conversation-analyzer.md` agent with transcript analysis prompts
2. Agent reads session JSONL, identifies: repeated corrections, failed approaches, time-consuming patterns
3. Outputs: suggested instincts (with confidence scores), suggested hook rules, skill improvement recommendations
4. User reviews and accepts/rejects suggestions
5. Accepted suggestions become instinct files or hook updates

---

## Strategic (needs planning — each 1-2 weeks)

### Proposal 9: Sub-Skill Architecture

**What:** Enable skills to contain sub-skills — nested SKILL.md files within a skill directory (e.g., `security-review/scan/SKILL.md`). Each sub-skill is independently invocable.

**Why:** ECC's directory-per-skill with nested sub-skills enables complex skills to be decomposed without creating top-level clutter. As Craftpowers grows, some skills (like `systematic-debugging`, `cook`) could benefit from sub-skill decomposition.

**ECC Reference:** `skills/security-review/scan/SKILL.md` — nested sub-skill pattern.

**Priority:** P2 (nice-to-have — architectural improvement)
**Effort:** L (3-5 days) — skill discovery changes, routing changes, documentation
**Impact:** Better organization for complex skills. Enables skill composition at directory level.

**Implementation Sketch:** Modify skill discovery to recursively scan for SKILL.md files within skill directories. Add namespace routing (`security-review:scan`). Update `writing-skills` to document sub-skill pattern.

---

### Proposal 10: Hook Profile System

**What:** Implement a profile system for hooks: `minimal` (safety-critical only), `standard` (recommended set), `strict` (all hooks enabled). Users select via environment variable or `.man.json`.

**Why:** ECC's `ECC_HOOK_PROFILE` lets users dial hook aggressiveness. Some users want maximum safety; others want minimal overhead. Currently Craftpowers has `.man.json` per-project config but no named profiles.

**ECC Reference:** `run-with-flags.js` checks `ECC_HOOK_PROFILE` against each hook's declared profiles before executing.

**Priority:** P2 (nice-to-have — UX improvement)
**Effort:** L (2-3 days) — profile definitions, per-hook profile tags, profile selection logic
**Impact:** Users can quickly adjust hook behavior without editing individual configs. Better onboarding experience.

**Implementation Sketch:** Define 3 profiles in a config file. Tag each hook with which profiles it belongs to. In hook dispatcher, check `MAN_HOOK_PROFILE` env var or `.man.json` profile field. Only run hooks matching the active profile.

---

### Proposal 11: Stack Auto-Detection & Configuration

**What:** Detect project stack from filesystem markers (e.g., `tsconfig.json` → TypeScript, `Cargo.toml` → Rust, `pyproject.toml` → Python) and auto-configure relevant skills, agents, and hooks.

**Why:** ECC's `project-stack-mappings.json` maps filesystem markers to recommended components. Currently Craftpowers requires manual `.man.json` configuration per project.

**ECC Reference:** `config/project-stack-mappings.json` — maps markers to skill/agent/hook recommendations.

**Priority:** P2 (nice-to-have — onboarding UX)
**Effort:** L (2-3 days) — detection logic, mapping config, auto-config on first run
**Impact:** Zero-config project setup. New projects get relevant skills/hooks automatically.

**Implementation Sketch:** Create stack detection in SessionStart hook. Map detected markers to recommended configurations. On first run in a new project, suggest or auto-apply relevant config.

---

### Proposal 12: GAN Adversarial Agent Pattern

**What:** Implement a `generator ↔ evaluator` adversarial loop pattern for iterative quality improvement. A generator agent produces output, an evaluator agent critiques it, iterate until quality threshold is met.

**Why:** ECC's GAN trio (`gan-planner → gan-generator ↔ gan-evaluator`) is inspired by the March 2026 Anthropic paper. This pattern could improve code review, plan writing, and security review quality by adding adversarial evaluation.

**ECC Reference:** `agents/gan-planner.md`, `agents/gan-generator.md`, `agents/gan-evaluator.md`

**Priority:** P2 (nice-to-have — quality improvement)
**Effort:** XL (1-2 weeks) — 3 agent definitions, loop orchestration, quality threshold logic, integration with existing workflows
**Impact:** Higher quality output for critical tasks. Adversarial pressure catches issues single-pass reviews miss.

**Implementation Sketch:** Define generator and evaluator agent pair. Build loop orchestration skill that: (1) generator produces output, (2) evaluator scores and critiques, (3) if below threshold, generator revises with feedback, (4) repeat until pass. Start with code review as first use case.

---

## Proposals Considered but Rejected

### ❌ Language-Specific Agent Pairs (28 agents)
ECC dedicates 28 of 60 agents to language-specific reviewers and build-resolvers. **Rejected** because Craftpowers' approach (generic agents + skill loading) is more maintainable. 28 agents to maintain vs 14 + dynamic skill loading. The depth gained doesn't justify the maintenance burden for a smaller team.

### ❌ LLM-as-Router for Skills
ECC loads all skill descriptions into context and lets the LLM infer which to invoke. **Rejected** because Craftpowers' explicit `Skill` tool invocation is more deterministic and reliable. ECC acknowledges this breaks down at 232+ skills (context cost).

### ❌ Multi-Harness Support (10+ harnesses)
ECC supports Claude Code, Codex, OpenCode, Cursor, Gemini CLI, etc. **Rejected** for now — Craftpowers should focus on Claude Code depth rather than spreading thin across harnesses. Reconsider if/when user demand warrants it.

### ❌ `origin` Frontmatter Field
ECC uses `origin: ECC` in skill frontmatter. **Rejected** — low value. Craftpowers' `phase` field is more useful for workflow orchestration.

### ❌ ML-Based Security Scanning (insaits SDK)
ECC's `insaits-security-monitor.py` uses a third-party ML SDK for credential/anomaly detection. **Rejected** — adds external dependency. Craftpowers' rule-based security hooks are sufficient and don't require third-party SDKs.

---

## Priority Roadmap

### Sprint 1 (This Week) — Quick Wins
1. P0: Prompt Defense Baseline for all agents
2. P0: Gateguard fact-forcing
3. P1: Catalog CI tests
4. P1: Cost tracking

### Sprint 2 (Next Week) — Core Innovations
5. P0: Instinct system
6. P1: Behavioral compliance testing
7. P1: Hook dispatcher consolidation

### Sprint 3 (Week After) — Meta & Polish
8. P2: Conversation analyzer agent
9. P2: Sub-skill architecture
10. P2: Hook profile system

### Backlog
11. P2: Stack auto-detection
12. P2: GAN adversarial pattern
