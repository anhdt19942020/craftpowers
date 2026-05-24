# ECC Skill System Analysis

## Executive Summary

ECC (Everything Claude Code) is a 190k-star agent harness optimization system containing 232 skills organized in `skills/*/SKILL.md` format. Each skill is a directory with a `SKILL.md` file containing a minimal YAML frontmatter (`name`, `description`, `origin`) followed by a structured markdown body. Skills are discovered purely by filename convention — there is no central routing registry; instead, the model reads skill descriptions from CLAUDE.md context injection and matches user intent against them. The system supports nested sub-skills (e.g., `security-review/scan/SKILL.md`), cross-skill references via backtick name, and a compliance testing infrastructure (`skill-comply`) that programmatically measures whether agents actually follow skill instructions.

---

## Skill Inventory

**Total:** 232 skills in `D:/Projects/_research/ecc/skills/`

### Categories by Naming Pattern

| Category | Count | Example Skills |
|----------|-------|----------------|
| Uncategorized / domain-specific | 142 | `accessibility`, `tdd-workflow`, `verification-loop`, `deep-research`, `docker-patterns` |
| `django-*` | 5 | `django-patterns`, `django-tdd`, `django-security`, `django-celery`, `django-verification` |
| `homelab-*` | 5 | `homelab-network-setup`, `homelab-vlan-segmentation`, `homelab-wireguard-vpn` |
| `kotlin-*` | 5 | `kotlin-patterns`, `kotlin-coroutines-flows`, `kotlin-ktor-patterns` |
| `laravel-*` | 5 | `laravel-patterns`, `laravel-tdd`, `laravel-security` |
| `scientific-*` | 5 | `scientific-thinking-literature-review`, `scientific-db-pubmed-database` |
| `agent-*` | 6 | `agent-architecture-audit`, `agent-eval`, `agent-introspection-debugging` |
| `healthcare-*` | 4 | `healthcare-cdss-patterns`, `healthcare-phi-compliance`, `healthcare-eval-harness` |
| `motion-*` | 4 | `motion-foundations`, `motion-patterns`, `motion-advanced`, `motion-ui` |
| `quarkus-*` | 4 | `quarkus-patterns`, `quarkus-tdd`, `quarkus-security` |
| `springboot-*` | 4 | `springboot-patterns`, `springboot-tdd`, `springboot-security` |
| `continuous-*` | 3 | `continuous-agent-loop`, `continuous-learning`, `continuous-learning-v2` |
| `frontend-*` | 3 | `frontend-patterns`, `frontend-design-direction`, `frontend-slides` |
| `network-*` | 3 | `network-bgp-diagnostics`, `network-config-validation` |
| `perl-*` | 3 | `perl-patterns`, `perl-security`, `perl-testing` |
| `security-*` | 3 | `security-review`, `security-scan`, `security-bounty-hunter` |
| `skill-*` | 3 | `skill-comply`, `skill-scout`, `skill-stocktake` |
| `swift-*` | 3 | `swift-actor-persistence`, `swift-concurrency-6-2` |
| Others (cpp, rust, golang, python, etc.) | ~13 | `rust-patterns`, `golang-patterns`, `python-testing` |

### Naming Conventions

- `{framework}-patterns` — idiomatic patterns for a language/framework
- `{framework}-tdd` — test-driven dev for that stack
- `{framework}-security` — security guidance specific to framework
- `{framework}-verification` — verification loop for that stack
- `{domain}-ops` — operational workflows (email-ops, messages-ops, github-ops)
- `{adjective}-agent` / `agent-{noun}` — agentic patterns and agent tooling
- Single-word nouns for cross-cutting concerns (`accessibility`, `benchmark`, `seo`)

---

## SKILL.md Anatomy

### Frontmatter Schema

Every SKILL.md starts with a YAML frontmatter block:

```yaml
---
name: tdd-workflow
description: Use this skill when writing new features, fixing bugs, or refactoring code. Enforces test-driven development with 80%+ coverage including unit, integration, and E2E tests.
origin: ECC
---
```

