# ECC Deep Research: Commands & Skills Catalog

**Date:** 2026-05-24
**Source:** Local clone at `D:\Projects\_research\ecc`
**Scope:** Everything Claude Code (ECC) — slash commands, 232 skills, routing, anatomy, install profiles

---

## 1. Repository Structure Overview

```
ecc/
├── agents/          — Specialized subagent definitions
├── commands/        — 72 slash command markdown files
├── legacy-command-shims/  — Old commands redirector (contains /commands/)
├── skills/          — 232 skill directories (each has SKILL.md)
├── hooks/           — Hook runtime configs
├── rules/           — Always-on guidelines
├── manifests/       — install-profiles.json, install-modules.json, install-components.json
├── scripts/         — Node.js utilities for hooks and orchestration
├── mcp-configs/     — MCP server configurations
└── COMMANDS-QUICK-REF.md  — Human-readable command index (59 commands listed)
```

**Key fact:** The COMMANDS-QUICK-REF lists 59 commands. The `commands/` directory has 72 `.md` files. The discrepancy is because some commands are language/framework-specific sub-commands not listed in the quick ref (e.g., `cpp-build.md`, `flutter-test.md`).

---

## 2. Complete Slash Command Inventory

All commands live in `/commands/*.md`. No separate routing table — Claude Code discovers them by path convention. Each file is a markdown document with a description frontmatter field. Commands invoke behavior through inline instructions, agent delegation, or skill references.

### Core Workflow Commands

| Command | File | What it does |
|---------|------|--------------|
| `/plan` | `plan.md` | Restate requirements, assess risks, write step-by-step implementation plan. Waits for user confirm before touching code. Supports PRD artifact mode (`.prd.md` input). |
| `/tdd` | *(via skill)* | Enforce test-driven development: scaffold interface → failing test → implement → verify 80%+ coverage |
| `/code-review` | `code-review.md` | Universal code review covering security, correctness, type safety, performance, completeness. Supports local diff mode AND GitHub PR review mode. |
| `/build-fix` | `build-fix.md` | Detect and fix build errors — delegates to right build-resolver agent automatically |
| `/verify` | *(via skill)* | Full verification loop: build → lint → test → type-check |
| `/quality-gate` | `quality-gate.md` | Quality gate check against project standards |
| `/refactor-clean` | `refactor-clean.md` | Remove dead code, consolidate duplicates, clean up structure |

### Language/Framework Build+Test+Review

| Command | File | Target |
|---------|------|--------|
| `/cpp-build` | `cpp-build.md` | C++ build |
| `/cpp-review` | `cpp-review.md` | C++ review |
| `/cpp-test` | `cpp-test.md` | C++ test |
| `/go-build` | `go-build.md` | Go build |
| `/go-review` | `go-review.md` | Go review |
| `/go-test` | `go-test.md` | Go test |
| `/kotlin-build` | `kotlin-build.md` | Kotlin build |
| `/kotlin-review` | `kotlin-review.md` | Kotlin review |
| `/kotlin-test` | `kotlin-test.md` | Kotlin test |
| `/rust-build` | `rust-build.md` | Rust build |
| `/rust-review` | `rust-review.md` | Rust review |
| `/rust-test` | `rust-test.md` | Rust test |
| `/flutter-build` | `flutter-build.md` | Flutter build |
| `/flutter-review` | `flutter-review.md` | Flutter review |
| `/flutter-test` | `flutter-test.md` | Flutter test |
| `/gradle-build` | `gradle-build.md` | Gradle build |
| `/fastapi-review` | `fastapi-review.md` | FastAPI review |
| `/python-review` | `python-review.md` | Python — PEP 8, type hints, security |
| `/go-review` | `go-review.md` | Go — idiomatic patterns, concurrency safety |
| `/gan-build` | `gan-build.md` | GAN training build |
| `/gan-design` | `gan-design.md` | GAN architecture design |
| `/multi-backend` | `multi-backend.md` | Multi-backend workflow |
| `/multi-frontend` | `multi-frontend.md` | Multi-frontend workflow |
| `/multi-execute` | `multi-execute.md` | Multi-service execution |
| `/multi-plan` | `multi-plan.md` | Multi-service planning |
| `/multi-workflow` | `multi-workflow.md` | Full multi-service orchestration |

### Session Management

| Command | File | What it does |
|---------|------|--------------|
| `/save-session` | `save-session.md` | Save current session state to `~/.claude/session-data/` |
| `/resume-session` | `resume-session.md` | Load most recent saved session and resume from where left off |
| `/sessions` | `sessions.md` | Browse, search, manage session history with aliases |
| `/checkpoint` | `checkpoint.md` | Mark a checkpoint in current session |
| `/aside` | `aside.md` | Answer a quick side question without losing task context |
| `/context-budget` | *(via skill)* | Analyse context window usage — find token overhead, optimise |

### Learning & Improvement

| Command | File | What it does |
|---------|------|--------------|
| `/learn` | `learn.md` | Extract reusable patterns from current session |
| `/learn-eval` | `learn-eval.md` | Extract patterns + self-evaluate quality before saving |
| `/evolve` | `evolve.md` | Analyse learned instincts, suggest evolved skill structures |
| `/promote` | `promote.md` | Promote project-scoped instincts to global scope |
| `/instinct-status` | `instinct-status.md` | Show all learned instincts (project + global) with confidence scores |
| `/instinct-export` | `instinct-export.md` | Export instincts to file |
| `/instinct-import` | `instinct-import.md` | Import instincts from file or URL |
| `/skill-create` | `skill-create.md` | Analyse local git history → generate reusable skill |
| `/skill-health` | `skill-health.md` | Skill portfolio health dashboard with analytics |
| `/rules-distill` | *(via skill)* | Scan skills, extract cross-cutting principles, distill into rules |

