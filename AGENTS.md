# Mankit — Agent Guidelines

This file provides guidance for AI coding agents (Codex, OpenAI o-series, and other agents that read AGENTS.md).

## What This Plugin Does

Mankit is a complete AI coding methodology plugin that combines:
- **Superpowers** (Jesse Vincent) — structured workflows: brainstorm → plan → TDD → review → ship
- **Matt Pocock's craft skills** — design tools: adversarial design, ADRs, ubiquitous language, structured refactoring

## Skills Available

When working in this repo, the following skills are available:

### Design & Planning
- **adversarial-design** — Stress-test a design by relentlessly questioning every decision branch
- **design-exploration** — Generate 3+ parallel designs via sub-agents, compare trade-offs
- **brainstorming** — Socratic design refinement with Socratic questioning
- **writing-plans** — Break work into 2–5 minute tasks with exact file paths and verification steps

### Architecture
- **architecture-decision-records** — Identify architectural improvement opportunities and record decisions as ADRs
- **ubiquitous-language** — Extract a DDD-style glossary and standardize domain language before coding

### GitHub Integration
- **to-prd** — Convert conversation context into a PRD and submit as a GitHub issue
- **to-issues** — Break a plan into independently-grabbable vertical-slice GitHub issues

### Development
- **test-driven-development** — Enforced RED-GREEN-REFACTOR cycle
- **subagent-driven-development** — Dispatch subagents per task with two-stage review
- **executing-plans** — Batch execution with checkpoints
- **using-git-worktrees** — Isolated workspace per feature branch

### Refactoring & Tooling
- **structured-refactoring** — Refactor plan with tiny commits, submitted as GitHub issues
- **setup-pre-commit** — Install Husky pre-commit hooks with lint-staged, type checking, tests
- **git-guardrails-claude-code** — Block dangerous git commands before Claude executes them

### Quality & Review
- **systematic-debugging** — 4-phase root cause process
- **verification-before-completion** — Verify work is actually done before claiming complete
- **requesting-code-review** — Pre-review checklist
- **receiving-code-review** — Structured response to review feedback

## Recommended Workflow

1. **brainstorming** → refine the idea
2. **adversarial-design** → stress-test before committing
3. **ubiquitous-language** → standardize domain language
4. **writing-plans** → break into tasks
5. **to-prd** + **to-issues** → create GitHub issues
6. **using-git-worktrees** → isolated workspace
7. **subagent-driven-development** / **executing-plans** → implement with review
8. **test-driven-development** → RED-GREEN-REFACTOR always
9. **requesting-code-review** → pre-submit checklist
10. **finishing-a-development-branch** → verify and merge

## Contributing

See CLAUDE.md for contributor guidelines. The rules apply equally to all agents.
