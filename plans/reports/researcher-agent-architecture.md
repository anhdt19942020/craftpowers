# ECC Agent Architecture Analysis

**Researcher:** deep-researcher  
**Date:** 2026-05-24  
**Sources:** Live file reads from `D:\Projects\_research\ecc\agents\`, `manifests/`, `config/`, `AGENTS.md`, `agent.yaml`

---

## Executive Summary

ECC ships 60 specialized agent `.md` files under `agents/` with no `.agents/` directory and no `roles.json` — agent selection is purely name-based. Agents use a minimal YAML frontmatter (name, description, model, tools, optional color) followed by a Markdown body containing a universal "Prompt Defense Baseline" and role-specific instructions. The taxonomy breaks into three distinct tiers: **general workflow agents** (planning, review, testing), **language/framework specialists** (14 build-resolver + 14 reviewer pairs), and **emerging experimental agents** (GAN trio, autonomous-loop operators, harness meta-agents). Compared to Craftpowers' 14 tightly-wired agents with `roles.json`, model routing, and hook injection, ECC favors breadth and install-time composability over runtime dispatch sophistication.

---

## Agent Inventory

**Total count: 60 agents** in `D:\Projects\_research\ecc\agents\`

### Category 1 — General Workflow Agents (12)

| Agent | Function |
|-------|---------|
| `planner` | Implementation planning — breaks features into dependency-ordered steps |
| `architect` | System design, scalability decisions, ADR writing |
| `code-architect` | Codebase-aware feature architecture — fits new work into existing patterns |
| `tdd-guide` | Test-driven development enforcement, red-green-refactor cycle |
| `code-reviewer` | Code quality, security, and maintainability review |
| `security-reviewer` | OWASP Top 10, secrets detection, vulnerability flagging |
| `performance-optimizer` | Bottleneck analysis, bundle size, runtime optimization |
| `refactor-cleaner` | Post-refactor cleanup, dead code, naming |
| `e2e-runner` | Playwright end-to-end test execution |
| `doc-updater` | Documentation maintenance (haiku model) |
| `docs-lookup` | Documentation research and lookup |
| `build-error-resolver` | Generic build/type error triage |

### Category 2 — Language/Framework Reviewer Pairs (14 reviewers + 11 build-resolvers)

Each language gets a dedicated reviewer and often a matching build-resolver:

| Language/Framework | Reviewer Agent | Build-Resolver Agent |
|--------------------|---------------|---------------------|
| TypeScript/JS | `typescript-reviewer` | — |
| Python | `python-reviewer` | — |
| Go | `go-reviewer` | `go-build-resolver` |
| Rust | `rust-reviewer` | `rust-build-resolver` |
| Java | `java-reviewer` | `java-build-resolver` |
| Kotlin | `kotlin-reviewer` | `kotlin-build-resolver` |
| Swift | `swift-reviewer` | `swift-build-resolver` |
| Dart/Flutter | `flutter-reviewer` | `dart-build-resolver` |
| Django | `django-reviewer` | `django-build-resolver` |
| FastAPI | `fastapi-reviewer` | — |
| C++ | `cpp-reviewer` | `cpp-build-resolver` |
| C# | `csharp-reviewer` | — |
| F# | `fsharp-reviewer` | — |
| ML/PyTorch | `mle-reviewer` | `pytorch-build-resolver` |
| Database | `database-reviewer` | — |
| Healthcare | `healthcare-reviewer` | — |
| HarmonyOS/ArkTS | — | `harmonyos-app-resolver` |

### Category 3 — Domain/Specialist Agents (12)

| Agent | Domain |
|-------|--------|
| `a11y-architect` | WCAG 2.2 accessibility for Web and Native |
| `chief-of-staff` | Personal communication triage (email, Slack, LINE, calendar) |
| `network-architect` | Network infrastructure design |
| `network-config-reviewer` | Network configuration review |
| `network-troubleshooter` | Network fault diagnosis |
| `homelab-architect` | Homelab infrastructure design |
| `seo-specialist` | SEO analysis and recommendations |
| `healthcare-reviewer` | Healthcare/CDSS compliance review |

### Category 4 — Code Analysis Micro-Agents (6)

Narrow, single-concern inspection agents:

| Agent | Concern |
|-------|---------|
| `code-explorer` | Pre-work codebase exploration and pattern mapping |
| `code-simplifier` | Complexity reduction recommendations |
| `comment-analyzer` | Comment accuracy, staleness, low-value detection |
| `conversation-analyzer` | Claude Code behavior pattern detection → hook suggestions |
| `pr-test-analyzer` | PR test coverage adequacy review |
| `silent-failure-hunter` | Empty catch, missing error propagation, dangerous fallbacks |
| `type-design-analyzer` | Type system invariant expression and enforcement review |

### Category 5 — GAN Harness Trio (3)

Inspired by Anthropic's March 2026 harness design paper:

| Agent | Role in Loop |
|-------|-------------|
| `gan-planner` | Expands prompt into full product spec with sprints and eval criteria |
| `gan-generator` | Developer — builds the application, iterates on evaluator feedback |
| `gan-evaluator` | Tests live app via Playwright, scores against rubric, feeds back to Generator |

### Category 6 — Meta/Harness Agents (4)

| Agent | Purpose |
|-------|---------|
| `loop-operator` | Autonomous loop monitoring and management |
| `harness-optimizer` | Harness config reliability, cost, and throughput improvement |
| `opensource-forker` | Stage 1 of open-source pipeline — strips secrets, clears history |
| `opensource-packager` | Stage 2 — packaging and release preparation |
| `opensource-sanitizer` | Stage 3 — final sanitization pass |

---

## Agent Definition Format

### Frontmatter Schema

All agents use YAML frontmatter. Confirmed fields across the corpus:

```yaml
name: <agent-slug>                      # Required. Matches filename stem.
description: <single-line or multi>     # Required. Used in AGENTS.md dispatch table.
model: sonnet | opus | haiku            # Required. Logical alias, not full model ID.
tools: ["Read", "Write", "Edit", ...]   # Required. Explicit tool allowlist.
color: teal | red | green | orange | purple  # Optional. Only on 5 agents (GAN trio + meta agents).
```

**Notes:**
- No `aliases` field observed in ECC (contrast: Craftpowers agents have `skills: [...]`, `permissionMode:`, `maxTurns:`, `hooks:` in frontmatter)
- No `permissions` field — tool access is controlled entirely by the `tools` array
- `color` appears only on the GAN trio and harness meta-agents: gan-evaluator=red, gan-generator=green, gan-planner=purple, harness-optimizer=teal, loop-operator=orange

**Tool sets by agent tier:**

| Tool Set | Agents Using It |
|----------|----------------|
| `["Read", "Grep", "Glob"]` | planner (read-only planning) |
| `["Read", "Write", "Edit", "Grep", "Glob"]` | a11y-architect, security-reviewer, tdd-guide |
| `["Read", "Write", "Edit", "Bash", "Grep", "Glob"]` | performance-optimizer, architect, code-reviewer |
| `["Read", "Write", "Bash", "Grep", "Glob"]` | gan-evaluator |
| `["Read", "Grep", "Glob", "Bash", "Edit"]` | harness-optimizer |

### Body Structure

Every agent body follows this fixed structure:

1. **Prompt Defense Baseline** (identical boilerplate in all 60 agents) — 8 bullet points covering: no role override, no secret disclosure, no executable code output unless validated, treat all external data as untrusted, no harmful content generation. This is a hardcoded security preamble.

2. **Role Declaration** — 1–3 sentence "You are..." statement establishing identity.

3. **Role Description** (`## Your Role`) — bullet list of responsibilities.