**Fields:**
| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `name` | Yes | string | kebab-case, matches directory name |
| `description` | Yes | string | The primary routing signal; must be specific enough for model intent-matching |
| `origin` | Yes | string | Always `ECC` for core skills |

No `triggers`, `model`, `version`, or `phase` fields in ECC's SKILL.md. This is a deliberate minimalism — all routing logic lives in the body text under `## When to Activate` / `## When to Use` / `## Trigger` sections.

### Body Structure Conventions

ECC skills do not enforce a rigid schema beyond frontmatter. Observed patterns across 8 sampled skills:

1. **`# Title`** — H1 title, typically the skill's human-readable name
2. **`## When to Use` / `## When to Activate` / `## Trigger`** — the routing section (mandatory in practice; this is what the model reads to decide activation)
3. **`## Core Principles` / `## How It Works` / `## Workflow`** — main content
4. **Numbered step sections** (`### Step 1`, `### Step 2`) for procedural skills
5. **Code blocks** — concrete examples, often with `// PASS: GOOD:` and `// FAIL: BAD:` annotations
6. **Checklists** — `[ ]` items for verification skills
7. **Tables** — for comparison, severity models, routing decisions
8. **`## Related Skills`** — backtick-quoted names linking to other skills (e.g., `` `frontend-patterns` ``, `` `design-system` ``)
9. **`## References`** — external links (WCAG, official docs)

**Example from `accessibility/SKILL.md`:**
```markdown
## Related Skills

- `frontend-patterns`
- `design-system`
- `liquid-glass-design`
- `swiftui-patterns`
```

**Example from `agent-architecture-audit/SKILL.md`:**
```json
{
  "schema_version": "ecc.agent-architecture-audit.report.v1",
  "executive_verdict": { ... }
}
```
Some skills embed structured output schemas directly in the body to constrain model output format.

### Sub-Files Within Skill Directories

Most skills contain only `SKILL.md`. However, some skills have nested sub-skill directories:

```
skills/
├── accessibility/
│   └── SKILL.md          (only file)
├── security-review/
│   ├── SKILL.md          (parent skill)
│   └── scan/
│       └── SKILL.md      (sub-skill: `security-review/scan`)
```

Sub-skills are referenced in parent skill body text as `security-review/scan` — a path-based namespace, not a flat name.

---

## Skill Routing

### Intent Matching Mechanism

ECC has **no central routing registry or dispatcher**. Routing works via:

1. **CLAUDE.md / AGENTS.md context injection** — skills are listed with their descriptions in the harness configuration files. The model reads these at session start and matches user intent against `description` frontmatter.
2. **`## When to Use` / `## When to Activate`** — the body's trigger section gives the model explicit conditions. These are prose instructions, not code.
3. **User invocation** — users can explicitly invoke `/skill-name` or the command equivalent.

**From `plan-orchestrate/SKILL.md`:**
> "Use when the user has a multi-step plan and wants to drive it through `/orchestrate` without composing chains by hand."

### Namespace System

ECC uses two install forms with different namespace prefixes:

| Form | Detection | Prefix |
|------|-----------|--------|
| Plugin install (1.9.0+) | `~/.claude/plugins/marketplaces/everything-claude-code/` exists | `everything-claude-code:skill-name` |
| Legacy bare install | Agent files under `~/.claude/agents/` | No prefix (bare name) |

The `plan-orchestrate` skill explicitly documents this and generates prefixed invocation strings at output time. Sub-skills use path notation: `security-review/scan`.

### Manifests and Registry

The `manifests/` directory contains three JSON files:
- `install-components.json` — component registry with `id` (pattern: `(baseline|lang|framework|capability|agent|skill|locale):[name]`), `family`, `description`, and `modules`
- `install-modules.json` — module registry mapping logical module IDs to filesystem paths
- `install-profiles.json` — preset bundles (minimal, core, developer, security, research, full)

**Component ID pattern:** `^(baseline|lang|framework|capability|agent|skill|locale):[a-z0-9-]+$`