### PR & Git Workflow

| Command | File | What it does |
|---------|------|--------------|
| `/pr` | `pr.md` | Create a pull request |
| `/review-pr` | `review-pr.md` | Review a specific PR by number, URL, or branch |
| `/prp-plan` | `prp-plan.md` | PRP: create implementation plan |
| `/prp-prd` | `prp-prd.md` | PRP: create PRD |
| `/prp-implement` | `prp-implement.md` | PRP: execute implementation |
| `/prp-commit` | `prp-commit.md` | PRP: commit changes |
| `/prp-pr` | `prp-pr.md` | PRP: create PR |

### Feature Development

| Command | File | What it does |
|---------|------|--------------|
| `/feature-dev` | `feature-dev.md` | End-to-end feature development workflow |
| `/plan-prd` | `plan-prd.md` | Create a PRD document |
| `/project-init` | `project-init.md` | Initialize a new project |
| `/update-codemaps` | `update-codemaps.md` | Update codebase code maps/documentation |
| `/update-docs` | `update-docs.md` | Update project documentation |
| `/test-coverage` | `test-coverage.md` | Analyse and improve test coverage |

### Project & Infrastructure

| Command | File | What it does |
|---------|------|--------------|
| `/projects` | `projects.md` | List known projects and instinct statistics |
| `/harness-audit` | `harness-audit.md` | Audit agent harness configuration for reliability and cost |
| `/eval` | *(via skill)* | Run evaluation harness |
| `/model-route` | `model-route.md` | Route a task to right model (Haiku / Sonnet / Opus) |
| `/pm2` | `pm2.md` | PM2 process manager initialisation |
| `/setup-pm` | `setup-pm.md` | Configure package manager (npm / pnpm / yarn / bun) |
| `/ecc-guide` | `ecc-guide.md` | ECC guide and documentation |

### Loops & Automation

| Command | File | What it does |
|---------|------|--------------|
| `/loop-start` | `loop-start.md` | Start a recurring agent loop on an interval |
| `/loop-status` | `loop-status.md` | Check status of running loops |
| `/claw` | *(NanoClaw)* | Start NanoClaw v2 — persistent REPL with model routing, skill hot-load, branching, metrics |
| `/santa-loop` | `santa-loop.md` | Run santa-method verification in a loop |

### Hookify

| Command | File | What it does |
|---------|------|--------------|
| `/hookify` | `hookify.md` | Create new hookify rules (auto-analyzes conversation) |
| `/hookify-list` | `hookify-list.md` | View all rules in table format |
| `/hookify-configure` | `hookify-configure.md` | Toggle rules on/off interactively |
| `/hookify-help` | `hookify-help.md` | Full hookify documentation |

### Business & Ops

| Command | File | What it does |
|---------|------|--------------|
| `/jira` | `jira.md` | Jira integration — create, update, query issues |
| `/cost-report` | `cost-report.md` | Generate token cost report |
| `/security-scan` | `security-scan.md` | Run security scan on codebase |
| `/prompt-optimize` | *(via skill)* | Analyse draft prompt and output optimised ECC-enriched version |

### Misc

| Command | File | What it does |
|---------|------|--------------|
| `/prune` | `prune.md` | Prune outdated or redundant content |
| `/aside` | `aside.md` | Side question without losing context |

---

## 3. Skill Routing Mechanism

**There is no dispatcher or registry.** ECC uses pure LLM inference for skill routing. Key mechanism:

1. **SKILL.md frontmatter `description` field** contains trigger phrases and keywords Claude uses to decide when to invoke a skill.
2. **When-to-use sections** in each SKILL.md body provide detailed natural language routing instructions.
3. **Commands** (the 72 `.md` files in `commands/`) route to skills by invoking the skill name in their body text, or by running inline workflow steps.
4. **Agent delegation** — some commands invoke specialized agents (planner, build-resolver, etc.) from `agents/`.

Example from `blueprint` SKILL.md description:
```
TRIGGER when: user requests a plan, blueprint, or roadmap for a complex multi-PR task,
or describes work that needs multiple sessions.
DO NOT TRIGGER when: task is completable in a single PR or fewer than 3 tool calls.
```

Commands do NOT use slash-syntax internally. The command file IS the slash command — Claude reads it as a system prompt injection for that session.

---

## 4. Complete Skill Inventory (232 skills)

### 4.1 Skill Categories

#### Planning & Design (13)
| Skill | Purpose |
|-------|---------|
| `blueprint` | Turn one-line objective into multi-session construction plan with dependency graph, adversarial review, parallel step detection |
| `plan-orchestrate` | Orchestrate multi-agent plan execution |
| `architecture-decision-records` | Create and manage ADRs |
| `hexagonal-architecture` | Hexagonal/ports-and-adapters architecture guidance |
| `api-design` | REST/GraphQL API design patterns |
| `design-system` | Design system creation and maintenance |
| `frontend-design-direction` | Frontend design direction and visual strategy |
| `frontend-slides` | Presentation slides generation |
| `product-lens` | Product thinking and strategy lens |
| `ralphinho-rfc-pipeline` | RFC-driven DAG decomposition for large features |
| `team-builder` | Build and configure agent teams |
| `dashboard-builder` | Dashboard layout and component design |
| `recsys-pipeline-architect` | Recommendation system pipeline architecture |

#### Implementation Skills (50+)