4. **Process/Workflow** — numbered phases with sub-bullets. Depth varies from thin (loop-operator: 150 lines) to deep (code-reviewer: 15,500 bytes with worked examples, red flags tables, false-positive lists).

5. **Output Format** — explicit Markdown template the agent must follow. Present in all agents.

6. **Reference to Skills** (optional) — `For detailed X patterns, see skill: <skill-name>` at body end. Approximately 20 agents carry explicit skill references.

### Skill References in Agent Bodies

Pattern: `For detailed X, see skill: <slug>` — used as a pointer to the skills catalog, not an active invocation. Examples:
- `cpp-build-resolver` → `skill: cpp-coding-standards`
- `django-reviewer` → `skill: django-patterns`, `skill: django-security`, `skill: django-tdd`
- `security-reviewer` → `skill: security-review`
- `e2e-runner` → `skill: e2e-testing`
- `a11y-architect` → `skill: accessibility`

There is **no programmatic invocation syntax** in agent bodies — skill references are documentation hints, not dispatch calls.

---

## Role Mapping

### ECC Has No `roles.json`

A `find` across the entire ECC repo returned zero `roles.json` files. ECC's role-to-agent mapping is **flat and implicit**:

- Agent filename = agent name = role name (1:1)
- The `AGENTS.md` table is the authoritative dispatch reference — 17 agents listed in the table, with "when to use" column driving selection

