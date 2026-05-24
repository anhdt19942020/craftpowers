# ECC vs Craftpowers — Synthesis Report

**Date:** 2026-05-24
**Based on:** 3 parallel deep-research reports (skill system, agent architecture, hook/instinct system)

## Executive Summary

ECC (Everything Claude Code) — 190k stars, 2844 files — takes a **breadth-first, contributor-friendly** approach: 232 skills with minimal frontmatter, 60 agents with language-specific specialization, and a hook system featuring the novel "instinct" concept (confidence-scored behavioral nudges injected at session start). Craftpowers/Mankit takes a **depth-first, workflow-opinionated** approach: 50 skills with richer metadata (`phase` field), 14 tightly-wired agents with `roles.json` dispatch, and hooks leveraging newer Claude Code event types. Neither is strictly better — they optimize for different things.

**ECC's strongest innovations:**
1. Instinct system — machine-learned behavioral priors, genuinely novel
2. Behavioral compliance testing (`skill-comply`) — automated skill quality validation
3. Dispatcher consolidation — single dispatcher per event type, reducing spawn overhead
4. Gateguard fact-forcing — demands evidence before allowing destructive actions
5. GAN agent trio — adversarial iterative improvement pattern

**Craftpowers' strongest advantages:**
1. `phase` lifecycle field — enables harness-level skill ordering
2. `roles.json` with programmatic dispatch — deterministic agent selection
3. SubagentStart hook context injection — agents get context automatically
4. Newer Claude Code event coverage — `SubagentStop`, `ConfigChange`, `WorktreeCreate`, etc.
5. Explicit `Skill` tool invocation — deterministic routing vs ECC's LLM-inferred routing

---

## Full Comparison Matrix

### Skills

| Dimension | ECC | Craftpowers | Winner |
|-----------|-----|-------------|--------|
| Count | 232 | 50 | ECC (quantity) |
| Frontmatter fields | `name`, `description`, `origin` (3 fields) | `name`, `description`, `phase` (3 fields) | Craftpowers (`phase` is more useful than `origin`) |
| Routing mechanism | LLM reads descriptions, infers intent | Explicit `Skill` tool invocation | Craftpowers (deterministic) |
| Sub-skills | Yes (`security-review/scan/SKILL.md`) | No | ECC |
| Composition | `plan-orchestrate` emits chains | Skills invoke via `Skill` tool | Craftpowers (more reliable) |
| Install profiles | 6 profiles (minimal→full) | All skills always available | ECC (granularity) |
| Stack auto-config | `project-stack-mappings.json` | Manual `.man.json` | ECC |
| Behavioral testing | `skill-comply` (automated) | `man-eval` (human A/B) | ECC (automation) |
| Catalog CI test | `catalog.test.js` (count parity) | None | ECC |
| Namespace | `everything-claude-code:{name}` | `{plugin}:{skill-name}` | Tie |

### Agents

| Dimension | ECC | Craftpowers | Winner |
|-----------|-----|-------------|--------|
| Count | 60 | 14 | Context-dependent |
| Role mapping | None (flat, name=role) | `roles.json` with model IDs | Craftpowers |
| Model assignment | Logical aliases (`sonnet`/`opus`) | Specific model IDs | Craftpowers (precise) |
| Dispatch | Semantic heuristics in AGENTS.md | `subagent_type` keys in skills | Craftpowers (programmatic) |
| Context injection | None (self-directed) | SubagentStart hook + frontmatter | Craftpowers |
| Skill references | `see skill: X` (documentation pointer) | Active `skills: [...]` in frontmatter | Craftpowers |
| Language coverage | 14 languages × 2 agents each (28 agents) | Generic agents for all languages | ECC (if you need language depth) |
| Security preamble | Universal 8-bullet Prompt Defense Baseline | None standardized | ECC |
| Meta-agents | `conversation-analyzer`, `harness-optimizer` | None | ECC |
| GAN pattern | `gan-planner → generator ↔ evaluator` | None | ECC |

### Hooks

| Dimension | ECC | Craftpowers | Winner |
|-----------|-----|-------------|--------|
| Language | JavaScript (Node.js) | Python | Tie (ecosystem choice) |
| Script count | 45 | ~25 | ECC |
| Event types used | 7 (standard) | 11 (including newer events) | Craftpowers |
| Instinct system | Yes (confidence-scored behavioral injection) | No | ECC |
| Dispatcher pattern | Yes (pre-bash-dispatcher consolidates) | 1 script per event | ECC (performance) |
| In-process execution | `module.exports.run()` via `run-with-flags.js` | Not observed | ECC |
| Profile gating | `ECC_HOOK_PROFILE` (minimal/standard/strict) | `.man.json` per-project | ECC (user-facing dial) |
| Config protection | File-path detection (ESLint, Prettier, etc.) | `ConfigChange` native event | Craftpowers (native event) |
| Cost tracking | Transcript JSONL parsing + `costs.jsonl` | Not observed | ECC |
| Security scanning | `insaits-security-monitor.py` (ML SDK) | `security-gate.py` | Tie |