**Language patterns:**
`backend-patterns`, `frontend-patterns`, `python-patterns`, `golang-patterns`, `rust-patterns`, `kotlin-patterns`, `kotlin-coroutines-flows`, `kotlin-exposed-patterns`, `kotlin-ktor-patterns`, `nestjs-patterns`, `fastapi-patterns`, `django-patterns`, `laravel-patterns`, `springboot-patterns`, `quarkus-patterns`, `android-clean-architecture`, `compose-multiplatform-patterns`, `dart-flutter-patterns`, `swiftui-patterns`, `swift-concurrency-6-2`, `swift-actor-persistence`, `swift-protocol-di-testing`, `angular-developer`, `dotnet-patterns`, `mcp-server-patterns`, `redis-patterns`, `postgres-patterns`, `mysql-patterns`, `clickhouse-io`, `jpa-patterns`, `prisma-patterns`, `database-migrations`, `nextjs-turbopack`, `nuxt4-patterns`, `tinystruct-patterns`, `bun-runtime`, `vite-patterns`, `ui-to-vue`, `motion-patterns`, `motion-ui`, `motion-advanced`, `motion-foundations`, `liquid-glass-design`, `cpp-coding-standards`, `java-coding-standards`, `coding-standards`, `perl-patterns`, `error-handling`, `hermes-imports`

**Testing:**
`python-testing`, `golang-testing`, `rust-testing`, `kotlin-testing`, `laravel-tdd`, `django-tdd`, `quarkus-tdd`, `springboot-tdd`, `cpp-testing`, `csharp-testing`, `fsharp-testing`, `perl-testing`, `e2e-testing`, `browser-qa`, `windows-desktop-e2e`, `django-verification`, `laravel-verification`, `quarkus-verification`, `springboot-verification`, `flutter-dart-code-review`

#### Testing/Quality Skills (21)
| Skill | Purpose |
|-------|---------|
| `tdd-workflow` | Enforce TDD with 80%+ coverage gate |
| `eval-harness` | Formal evaluation framework (EDD) with pass@k metrics |
| `plankton-code-quality` | Write-time linting via PostToolUse hooks with tiered model routing |
| `ai-regression-testing` | AI-specific regression test patterns |
| `council` | Multi-agent adversarial decision council |
| `santa-method` | Two-reviewer adversarial verification gate |
| `verification-loop` | Full build → lint → test → type-check loop |
| `production-audit` | Pre-production readiness audit |
| `hookify-rules` | Create Claude Code hook rules declaratively |
| `iterative-retrieval` | Progressive 4-phase context retrieval for subagents |
| `skill-scout` | Search for existing skills before creating new ones |
| `skill-stocktake` | Skill portfolio inventory and health check |
| `skill-comply` | Verify a skill follows ECC conventions |
| `configure-ecc` | ECC configuration management |
| `agent-introspection-debugging` | Debug misbehaving agents |
| `agent-sort` | Evidence-based ECC install plan for a repo |
| `continuous-learning` | Extract and persist reusable patterns (v1) |
| `continuous-learning-v2` | Pattern extraction v2 with improved taxonomy |
| `strategic-compact` | Suggest manual `/compact` at logical task boundaries |
| `code-tour` | Generate guided codebase tour |
| `codebase-onboarding` | Structured onboarding for new developers |

#### Security Skills (14)
| Skill | Purpose |
|-------|---------|
| `security-review` | General security vulnerability scanner |
| `security-scan` | Automated security scanning |
| `security-bounty-hunter` | Bug bounty hunting patterns |
| `hipaa-compliance` | HIPAA compliance guidance |
| `healthcare-phi-compliance` | PHI data protection |
| `django-security` | Django-specific security |
| `laravel-security` | Laravel-specific security |
| `springboot-security` | Spring Boot security |
| `quarkus-security` | Quarkus security |
| `perl-security` | Perl security |
| `defi-amm-security` | DeFi AMM smart contract security |
| `llm-trading-agent-security` | LLM trading agent security |
| `evm-token-decimals` | EVM token decimal handling (precision bugs) |
| `nodejs-keccak256` | Node.js cryptographic hashing |

#### Research Skills (9)
| Skill | Purpose |
|-------|---------|
| `deep-research` | Multi-source web research via Firecrawl + Exa MCPs |
| `exa-search` | Exa semantic search API integration |
| `research-ops` | Research operations and workflow |
| `scientific-db-pubmed-database` | PubMed database queries |
| `scientific-db-uspto-database` | USPTO patent database |
| `scientific-pkg-gget` | Genomics data retrieval (gget) |
| `scientific-thinking-literature-review` | Structured literature review |
| `scientific-thinking-scholar-evaluation` | Scholar source evaluation |
| `search-first` | Research-before-coding workflow; invokes researcher agent |

#### Agentic/Meta Skills (20)
| Skill | Purpose |
|-------|---------|
| `continuous-agent-loop` | Patterns for autonomous loops with quality gates and recovery |
| `autonomous-loops` | Autonomous agent loop primitives (predecessor to `continuous-agent-loop`) |
| `autonomous-agent-harness` | Agent harness construction |
| `agent-harness-construction` | Build agent harness from scratch |
| `agent-architecture-audit` | Audit multi-agent architecture |
| `agentic-engineering` | Agentic system engineering principles |
| `agentic-os` | Operating-system-like agent orchestration |
| `ai-first-engineering` | AI-first development methodology |
| `blueprint` | Multi-session construction planner (also in Planning) |
| `claude-devfleet` | Multi-agent Claude development fleet |
| `enterprise-agent-ops` | Enterprise-scale agent operations |
| `nanoclaw-repl` | Persistent REPL with model routing and session branching |
| `prompt-optimizer` | Analyze and optimize prompts against ECC ecosystem |
| `token-budget-advisor` | Token usage cost optimization |
| `cost-aware-llm-pipeline` | LLM pipeline design for cost efficiency |
| `ralphinho-rfc-pipeline` | RFC DAG decomposition |
| `regex-vs-llm-structured-text` | Decision guide: regex vs LLM for parsing |
| `content-hash-cache-pattern` | Content-addressed caching patterns |
| `data-scraper-agent` | Web scraping agent patterns |
| `openclaw-persona-forge` | Persona creation for agent teams |