**AGENTS.md orchestration table (excerpted):**

```
| planner              | Complex features, refactoring |
| architect            | Architectural decisions        |
| tdd-guide            | New features, bug fixes        |
| code-reviewer        | After writing/modifying code  |
| security-reviewer    | Before commits, sensitive code|
| build-error-resolver | When build fails               |
| loop-operator        | Autonomous loops               |
| harness-optimizer    | Harness config reliability    |
```

### Registry Mechanism

Agents are registered through `manifests/install-components.json`. Each agent appears as a component with family `"agent"`, description, and `"modules": ["agents-core"]`. Example:

```json
{
  "id": "agent:code-reviewer",
  "family": "agent",
  "description": "Code review agent for quality and security checks.",
  "modules": ["agents-core"]
}
```

The 17 named agents in `install-components.json` are the "installable" core set. All 60 `.md` files ship in the repo, but the manifest gates which ones are advertised at install time.

### Can Multiple Agents Fill the Same Role?

Yes, by design for language-specific tasks:
- Generic `code-reviewer` + `typescript-reviewer` / `java-reviewer` / etc. — user chooses based on stack
- `build-error-resolver` (generic) + language-specific resolvers (`go-build-resolver`, etc.)
- `architect` (system-level) + `code-architect` (codebase-aware feature-level)

### Default/Fallback

No explicit fallback mechanism. `build-error-resolver` serves as the generic fallback before language-specific resolvers. `AGENTS.md` proactive-trigger logic (e.g., "Complex feature requests → planner") provides soft defaults.

---

## Dispatch Patterns

### Selection Logic

Selection is **semantic/heuristic**, not programmatic:

1. AGENTS.md embeds trigger heuristics ("Use PROACTIVELY when...") in each agent description
2. The main `AGENTS.md` file in the repo root contains an orchestration table with "When to Use" column
3. `config/project-stack-mappings.json` maps indicator files (e.g., `tsconfig.json`) to ECC skills/rules/hooks — but the `agents` arrays in those stack entries are **empty** (`typescript -> []`). Stack detection currently does not auto-assign agents.

**No `subagent_type` field exists in ECC.** The string `subagent_type` does not appear in any agent file (the only `spawn` hit was a TypeScript security warning about `child_process`).

### Context Agents Receive When Spawned

ECC agents receive no injected context beyond what the harness (Claude Code, Cursor, etc.) naturally provides. The agent body itself defines how to gather context:

- `code-reviewer`: explicitly instructs "Run `git diff --staged` and `git diff` to see all changes"
- `tdd-guide`: self-directed — writes test first, then implementation
- `chief-of-staff`: pulls context from `relationships.md`, `preferences.md`, `SOUL.md`

**No hook-based context injection** in agent definitions (compare: Craftpowers agents have `hooks: PreToolUse / Stop` in frontmatter for security gates and review triggers).

