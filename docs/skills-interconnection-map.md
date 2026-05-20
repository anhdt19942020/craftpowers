# Mankit Skills Interconnection Map

> 40+ skills · 60+ connections · 1 ecosystem

## Core Architecture

Mankit's skill system is designed as an **interconnected ecosystem** — not a collection of isolated tools. Skills call each other, delegate subtasks, and compose workflows automatically.

## Dependency Graph

```
writing-plans (planner)
├── brainstorming → research-playbook, design-exploration
├── man-assess → using-man
└── generates plan consumed by executing-plans

executing-plans (orchestrator)
├── writing-plans → brainstorming, research-playbook
├── subagent-driven-development → dispatching-parallel-agents, using-git-worktrees
├── systematic-debugging → debug-flight-recorder
├── verification-before-completion
└── finishing-a-development-branch → release-prep

agent-teams (meta-orchestrator)
├── subagent-driven-development, executing-plans
├── agent-introspection
└── wraps each as multi-agent template

brainstorming → design-exploration, research-playbook, writing-plans
systematic-debugging → debug-flight-recorder, agent-introspection
finishing-a-development-branch → release-prep, verification-before-completion
```

## Layer Model

### Layer 1 — Orchestrators
| Skill | Role | Outbound deps |
|-------|------|---------------|
| **executing-plans** | Central orchestrator for feature implementation lifecycle | 6+ skills |
| **agent-teams** | Multi-session parallel collaboration wrapper | 5 skills |
| **subagent-driven-development** | Parallel subagent dispatch with worktree isolation | 3 skills |

### Layer 2 — Workflow Hubs
| Skill | Role | Called by | Calls |
|-------|------|----------|-------|
| **writing-plans** | Architecture & planning | executing-plans, agent-teams, brainstorming | brainstorming, research-playbook |
| **brainstorming** | Solution ideation | writing-plans, systematic-debugging | design-exploration, research-playbook |
| **systematic-debugging** | Root cause investigation | executing-plans, man-fix | debug-flight-recorder, agent-introspection |
| **finishing-a-development-branch** | Branch completion gate | executing-plans | release-prep, verification-before-completion |
| **verification-before-completion** | Pre-commit evidence gate | executing-plans, finishing-a-development-branch | — |
| **research-playbook** | Mode routing + research dispatch | writing-plans, brainstorming | — |
| **dispatching-parallel-agents** | Parallel agent coordination | subagent-driven-development | using-git-worktrees |

### Layer 3 — Utility Providers
Pure capability providers — referenced by hub skills but don't call other skills.

| Skill | Domain | Referenced by |
|-------|--------|---------------|
| **debug-flight-recorder** | Temp instrumentation & cleanup | systematic-debugging |
| **agent-introspection** | Agent misbehavior diagnosis | systematic-debugging, agent-teams |
| **design-exploration** | Competing design via parallel agents | brainstorming, writing-plans |
| **using-git-worktrees** | Isolated worktree management | subagent-driven-development, dispatching-parallel-agents |
| **effort-tuning** | Model/effort selection per task | subagent-driven-development, agent-teams |
| **release-prep** | Pre-deploy audit | finishing-a-development-branch |
| **context-management** | Context window strategy | executing-plans, agent-teams |
| **session-recovery** | Post-compact state rebuild | executing-plans |
| **cost-budgeting** | Token spend estimation | agent-teams, subagent-driven-development |
| **engineering-principles** | SOLID/DRY/KISS enforcement | — |
| **source-driven-development** | Doc-grounded implementation | — |
| **api-and-interface-design** | Interface contracts | — |
| **nodejs-patterns** | Node.js best practices | — |
| **frontend-ui-engineering** | Production UI patterns | — |
| **websocket-patterns** | Real-time communication | — |

### Layer 4 — Standalone Skills
Domain-specific tools operating independently.

`adversarial-design` · `architecture-decision-records` · `browser-testing-with-devtools` · `cloud-routines` · `event-driven-agents` · `generate-project-context` · `git-guardrails-claude-code` · `man-assess` · `receiving-code-review` · `requesting-code-review` · `setup-pre-commit` · `structured-refactoring` · `test-driven-development` · `to-issues` · `to-prd` · `ubiquitous-language` · `using-man` · `writing-skills`

## Hub Connectivity (most referenced)

| Skill | Inbound references |
|-------|-------------------|
| writing-plans | 4 (executing-plans, agent-teams, brainstorming, man-plan) |
| brainstorming | 3 (writing-plans, systematic-debugging, man-brainstorm) |
| systematic-debugging | 3 (executing-plans, man-fix, debug-flight-recorder) |
| verification-before-completion | 3 (executing-plans, finishing-a-development-branch, man-ship) |
| research-playbook | 3 (writing-plans, brainstorming, man-explore) |
| using-git-worktrees | 2 (subagent-driven-development, dispatching-parallel-agents) |
| release-prep | 2 (finishing-a-development-branch, man-release) |
| agent-introspection | 2 (systematic-debugging, agent-teams) |

## Key Architectural Patterns

1. **executing-plans is the nucleus** — mandatory for all feature implementation, orchestrates 6+ skills through the full lifecycle: writing-plans → brainstorming → subagent-driven-development → systematic-debugging → verification-before-completion → finishing-a-development-branch

2. **Hub-and-spoke topology** — orchestrators (executing-plans, agent-teams) fan out to workflow hubs (writing-plans, systematic-debugging, finishing-a-development-branch), which fan out to utility providers

3. **Cross-hub references** — systematic-debugging calls debug-flight-recorder, brainstorming calls writing-plans, finishing-a-development-branch calls release-prep — creating a resilient mesh, not a rigid tree

4. **Utility layer is stateless** — debug-flight-recorder, agent-introspection, design-exploration provide pure capabilities without calling other skills, keeping the dependency graph acyclic at the leaf level

5. **agent-teams wraps everything** — for multi-session parallel work, agent-teams composes executing-plans + writing-plans + research-playbook + subagent-driven-development + agent-introspection into coordinated agent templates

6. **man-* commands are entry points** — man-plan, man-fix, man-ship, man-brainstorm, man-explore are thin wrappers that invoke hub skills; they are gateways, not workflow logic