#### DevOps/Deployment Skills (15)
| Skill | Purpose |
|-------|---------|
| `deployment-patterns` | General deployment workflow patterns |
| `docker-patterns` | Docker containerisation patterns |
| `cisco-ios-patterns` | Cisco IOS network device automation |
| `netmiko-ssh-automation` | SSH automation via Netmiko |
| `network-bgp-diagnostics` | BGP routing diagnostics |
| `network-config-validation` | Network config validation |
| `network-interface-health` | Network interface health monitoring |
| `homelab-network-readiness` | Homelab network setup readiness |
| `homelab-network-setup` | Homelab network configuration |
| `homelab-pihole-dns` | Pi-hole DNS setup |
| `homelab-vlan-segmentation` | VLAN network segmentation |
| `homelab-wireguard-vpn` | WireGuard VPN setup |
| `flox-environments` | Flox reproducible environments |
| `uncloud` | Cloud-to-local migration patterns |
| `dmux-workflows` | Tmux/worktree orchestration workflows |

#### Business/Content Skills (20)
| Skill | Purpose |
|-------|---------|
| `article-writing` | Structured article and blog writing |
| `brand-voice` | Brand voice system |
| `content-engine` | Content production pipeline |
| `investor-materials` | Investor deck and materials |
| `investor-outreach` | Investor outreach campaigns |
| `lead-intelligence` | Sales lead research |
| `product-capability` | Product capability documentation |
| `social-graph-ranker` | Social graph analysis |
| `seo` | SEO optimization |
| `market-research` | Market research workflow |
| `crosspost` | Cross-platform content publishing |
| `customer-billing-ops` | Customer billing operations |
| `finance-billing-ops` | Finance and billing workflows |
| `email-ops` | Email operations |
| `messages-ops` | Messaging platform operations |
| `github-ops` | GitHub operations |
| `google-workspace-ops` | Google Workspace automation |
| `connections-optimizer` | Network connections optimization |
| `cost-tracking` | Cost tracking and reporting |
| `automation-audit-ops` | Automation audit operations |

#### Domain-Specific Skills (30+)
| Skill | Domain |
|-------|--------|
| `healthcare-cdss-patterns` | Clinical decision support systems |
| `healthcare-emr-patterns` | Electronic medical records |
| `healthcare-eval-harness` | Healthcare AI evaluation |
| `hipaa-compliance` | HIPAA regulatory |
| `inventory-demand-planning` | Supply chain inventory |
| `logistics-exception-management` | Logistics exception handling |
| `production-scheduling` | Manufacturing production scheduling |
| `returns-reverse-logistics` | Returns/reverse logistics |
| `quality-nonconformance` | Quality control non-conformance |
| `customs-trade-compliance` | International trade compliance |
| `energy-procurement` | Energy procurement workflows |
| `carrier-relationship-management` | Carrier management |
| `nutrient-document-processing` | Nutritional document processing |
| `visa-doc-translate` | Visa document translation |
| `manim-video` | Manim mathematical animation |
| `remotion-video-creation` | Remotion video production |
| `fal-ai-media` | FAL AI media generation |
| `blender-motion-state-inspection` | Blender 3D state inspection |
| `ios-icon-gen` | iOS icon generation |
| `gan-style-harness` | GAN training harness |
| `benchmark` | Performance benchmarking |
| `pytorch-patterns` | PyTorch ML patterns |
| `mle-workflow` | Machine learning engineering workflow |
| `recsys-pipeline-architect` | Recommendation system pipeline |
| `videodb` | Video database operations |
| `video-editing` | Video editing workflow |
| `defi-amm-security` | DeFi AMM security |
| `evm-token-decimals` | EVM token precision |
| `agent-payment-x402` | x402 payment protocol for agents |
| `jira-integration` | Jira integration patterns |

---

## 5. Skill Anatomy Deep Dive (5 Skills)

### 5.1 `blueprint`

**Frontmatter:**
```yaml
name: blueprint
description: >-
  Turn a one-line objective into a step-by-step construction plan for
  multi-session, multi-agent engineering projects. Each step has a
  self-contained context brief so a fresh agent can execute it cold.
  Includes adversarial review gate, dependency graph, parallel step
  detection, anti-pattern catalog, and plan mutation protocol.
  TRIGGER when: user requests a plan, blueprint, or roadmap for a
  complex multi-PR task, or describes work that needs multiple sessions.
  DO NOT TRIGGER when: task is completable in a single PR or fewer
  than 3 tool calls, or user says "just do it".
origin: community
```

**Body structure:** When-to-use, Do-not-use, 5-phase pipeline (Research → Design → Draft → Review → Finalize), anti-pattern catalog, plan mutation protocol, Related Skills.

**Key mechanism:** 5-phase pipeline. Phase 4 delegates adversarial review to a strongest-model subagent (Opus). Every step in the output plan includes a context brief, task list, verification commands, exit criteria — so a fresh agent can execute any step cold without reading prior steps. Pure Markdown, zero runtime dependencies.

**References:** Uses `santa-method` for adversarial review gate.

### 5.2 `santa-method`

**Frontmatter:**
```yaml
name: santa-method
description: "Multi-agent adversarial verification with convergence loop. Two independent review agents must both pass before output ships."
origin: "Ronald Skelton - Founder, RapportScore.ai"
```

**Body structure:** When-to-activate, When-not-to-use, Architecture (Naughty or Nice), Reviewer prompt template, Rubric design, Verdict gate, Convergence loop.