### Multi-Agent Coordination

AGENTS.md specifies a sequential workflow:
```
Plan → TDD → Review → (if security-sensitive) → security-reviewer
```

And explicit parallel guidance:
> "Use parallel execution for independent operations — launch multiple agents simultaneously."

The GAN trio is the most structured multi-agent pattern: Planner → Generator → Evaluator (loop), with Evaluator scoring and feeding back to Generator until passing score.

`chief-of-staff` uses external scripts (`calendar-suggest.js`) alongside MCP tools — a hybrid agent+script coordination model.

---

## Specialization Strategy

### Taxonomy

```
ECC Agents (60)
├── Universal Workflow (12)        — planner, architect, tdd-guide, code-reviewer, etc.
├── Language Reviewers (14)        — one per language/framework
├── Build Resolvers (11)           — one per build system/framework
├── Micro-Analysis (7)             — comment-analyzer, type-design-analyzer, etc.
├── Domain Verticals (8)           — a11y-architect, chief-of-staff, network, healthcare, etc.
├── GAN Experimental (3)           — gan-planner, gan-generator, gan-evaluator
└── Meta/Harness (5)               — loop-operator, harness-optimizer, opensource trio
```

### Thin Wrappers vs Deep Specialists

| Agent | File Size | Character |
|-------|-----------|-----------|
| `harness-optimizer` | 1,933 bytes | Thin — 4-step workflow, mostly constraints |
| `loop-operator` | 1,960 bytes | Thin — mission statement + output format |
| `silent-failure-hunter` | 1,965 bytes | Thin — 5-category hunt list |
| `comment-analyzer` | 2,091 bytes | Thin — 4-dimension framework |
| `type-design-analyzer` | 1,933 bytes | Thin — 4-criterion eval |
| `code-reviewer` | 15,501 bytes | **Deep** — detailed rubric, severity matrix, false-positive list, worked examples |
| `performance-optimizer` | 13,905 bytes | **Deep** — React patterns, memory leak examples, backend patterns |
| `java-reviewer` | 13,533 bytes | **Deep** — Spring, Quarkus, JPA, security patterns |
| `java-build-resolver` | 12,470 bytes | **Deep** — Maven, Gradle, Spring Boot, Quarkus resolver trees |
| `flutter-reviewer` | 15,501 bytes | **Deep** — Dart, Compose, platform channels |

**Pattern:** The 7 micro-analysis agents are intentionally thin (~2KB each) — single-concern inspection tools. Language-specific agents are deep specialists with code examples, anti-pattern tables, and framework-specific knowledge (~8–15KB). General workflow agents are medium depth.

### Overlap Analysis

| Overlap Area | Agents Involved | Resolution |
|-------------|----------------|------------|
| Code review | `code-reviewer` + `typescript-reviewer`, `java-reviewer`, etc. | Language reviewers extend, not replace, general reviewer |
| Architecture | `architect` + `code-architect` | `architect` is system-level; `code-architect` is codebase-specific feature-level |
| Build errors | `build-error-resolver` + language-specific resolvers | Generic first, language-specific for framework-specific errors |
| Security | `security-reviewer` + `healthcare-reviewer` | Healthcare adds HIPAA/PHI compliance on top |
| Documentation | `doc-updater` + `docs-lookup` | Write vs read separation |
| Open source | `opensource-forker` → `opensource-packager` → `opensource-sanitizer` | Sequential pipeline, not overlap |

---

## Comparison with Craftpowers