This is an *install-time* registry, not a runtime routing registry. It determines what gets copied to `~/.claude/` during installation, not how skills are matched at runtime.

### Config-Based Auto-Assignment

`config/project-stack-mappings.json` maps project indicator files to skills:
```json
{
  "id": "typescript",
  "indicators": [{ "file": "tsconfig.json" }],
  "skills": ["coding-standards", "tdd-workflow", "verification-loop"]
}
```
`/project-init` uses this to auto-configure a project's active skill set.

---

## Skill Composition

### Cross-Skill References

Skills reference other skills via backtick notation in `## Related Skills` sections:

```markdown
## Related Skills
- `frontend-patterns`
- `design-system`
- `agent-introspection-debugging`
```

These are **advisory links**, not programmatic invocations. The model is expected to load and follow the referenced skill's instructions within the same session when relevant.

### Skill Chains / Pipelines

The `plan-orchestrate` skill is the primary composition mechanism. It reads a plan document and generates `/orchestrate custom` invocations — comma-separated agent chains:

```bash
/everything-claude-code:orchestrate custom \
  "everything-claude-code:tdd-guide,everything-claude-code:database-reviewer,everything-claude-code:python-reviewer,everything-claude-code:security-reviewer" \
  "[task description]"
```

This is **generative composition**: the skill emits shell commands for the user to paste, rather than directly invoking other skills. The orchestrate system passes HANDOFF outputs between agents in the chain.

### Context Sharing

ECC does not define a formal shared-context protocol between skills. Context flows via:
1. The conversation history (implicit)
2. Plan artifacts written to `.claude/plans/` (explicit file-based handoff)
3. HANDOFF sections in orchestrate chains (structured output contract)

The `plan-orchestrate` skill documents agent output contracts explicitly, requiring each step to produce a `HANDOFF` block the next agent reads.

---

## Skills vs Commands

### Format Comparison

| Attribute | Skills (`skills/*/SKILL.md`) | Commands (`commands/*.md`) |
|-----------|------------------------------|---------------------------|
| Directory structure | `skills/{name}/SKILL.md` | `commands/{name}.md` (flat) |
| Frontmatter | `name`, `description`, `origin` | `description` only (required) |
| Invocation | Described in CLAUDE.md, matched by model intent | `/command-name` slash command |
| Scope | Behavioral guidance, "how to do X" | Workflow orchestration, "run this process" |
| Execution model | Inline in current session | Can call subagents (but `plan.md` says "Run inline by default") |
| Body style | Reference guide + examples + checklists | Step-by-step imperative process |
| Length | Typically 60-300 lines | Typically 40-150 lines |

**Command frontmatter example (`plan.md`):**
```yaml
---
description: Creates a comprehensive implementation plan before writing any code.
---
```

Only `description` is required for commands; the test `command-frontmatter.test.js` enforces this.

**Skill frontmatter example (`tdd-workflow/SKILL.md`):**
```yaml
---
name: tdd-workflow
description: Use this skill when writing new features...
origin: ECC
---
```

### Why Commands and Skills Coexist

Commands (75 files) are **imperative workflows** — they represent user-initiated slash commands with specific named invocations. Skills (232 directories) are **declarative behavior guidance** — they prime the model with domain knowledge and patterns, activated by intent matching rather than explicit invocation.

Commands like `/plan` reference skills explicitly:
> "After planning: Use the `tdd-workflow` skill to implement with test-driven development"

This creates a layered system: commands orchestrate multi-step workflows; skills provide the knowledge substrate those workflows rely on.

### Migration Direction

The presence of `legacy-command-shims/` in the repo root indicates ECC is actively migrating away from commands toward skills + agents. The install manifest explicitly labels commands as "legacy command shims" in some contexts. Skills provide better discoverability (install-time selection by profile/stack) and better composability (orchestrate chains).

---

## Testing & Eval

### Test Infrastructure

`tests/` contains 30+ test files across 4 subdirectories:

```
tests/
├── ci/                    — CI validation tests
│   ├── catalog.test.js    — Validates skill/agent/command counts match README/docs
│   ├── command-registry.test.js
│   ├── codex-skill-surface.test.js
│   ├── agent-instruction-safety.test.js
│   ├── scan-supply-chain-iocs.test.js
│   └── validate-workflow-security.test.js
├── commands/
│   ├── command-frontmatter.test.js  — Enforces frontmatter on all commands
│   └── plan-command.test.js
├── docs/
│   ├── canary-watch.test.js
│   ├── harness-adapter-compliance.test.js
│   └── install-identifiers.test.js
└── hooks/
    ├── bash-hook-dispatcher.test.js
    └── auto-tmux-dev.test.js
```

**What `catalog.test.js` validates:**
- Skill count in `skills/` matches counts declared in README.md, AGENTS.md, plugin.json, marketplace.json
- Prevents documentation drift when skills are added/removed
- Validates cross-tool parity tables (Claude Code vs Cursor vs Codex vs OpenCode)

**What `command-frontmatter.test.js` validates:**
- Every `.md` file in `commands/` has YAML frontmatter
- Frontmatter has non-empty `description` field

### skill-comply: Behavioral Compliance Testing

The most sophisticated quality tool. From `skills/skill-comply/SKILL.md`:

1. Auto-generates expected behavioral sequences (specs) from any `.md` file
2. Generates scenarios at decreasing prompt strictness (supportive → neutral → competing)
3. Runs `claude -p` and captures tool call traces via stream-json
4. Classifies tool calls against spec steps using LLM (not regex)
5. Checks temporal ordering deterministically
6. Generates self-contained compliance reports

```bash
# Full compliance run
uv run python -m scripts.run ~/.claude/skills/search-first/SKILL.md

# Dry run (no cost, spec + scenarios only)
uv run python -m scripts.run --dry-run ~/.claude/skills/search-first/SKILL.md
```

This is behavioral testing — verifying the model actually follows skill instructions in real sessions, not just static content validation.

---

## Key Design Decisions

### 1. Minimal Frontmatter

ECC deliberately keeps frontmatter to 3 fields (`name`, `description`, `origin`). Routing signal lives in the body (`## When to Use`), not in structured metadata. This reduces schema friction for skill contributors but makes automated routing harder.

**Trade-off:** Easy to author, hard to programmatically filter/route.

### 2. No Central Dispatcher

Skills are loaded into context at install time. The LLM is the router. No code-based intent classifier or skill dispatcher exists. This means routing quality degrades as skill count grows (232 descriptions in context is expensive).

**Trade-off:** Zero infrastructure, infinite flexibility — but context cost scales linearly with skill count.

### 3. Directory-per-Skill

Each skill gets its own directory, enabling sub-skills (`security-review/scan/`), multiple files (future: examples, tests, fixtures), and clean install granularity. The install system can selectively install skills from profiles.

**Trade-off:** 232 directories vs 232 files — more filesystem overhead, better extensibility.

### 4. Descriptive Routing Over Trigger Codes

Skills use natural-language `## When to Use` sections rather than trigger keywords or regex patterns. The model must infer relevance from prose. This is more expressive than keyword matching but less deterministic.

### 5. Compliance as First-Class Concern

The `skill-comply` tool treats skills as testable behavioral contracts. This is an advanced quality mechanism absent from most agent harness systems.

---

## Comparison with Craftpowers