**Key mechanism:** Two independent reviewer subagents launched in parallel with identical rubric, same inputs, no shared context. Both must pass (both return PASS verdict) for output to ship. If either fails, convergence loop: apply fixes, re-run BOTH reviewers. Loop terminates only on double-pass. Anti-anchoring: fresh context prevents reviewer B seeing reviewer C's assessment. Python-style pseudocode shows parallel spawn pattern.

**No sub-skills.** Single SKILL.md file.

### 5.3 `eval-harness`

**Frontmatter:**
```yaml
name: eval-harness
description: Formal evaluation framework for Claude Code sessions implementing eval-driven development (EDD) principles
origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
```

**Body structure:** When to Activate, Philosophy, Eval Types (Capability / Regression), Grader Types (Code-Based / Model-Based / Human), Metrics (pass@k, pass^k), Reporting template, Integration Patterns.

**Key mechanism:** Treats evals as "unit tests of AI development." Defines pass@k metric ("at least one success in k attempts"). Three grader types: deterministic code-based (bash scripts), model-based (LLM-as-judge with structured JSON output), human-flagged. Template-driven: standard eval definition files at `.claude/evals/feature-name.md`.

**Note:** `tools` field in frontmatter explicitly lists allowed tools — a convention not all skills use.

### 5.4 `council`

**Frontmatter:**
```yaml
name: council
(inferred from directory name — no explicit frontmatter visible in excerpt)
```

**Body structure:** When to Use, When NOT to Use (table), Roles table, Workflow (5 steps), Prompt template for each role, Synthesis rules, Output format, Persistence Rule, Anti-Patterns, Related Skills.

**Key mechanism:** 4-voice decision council. Main Claude writes its position FIRST (anti-anchoring). Then launches three subagents in parallel: Skeptic, Pragmatist, Critic. Each gets only question + compact context (NOT full conversation). Each returns: Position, Reasoning (3 bullets), Risk, Surprise. Main Claude synthesizes with bias guardrails. Output limited to phone-screen size.

**Related skills listed inline:** `santa-method`, `knowledge-ops`, `search-first`, `architecture-decision-records`.

### 5.5 `hookify-rules`

**Frontmatter:**
```yaml
name: hookify-rules
description: This skill should be used when the user asks to create a hookify rule, write a hook rule, configure hookify, add a hookify rule, or needs guidance on hookify rule syntax and patterns.
```

**Body structure:** Overview, Basic Format (YAML frontmatter + markdown body), Frontmatter Fields table, Advanced Format (multiple conditions), Event Type Guide, Pattern Writing Tips, File Organization, Commands.

**Key mechanism:** Declarative hook rules as markdown files with YAML frontmatter. Each rule specifies `event` (bash/file/stop/prompt/all), `action` (warn/block), `pattern` (regex). Multiple conditions use AND logic. Files stored at `.claude/hookify.{rule-name}.local.md`. This is ECC's abstraction layer over raw Claude Code hook JSON — much more ergonomic for non-engineers.

---

## 6. Install Profiles

ECC uses a 3-tier manifest system:
1. `install-profiles.json` — named profiles (user-facing)
2. `install-modules.json` — module definitions (what files each module includes)
3. `install-components.json` — component definitions (mappings by framework/language/capability)

### Profiles

| Profile | Description | Modules |
|---------|-------------|---------|
| `minimal` | No hook runtime. Rules + agents + commands + platform configs + quality workflow. | rules-core, agents-core, commands-core, platform-configs, workflow-quality |
| `core` | Adds hooks runtime to minimal. | + hooks-runtime |
| `developer` | Default profile for most ECC users. Adds frameworks, database, orchestration. | + framework-language, database, orchestration |
| `security` | Security-heavy setup. | core + security |
| `research` | Research/content/publishing workflows. | core + research-apis, business-content, social-distribution |
| `full` | All classified modules. | Everything |

### Module Definitions (what skills each module contains)

| Module | Kind | Skills Count | Key Skills |
|--------|------|-------------|------------|
| `rules-core` | rules | 0 skills (rules files) | Core rules and language packs |
| `agents-core` | agents | 0 skills (agent files) | planner, code-reviewer, tdd-guide, architect, build-error-resolver, e2e-runner, security-reviewer |
| `commands-core` | commands | 0 skills (command files) | Core slash commands |
| `hooks-runtime` | hooks | 0 skills (hook configs + scripts) | Hook configs and helper scripts |
| `platform-configs` | configs | 0 skills | Package manager + MCP catalog |
| `framework-language` | skills | ~48 | All language/framework patterns + testing |
| `database` | skills | 6 | clickhouse-io, database-migrations, jpa, mysql, postgres, prisma |
| `workflow-quality` | skills | 21 | tdd-workflow, eval-harness, council, santa-method, hookify-rules, iterative-retrieval, plankton-code-quality, skill-scout, strategic-compact, etc. |
| `security` | skills | 14 | security-review, security-scan, hipaa, healthcare-phi, defi-amm-security, llm-trading-agent-security, etc. |
| `research-apis` | skills | 8 | deep-research, exa-search, scientific-* |
| `business-content` | skills | 10 | article-writing, brand-voice, content-engine, investor-*, seo, market-research |
| `operator-workflows` | skills | ~12 | automation-audit-ops, api-connector-builder, customer-billing-ops, finance-billing-ops, email-ops, github-ops, google-workspace-ops, cost-tracking |
| `social-distribution` | skills | ~3 | crosspost + social skills |
| `media-generation` | skills | ~5 | fal-ai-media, manim-video, remotion-video-creation, ios-icon-gen, video-editing |
| `orchestration` | mixed | ~8 | dmux-workflows + orchestration scripts |
| `swift-apple` | skills | 6 | foundation-models-on-device, liquid-glass-design, swift-actor-persistence, swift-concurrency-6-2, swift-protocol-di-testing, swiftui-patterns |
| `agentic-patterns` | skills | 20 | agent-architecture-audit, agentic-engineering, autonomous-loops, blueprint, claude-devfleet, continuous-agent-loop, cost-aware-llm-pipeline, data-scraper-agent, enterprise-agent-ops, nanoclaw-repl, prompt-optimizer, ralphinho-rfc-pipeline, search-first, token-budget-advisor, team-builder, etc. |
| `devops-infra` | skills | ~8 | cisco-ios-patterns, deployment-patterns, docker-patterns, netmiko-ssh-automation, network-* |
| `machine-learning` | skills | ~4 | pytorch-patterns, mle-workflow, benchmark, recsys-pipeline-architect |
| `supply-chain-domain` | skills | ~8 | inventory-demand-planning, logistics-exception-management, production-scheduling, returns-reverse-logistics, quality-nonconformance, customs-trade-compliance, energy-procurement, carrier-relationship-management |
| `document-processing` | skills | ~3 | nutrient-document-processing, visa-doc-translate + others |