---

## ECC's Top 10 Design Decisions

### 1. LLM-as-Router (no skill dispatcher)
Skills loaded into context; LLM infers which to invoke. Zero infrastructure, infinite flexibility. **Breaks down** at 232+ skills — context cost scales linearly.

### 2. Instincts as Behavioral Priors
Machine-learned directives injected once per session. Distinct from hooks (guards) and rules (static). Confidence-scored (0.7 threshold), capped (6 max), scoped (project > global).

### 3. Dispatcher Consolidation
Single `pre-bash-dispatcher.js` multiplexes 5+ sub-checks instead of spawning N processes. Reduces per-tool-call overhead from ~250ms to ~50ms.

### 4. Horizontal Agent Specialization
One reviewer + one build-resolver per language/framework. 28 of 60 agents are language-specific. Deep knowledge > generic flexibility.

### 5. Fact-Forcing Gate (Gateguard)
Before destructive actions, demands 3 specific facts: targets list, rollback plan, verbatim instruction quote. Not a confirmation dialog — forces evidence production.

### 6. Directory-per-Skill
232 directories instead of 232 files. Enables sub-skills, fixtures, tests per skill. Install system can cherry-pick.

### 7. Universal Prompt Defense Baseline
Every agent starts with 8-bullet security preamble. Systematic defense-in-depth regardless of agent role.

### 8. In-Process Hook Execution
`run-with-flags.js` loads hooks that export `module.exports.run()` in-process, avoiding 50-100ms `spawnSync` overhead per call.

### 9. GAN Adversarial Pattern
`gan-planner → gan-generator ↔ gan-evaluator` loop. Generator produces, evaluator critiques, iterate until quality threshold. Inspired by March 2026 Anthropic paper.

### 10. Session Evaluation as Learning
`evaluate-session.js` analyzes completed sessions and can generate instinct files — the system learns from its own behavior over time.

---

## Craftpowers' Unique Advantages

### 1. `phase` Lifecycle Field
Enables harness-level skill ordering (`THINK` → `PLAN` → `ACT`). ECC has no equivalent — skills are unordered.

### 2. Programmatic Agent Dispatch
`roles.json` + `subagent_type` in skills = deterministic agent selection. ECC relies on AGENTS.md prose and human judgment.

### 3. SubagentStart Context Injection
Agents automatically receive project context at spawn time via hook. ECC agents must self-discover context.

### 4. Newer Event Type Coverage
`SubagentStop`, `StopFailure`, `WorktreeCreate`, `ConfigChange`, `PermissionRequest`, `UserPromptSubmit` — Craftpowers uses events ECC doesn't.

### 5. Explicit Skill Invocation
`Skill` tool provides deterministic routing. ECC's LLM-inferred routing can hallucinate skill names or pick wrong skills.

### 6. Agent-Skill Active Binding
Agent frontmatter lists `skills: [...]` actively loaded at dispatch. ECC's `see skill: X` is a documentation pointer, not active loading.

---

## Critical Gaps (ECC has, Craftpowers should consider)

1. **Instinct system** — behavioral priors learned from sessions. No Craftpowers equivalent. High novelty, high value.
2. **Behavioral compliance testing** — `skill-comply` automates skill quality validation. Craftpowers only has human A/B eval.
3. **Cost tracking** — transcript-based token cost tracking per session. Craftpowers has no cost visibility.
4. **Dispatcher consolidation** — single dispatcher per event type. Craftpowers spawns separate process per hook.
5. **Prompt Defense Baseline** — standardized security preamble across all agents. Craftpowers agents have no unified security layer.
6. **Conversation analyzer agent** — watches conversation patterns, suggests hook rules. Novel meta-agent concept.
7. **Catalog CI tests** — automated parity checks between filesystem and docs. Catches drift.
8. **Gateguard fact-forcing** — evidence-based approval for destructive actions (vs simple confirmation).

## Design Philosophy Differences

| Aspect | ECC | Craftpowers |
|--------|-----|-------------|
| **Core philosophy** | Breadth + contributor accessibility | Depth + workflow opinionation |
| **Skill routing** | LLM inference (flexible, non-deterministic) | Explicit invocation (deterministic, reliable) |
| **Agent strategy** | Many specialists (60) | Few generalists + skill loading (14) |
| **Hook approach** | Performance-optimized dispatchers | Event-type coverage breadth |
| **Quality assurance** | Automated behavioral testing | Human evaluation |
| **Install model** | Profiles with granular opt-in | Everything available always |
| **Learning** | Instincts (machine-learned priors) | Memory system (explicit user notes) |
| **Multi-harness** | 10+ harnesses supported | Claude Code only (focus) |

Neither approach is wrong. ECC optimizes for scale and broad adoption (190k stars). Craftpowers optimizes for reliability and deep workflow integration. The best improvements for Craftpowers will borrow ECC's novel concepts while preserving Craftpowers' deterministic, opinionated architecture.