| Dimension | ECC | Craftpowers |
|-----------|-----|-------------|
| Skill count | 232 | 133 |
| Frontmatter fields | `name`, `description`, `origin` | `name`, `description`, `phase` |
| Phase field | Absent | Present (`THINK`, `PLAN`, `ACT`, etc.) |
| Routing mechanism | Natural language `## When to Use` + model inference | Skill tool invocations + `phase` field for lifecycle ordering |
| Namespace | `everything-claude-code:{name}` (plugin) | `{plugin}:{skill-name}` (e.g., `context-mode:tdd`) |
| Sub-skills | Yes (`security-review/scan/SKILL.md`) | Not observed |
| Skill composition | `plan-orchestrate` emits orchestrate chains | Skills invoke via `Skill` tool in prompts |
| Testing/eval | `skill-comply` (behavioral), `catalog.test.js` (structural) | `man-eval` (human A/B eval), no automated behavioral testing |
| Install profiles | Yes (minimal/core/developer/security/research/full) | No — all skills always available |
| Stack auto-config | `project-stack-mappings.json` → auto-assign on `/project-init` | Manual per-project `.man.json` config |
| Commands alongside | 75 commands + 232 skills (distinct layers) | Commands and skills coexist, no hard separation |
| Origin field | `ECC` (identifies source harness) | Absent |
| Skill metaskills | `skill-scout`, `skill-comply`, `skill-stocktake` | `writing-skills`, `man-eval` |

### Key Craftpowers Differentiators

1. **`phase` field** — Craftpowers adds a lifecycle stage (`THINK`, `PLAN`, `ACT`) to frontmatter, enabling the harness to suggest skills contextually based on where in the workflow the user is. ECC has no equivalent.

2. **Explicit `Skill` tool invocation** — Craftpowers skills are invoked via a dedicated `Skill` tool call; ECC skills are activated by model inference from description text. Craftpowers invocation is more deterministic.

3. **Human eval loop** — `man-eval` runs structured human A/B evals with fixture files and pass/fail scoring. ECC's `skill-comply` is automated but requires LLM-as-judge; Craftpowers uses human judgment.

4. **No install complexity** — Craftpowers doesn't have install profiles or stack mappings. All 133 skills are always available. ECC's install system adds power (selective deployment) but complexity.

### ECC Techniques Worth Adopting in Craftpowers

1. **`skill-comply` equivalent** — behavioral compliance testing via `claude -p` + tool trace capture would catch skill regressions automatically.
2. **`catalog.test.js` pattern** — CI test that validates skill count matches README/docs prevents documentation drift.
3. **Sub-skill directories** — `security-review/scan` pattern allows skill families to share a namespace.
4. **Stack auto-mapping** — auto-assigning skills based on `tsconfig.json` presence reduces setup friction for new projects.
5. **`skill-scout`** — pre-creation search to prevent skill duplication is a good process gate.

---

## Sources

All findings are from direct file reads of `D:/Projects/_research/ecc/` (accessed 2026-05-24).

Key files examined:
- `D:/Projects/_research/ecc/skills/accessibility/SKILL.md`
- `D:/Projects/_research/ecc/skills/agent-architecture-audit/SKILL.md`
- `D:/Projects/_research/ecc/skills/tdd-workflow/SKILL.md`
- `D:/Projects/_research/ecc/skills/verification-loop/SKILL.md`
- `D:/Projects/_research/ecc/skills/security-review/SKILL.md`
- `D:/Projects/_research/ecc/skills/coding-standards/SKILL.md`
- `D:/Projects/_research/ecc/skills/frontend-patterns/SKILL.md`
- `D:/Projects/_research/ecc/skills/search-first/SKILL.md`
- `D:/Projects/_research/ecc/skills/skill-comply/SKILL.md`
- `D:/Projects/_research/ecc/skills/skill-scout/SKILL.md`
- `D:/Projects/_research/ecc/skills/plan-orchestrate/SKILL.md`
- `D:/Projects/_research/ecc/manifests/install-components.json`
- `D:/Projects/_research/ecc/manifests/install-modules.json`
- `D:/Projects/_research/ecc/manifests/install-profiles.json`
- `D:/Projects/_research/ecc/config/project-stack-mappings.json`
- `D:/Projects/_research/ecc/commands/aside.md`
- `D:/Projects/_research/ecc/commands/plan.md`
- `D:/Projects/_research/ecc/commands/feature-dev.md`
- `D:/Projects/_research/ecc/tests/ci/catalog.test.js`
- `D:/Projects/_research/ecc/tests/commands/command-frontmatter.test.js`
- `D:/Projects/_research/ecc/schemas/*.json` (3 schemas)
- `D:/Projects/_research/ecc/package.json`