---

## 7. Sub-Skills

**ECC does NOT use sub-skills in the sense of nested SKILL.md hierarchies.** Each skill directory contains exactly one `SKILL.md`. The sub-skills scan confirmed no skill has additional skill files in subdirectories.

Instead, ECC achieves skill composition through:
1. **Cross-references** — Skills explicitly list `Related Skills` section pointing to other skill names
2. **Sequential invocation** — `continuous-agent-loop` recommends a combination: `ralphinho-rfc-pipeline` + `plankton-code-quality` + `eval-harness` + `nanoclaw-repl`
3. **Agent delegation** — Skills spawn subagents (e.g., `council` spawns Skeptic/Pragmatist/Critic, `blueprint` spawns an Opus reviewer)
4. **Command-to-skill binding** — A command file can reference a skill in its body text, invoking it contextually

The `legacy-command-shims/` directory contains only a pointer to `commands/` (a symlink/redirect) with a README.

---

## 8. Top 20 Most Interesting Skills

### 1. `santa-method`
**Purpose:** Adversarial verification — two independent reviewers must both pass.
**Mechanism:** Anti-anchoring through parallel isolated reviewer subagents. Identical rubric, no shared context. Verdict gate: both must pass. Convergence loop on failure.
**Why interesting:** Solves LLM self-approval bias. Named after Ronald Skelton (RapportScore.ai). A rare pattern that treats LLM output correctness as a testable binary gate rather than a confidence score.
**Mankit equivalent:** `adversarial-design` (grills design decisions) is related but advisory, not a binary gate. No direct equivalent.

### 2. `council`
**Purpose:** 4-voice adversarial decision council for ambiguous choices.
**Mechanism:** Main Claude writes position first (anti-anchoring), then spawns Skeptic + Pragmatist + Critic in parallel with minimal context. Synthesizes with explicit bias guardrails. NOT for code review — only for genuine decision ambiguity.
**Why interesting:** Explicit anti-anchoring protocol is novel. The "write your position first" step prevents the main model from simply mirroring subagents. Highly specific when-NOT-to-use table prevents misuse.
**Mankit equivalent:** `adversarial-design` partially covers this. Mankit's `multi-persona-predict` (5 personas) is the closest analog.

### 3. `blueprint`
**Purpose:** Turn one-line objective into a multi-session, multi-agent construction plan.
**Mechanism:** 5-phase pipeline (Research → Design → Draft → adversarial Review → Finalize). Every step is self-contained — a fresh agent can execute it cold. Parallel step detection via dependency graph. Formal plan mutation protocol (split/insert/skip/reorder/abandon with audit trail).
**Why interesting:** The "cold execution" constraint is key — forces the plan to be truly self-contained. Adversarial review in phase 4 catches plan anti-patterns before implementation starts. Pure markdown, zero dependencies.
**Mankit equivalent:** `writing-plans` is much simpler. Blueprint is significantly more rigorous with dependency graphs, parallel detection, and mutation protocols.

### 4. `plankton-code-quality`
**Purpose:** Write-time linting enforcement via PostToolUse hooks with tiered model routing.
**Mechanism:** Three-phase: Auto-format silently → collect violations as JSON → spawn Claude subprocess to fix violations, routing to Haiku/Sonnet/Opus based on violation complexity. Config protection blocks LLMs from disabling lint rules. Main agent only sees violations the subprocess couldn't fix.
**Why interesting:** Self-healing code quality loop. LLM tries to cheat by editing linter configs — this blocks that with PreToolUse hooks AND a Stop hook. Tiered model routing (Haiku for style, Opus for type reasoning) optimizes cost.
**Mankit equivalent:** `setup-pre-commit` (Husky) is pre-commit only, not write-time. No equivalent.

### 5. `eval-harness`
**Purpose:** Formal EDD (Eval-Driven Development) framework with pass@k metrics.
**Mechanism:** Defines capability evals, regression evals, three grader types (code-based bash, model-based LLM-as-judge, human-flagged). Standardizes pass@k and pass^k metrics. Template-driven eval definitions stored as markdown files.
**Why interesting:** Applies software testing rigor to LLM output evaluation. Pass@k gives probabilistic coverage — "at least one success in k attempts." Model-based grading is structured JSON, not prose — deterministic aggregation.
**Mankit equivalent:** `man-eval` runs interactive A/B evals from fixture files. Less formal, no pass@k. No direct equivalent for automated EDD.

### 6. `ralphinho-rfc-pipeline`
**Purpose:** RFC-driven multi-agent DAG execution for features too large for a single agent pass.
**Mechanism:** 7 stages: RFC intake → DAG decomposition → unit assignment → implementation → validation → merge queue → system verification. Each work unit has formal spec (id, depends_on, scope, acceptance_tests, risk_level, rollback_plan). Three complexity tiers. Merge queue rules: never merge with dependency failures, always rebase, re-run integration tests.
**Why interesting:** Applies software engineering project management rigor (DAG, merge queue, rollback plans) to LLM task orchestration. Work unit scorecards provide progress visibility.
**Mankit equivalent:** `subagent-driven-development` for parallel tasks. No DAG/merge queue equivalent.