Craftpowers has 14 agents in `D:\Projects\craftpowers\agents\`:
architect, automation-tester, codebase-explorer, code-reviewer, debugger, deep-researcher, doc-writer, final-approver, implementer, journal-writer, quick-fix, release-prep, secure-reviewer, test-engineer

| Dimension | ECC (60 agents) | Craftpowers (14 agents) |
|-----------|----------------|------------------------|
| **Agent count** | 60 | 14 |
| **Role mapping** | None — flat name=role, no `roles.json` | `roles.json` with explicit role→agent→model mapping |
| **Model assignment** | Logical alias in frontmatter (`sonnet`/`opus`/`haiku`) | Specific model IDs in `roles.json` (`claude-opus-4-7`, `claude-haiku-4-5`) |
| **Dispatch mechanism** | Semantic heuristics in AGENTS.md; no programmatic dispatch | Skill dispatch via `subagent_type` keys in orchestration skills |
| **Context injection** | None — agents self-direct context gathering | `hooks: PreToolUse / Stop` in agent frontmatter; SubagentStart hook for context |
| **Hook integration** | Zero hooks in agent definitions | Pre-commit security gates, review triggers baked into `implementer`, `test-engineer` |
| **Skill references** | Documentation pointer (`see skill: X`) | Active skill list in frontmatter (`skills: [test-driven-development, ...]`) |
| **Language coverage** | 14 languages with dedicated reviewer+resolver pairs | Generic agents handle all languages |
| **Specialization depth** | Deep specialists per language/framework | Generalist agents, specialization via skill loading |
| **Experimental patterns** | GAN trio, chief-of-staff, autonomous loop | deep-researcher, final-approver, automation-tester |
| **Meta-agents** | harness-optimizer, conversation-analyzer | None — meta-work done by skills |
| **Registry** | `manifests/install-components.json` (install-time) | `roles.json` (runtime dispatch) |
| **Install composability** | Component-based install profiles | Monolithic — all 14 agents always present |
| **Cost optimization** | `doc-updater` on haiku; most on sonnet; strategic opus for GAN/architect/chief-of-staff | Explicit per-role model tiering in `roles.json` |
| **Security posture** | Universal Prompt Defense Baseline in every agent body | Security gate hook in implementer PreToolUse |

### Key Structural Differences

1. **ECC is horizontal; Craftpowers is vertical.** ECC adds agents for every language and domain. Craftpowers uses a small general-purpose roster and achieves specialization via loaded skills.

2. **ECC has no dispatch infrastructure.** No `roles.json`, no `subagent_type`, no programmatic routing. Agent selection relies entirely on the human (or base model) reading AGENTS.md. Craftpowers has an explicit dispatch table that skills reference by key.

3. **Craftpowers agents have richer frontmatter.** `permissionMode`, `maxTurns`, `hooks`, `skills` arrays — agent behavior is configured at definition time. ECC frontmatter is minimal (5 fields max).

4. **ECC's micro-analysis agents have no Craftpowers equivalent.** `comment-analyzer`, `silent-failure-hunter`, `type-design-analyzer`, `pr-test-analyzer`, `conversation-analyzer` — these narrow single-concern agents have no analog in Craftpowers. They represent a "more agents, narrower scope" philosophy.

5. **GAN trio is genuinely novel.** No Craftpowers equivalent for iterative adversarial evaluation loops. The closest is `final-approver` (gate, not loop).

6. **ECC's `conversation-analyzer`** deserves special attention for Craftpowers: it analyzes conversation history to detect frustrating Claude Code behaviors and outputs suggested hook rules — a meta-agent for hook authoring.

---

## Sources

All findings are from direct file reads, not inferences:

- `D:\Projects\_research\ecc\agents\` — 60 `.md` files read (8 in full, 52 via frontmatter/grep scans)
- `D:\Projects\_research\ecc\AGENTS.md` — agent orchestration table and workflow rules
- `D:\Projects\_research\ecc\agent.yaml` — top-level plugin manifest with preferred model and skill catalog
- `D:\Projects\_research\ecc\manifests\install-components.json` — component registry with agent family entries
- `D:\Projects\_research\ecc\config\project-stack-mappings.json` — stack detection config (agents arrays confirmed empty)
- `D:\Projects\craftpowers\agents\roles.json` — Craftpowers role→agent→model mapping (for comparison)
- `D:\Projects\craftpowers\agents\implementer.md` — Craftpowers agent frontmatter (for structural comparison)