### 7. `iterative-retrieval`
**Purpose:** Solve the "context problem" for subagents that don't know what context they need upfront.
**Mechanism:** 4-phase loop: DISPATCH (broad query) → EVALUATE (score relevance 0-1) → REFINE (update search criteria based on evaluation) → CONVERGE (exit when sufficient high-relevance context found). JavaScript-style pseudocode shows the loop. Handles terminology mismatch (e.g., codebase uses "throttle" not "rate-limit").
**Why interesting:** Addresses a fundamental multi-agent failure mode. Most agents either drown in context or starve for it. This progressive refinement is RAG-for-agents without a vector database.
**Mankit equivalent:** No equivalent. This is a novel pattern.

### 8. `continuous-agent-loop` (v1.8+)
**Purpose:** Patterns for autonomous agent loops with quality gates and recovery controls.
**Mechanism:** Loop selection flow (sequential/infinite/RFC/PR modes). Recommended production stack: RFC decomposition + quality gates + eval loop + session persistence. Failure mode taxonomy: churn, repeated retries, merge queue stalls, cost drift. Recovery: freeze → harness-audit → reduce scope → replay with explicit criteria.
**Why interesting:** Formalizes the meta-level of running autonomous agents: how to choose loop type, how to detect failure, how to recover without human intervention.
**Mankit equivalent:** `autoresearch-loop` (iteration loop with metrics). Narrower scope.

### 9. `hookify-rules`
**Purpose:** Declarative hook rules as markdown files — much more ergonomic than raw JSON hook config.
**Mechanism:** YAML frontmatter specifies event type, action (warn/block), pattern (regex) or multiple conditions. Five event types: bash, file, stop, prompt, all. Stored at `.claude/hookify.{rule-name}.local.md`. Companion commands: `/hookify`, `/hookify-list`, `/hookify-configure`, `/hookify-help`.
**Why interesting:** Abstraction layer over Claude Code's raw hook system. Declarative markdown makes hook authoring accessible to non-engineers. Supports complex multi-condition rules with AND logic.
**Mankit equivalent:** Mankit hooks are configured in settings.json JSON directly. No declarative abstraction layer equivalent.

### 10. `strategic-compact`
**Purpose:** Suggest manual `/compact` at logical task boundaries instead of arbitrary auto-compaction.
**Mechanism:** Runs a `suggest-compact.js` script via PreToolUse hook on Edit/Write. Tracks tool call count, suggests compaction at configurable threshold (default: 50 calls), reminds every 25 calls after threshold. Provides a decision table: which phase transitions should compact.
**Why interesting:** Meta-skill for context management. Auto-compaction mid-implementation breaks state. Strategic compaction preserves what matters. The phase-transition table is practically useful.
**Mankit equivalent:** `context-management` skill. Similar domain, but Mankit's version is more advisory and less automated.

### 11. `nanoclaw-repl`
**Purpose:** Persistent REPL with model routing, skill hot-loading, session branching, metrics.
**Mechanism:** `scripts/claw.js` — persistent markdown-backed sessions. Commands: `/model` (switch models), `/load` (hot-load skill), `/branch` (session branching before risky changes), `/compact`, `/search`, `/export`, `/metrics`. Zero external runtime dependencies. Markdown-as-database.
**Why interesting:** REPL-as-agent-interface. Session branching is particularly novel — like git branches for agent sessions. Markdown-as-database means the entire session history is human-readable and editable.
**Mankit equivalent:** `session-recovery`. NanoClaw is much more fully-featured.

### 12. `agent-sort`
**Purpose:** Build an evidence-backed ECC install plan for a specific repo.
**Mechanism:** Classify ECC components into DAILY (load every session) vs LIBRARY (keep accessible but don't load). Every DAILY decision must cite concrete repo evidence (file extensions, lockfiles, framework configs, CI scripts). Runs parallel review passes. Output: DAILY inventory, LIBRARY inventory, install plan, verification report.
**Why interesting:** Anti-cargo-cult skill. Prevents installing 232 skills just because they exist. Evidence-based classification is disciplined — must grep actual repo before deciding.
**Mankit equivalent:** `man-assess` discovers which mankit workflows fit. Less rigorous, no DAILY/LIBRARY classification.

### 13. `prompt-optimizer`
**Purpose:** Analyze a draft prompt, critique it, match to ECC components, output optimized prompt.
**Mechanism:** 6-phase pipeline (analysis only — never executes the task). Matches intent against ECC skills/agents/commands. Advisory: output is an optimized prompt the user can paste, not the task result. Explicit "do not switch into implementation mode" rule.
**Why interesting:** Prompt engineering as a first-class skill. The advisory-only constraint is important — it prevents scope creep. The ECC ecosystem matching means the optimizer has domain knowledge about available tools.
**Mankit equivalent:** None.

### 14. `skill-scout`
**Purpose:** Search for existing skills before creating a new one — prevent duplication.
**Mechanism:** 4 steps: capture intent (keywords/synonyms) → search local installed skills → search remote (GitHub search for SKILL.md files) → evaluate matches. Sourced from a community PR. Provides bash commands for both local and remote search.
**Why interesting:** Meta-skill for skill management. Addresses the commons problem: 232 skills suggest duplication. Greps SKILL.md frontmatter descriptions for semantic matching.
**Mankit equivalent:** None.

### 15. `search-first`
**Purpose:** Research-before-coding — search for existing tools/libraries/patterns before writing custom code.
**Mechanism:** Invokes the researcher agent. Enforces a research gate before implementation starts.
**Why interesting:** Cultural enforcement skill. Prevents the "just implement it" instinct. Directly invokes an agent rather than providing workflow instructions.
**Mankit equivalent:** `research-playbook`. Similar domain.

### 16. `council` (already covered as #2)

### 17. `deep-research`
**Purpose:** Multi-source deep research using Firecrawl and Exa MCPs.
**Mechanism:** Leverages external MCP tools (Firecrawl for web crawling, Exa for semantic search). Synthesizes findings with source attribution and citations.
**Why interesting:** MCP-native design — the skill is the orchestration logic, MCPs are the tools. Decouples research method from research content.
**Mankit equivalent:** `deep-researcher` agent. ECC's version is more MCP-explicit.

### 18. `plankton-code-quality` (already covered as #4)

### 19. `token-budget-advisor`
**Purpose:** Token usage cost optimization guidance.
**Mechanism:** Analyzes context window usage patterns, provides optimization recommendations. Works with `context-budget` command.
**Why interesting:** Cost-consciousness baked in as a skill, not an afterthought. In multi-agent systems, token costs compound quickly.
**Mankit equivalent:** `cost-budgeting` skill. Similar scope.

### 20. `agentic-os`
**Purpose:** Operating-system-like agent orchestration — treat agents as processes with scheduling and resource management.
**Mechanism:** Abstracts multi-agent coordination as an OS metaphor: process scheduling, resource allocation, inter-agent communication.
**Why interesting:** High-level abstraction for enterprise-scale agent deployments. OS metaphor provides familiar mental model for complex orchestration.
**Mankit equivalent:** `agent-teams` skill. Less OS-metaphor framing.

---

## 9. Patterns Worth Adopting for Mankit

### 9.1 Explicit TRIGGER / DO NOT TRIGGER in frontmatter description
ECC's `blueprint` puts trigger conditions directly in the `description` field:
```yaml
description: >-
  ...
  TRIGGER when: user requests a plan, blueprint, or roadmap...
  DO NOT TRIGGER when: task is completable in a single PR...
```
This is read by Claude at invocation time and prevents misuse. Mankit skills have "When to use" sections but not explicit NOT-trigger guards in frontmatter.

### 9.2 Anti-anchoring pattern in multi-agent deliberation
The `council` skill's "write your position first before reading subagents" rule is high-value. Mankit's `multi-persona-predict` could adopt this.

### 9.3 Binary gate adversarial verification (santa-method)
Converting quality review from "advisory" to a hard binary gate (both reviewers must pass) is stronger than Mankit's current advisory reviews. Consider for pre-PR gates.

### 9.4 Write-time quality enforcement (plankton pattern)
PostToolUse hooks that silently auto-fix violations, routing to different models by violation complexity, with config protection — this is a much stronger quality loop than pre-commit hooks alone.

### 9.5 Evidence-based install classification (agent-sort)
DAILY vs LIBRARY classification backed by grep evidence is worth adopting for Mankit's own skill selection. Current `man-assess` is more conversational than evidence-driven.

### 9.6 Iterative retrieval for subagent context
The DISPATCH → EVALUATE → REFINE → CONVERGE loop is immediately adoptable in any orchestration skill where subagents need codebase context.

### 9.7 Strategic compaction as a hook
The `suggest-compact.js` PreToolUse hook that counts tool calls and suggests compaction at phase boundaries is directly implementable in Mankit's hook system.

### 9.8 Hookify as declarative abstraction
ECC's hookify markdown format (YAML frontmatter + regex patterns → hook rules) is significantly more ergonomic than Mankit's current settings.json approach. Worth considering as a layer.

### 9.9 Pass@k metrics for skill evaluation
Adopting pass@k and pass^k from `eval-harness` would give Mankit's `man-eval` a more rigorous measurement framework than simple pass/fail.

### 9.10 Skill scout before skill creation
ECC's `skill-scout` enforces a search gate before creating new skills. Mankit has no equivalent. With 232 skills in ECC and growing numbers in Mankit, this is increasingly important.

---

## 10. Caveats

- ECC's 232 skills are not all equal quality. Some are contributed by the community (noted with `origin: community`) with varying levels of maturity.
- Install modules have `stability` fields: `stable`, `beta`. Several modules are `beta`, meaning APIs/conventions may change.
- ECC targets multiple harnesses: claude, claude-project, cursor, antigravity, codex, opencode, codebuddy, joycode, qwen, zed. Skill behavior may differ across targets.
- No automated skill routing registry — routing is purely LLM inference from frontmatter descriptions. Skills with poor or ambiguous descriptions may not route correctly.
- Sub-skills do not exist in ECC — each skill is a single SKILL.md. Composition is achieved through cross-references and agent delegation.
- The "legacy-command-shims" directory is just a pointer — no actual legacy shim files beyond a README.
- Skills marked `origin: ECC` are maintained by the core team. `origin: community` skills have variable maintenance.

---

## Sources

All findings from local repository at `D:\Projects\_research\ecc` (cloned 2026-05-24).

Key files examined:
- `COMMANDS-QUICK-REF.md` — official 59-command reference
- `commands/*.md` — all 72 command files
- `manifests/install-profiles.json` — 6 install profiles
- `manifests/install-modules.json` — 21 modules with skill paths
- `manifests/install-components.json` — component-to-module mappings
- `skills/*/SKILL.md` — deep-dived: blueprint, santa-method, eval-harness, council, hookify-rules, tdd-workflow, iterative-retrieval, continuous-agent-loop, nanoclaw-repl, plankton-code-quality, strategic-compact, agent-sort, prompt-optimizer, skill-scout, search-first, ralphinho-rfc-pipeline
- `CLAUDE.md` — project architecture description
