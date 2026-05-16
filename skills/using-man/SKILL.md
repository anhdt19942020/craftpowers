---
name: using-man
description: How to find and use skills. Loaded at session start. Requires Skill tool invocation before any response.
phase: META
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Instruction Priority

Superpowers skills override default system prompt behavior, but **user instructions always take precedence**:

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **Superpowers skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If CLAUDE.md, GEMINI.md, or AGENTS.md says "don't use TDD" and a skill says "always use TDD," follow the user's instructions. The user is in control.

## How to Access Skills

**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you—follow it directly. Never use the Read tool on skill files.

**In Copilot CLI:** Use the `skill` tool. Skills are auto-discovered from installed plugins. The `skill` tool works the same as Claude Code's `Skill` tool.

## Platform Adaptation

Skills use Claude Code tool names. For Copilot CLI tool equivalents, see `references/copilot-tools.md`.

# Using Skills

## The Rule

**Invoke relevant or requested skills BEFORE any response or action.** Even a 1% chance a skill might apply means that you should invoke the skill to check. If an invoked skill turns out to be wrong for the situation, you don't need to use it.

```dot
digraph skill_flow {
    "User message received" [shape=doublecircle];
    "About to EnterPlanMode?" [shape=doublecircle];
    "Already brainstormed?" [shape=diamond];
    "Invoke brainstorming skill" [shape=box];
    "Might any skill apply?" [shape=diamond];
    "Invoke Skill tool" [shape=box];
    "Announce: 'Using [skill] to [purpose]'" [shape=box];
    "Has checklist?" [shape=diamond];
    "Create TodoWrite todo per item" [shape=box];
    "Follow skill exactly" [shape=box];
    "Respond (including clarifications)" [shape=doublecircle];

    "About to EnterPlanMode?" -> "Already brainstormed?";
    "Already brainstormed?" -> "Invoke brainstorming skill" [label="no"];
    "Already brainstormed?" -> "Might any skill apply?" [label="yes"];
    "Invoke brainstorming skill" -> "Might any skill apply?";

    "User message received" -> "Might any skill apply?";
    "Might any skill apply?" -> "Invoke Skill tool" [label="yes, even 1%"];
    "Might any skill apply?" -> "Respond (including clarifications)" [label="definitely not"];
    "Invoke Skill tool" -> "Announce: 'Using [skill] to [purpose]'";
    "Announce: 'Using [skill] to [purpose]'" -> "Has checklist?";
    "Has checklist?" -> "Create TodoWrite todo per item" [label="yes"];
    "Has checklist?" -> "Follow skill exactly" [label="no"];
    "Create TodoWrite todo per item" -> "Follow skill exactly";
}
```

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |
| "I already loaded a process skill, domain skills come later" | Domain knowledge skills load CONCURRENTLY with process skills, not after. |

## Skill Priority

When multiple skills could apply, use this order:

1. **Process skills first** (brainstorming, debugging) - these determine HOW to approach the task
2. **Domain knowledge skills concurrently** (websocket-patterns, nodejs-patterns, laravel-patterns) - load immediately when domain is identified, even during brainstorming, even before clarifying questions
3. **Implementation workflow skills last** (frontend-design, mcp-builder) - load when starting to build

"Let's build X" → brainstorming + domain knowledge skills simultaneously, then implementation skills.
"Fix this bug" → debugging + domain knowledge skills simultaneously.
"Socket not reliable" → brainstorming + websocket-patterns immediately — NOT deferred until implementation.

## Skill Types

**Rigid** (TDD, debugging): Follow exactly. Don't adapt away discipline.

**Flexible** (patterns): Adapt principles to context.

The skill itself tells you which.

## Scale-Adaptive Routing

Before invoking a workflow skill, assess task complexity and route to the appropriate pipeline depth. This prevents over-engineering trivial tasks and under-planning complex ones.

**Auto-detect complexity using these signals:**

| Signal | Quick | Standard | Full |
|--------|-------|----------|------|
| Files touched | 1-2 | 3-8 | 9+ or cross-layer |
| New abstractions needed | 0 | 1-2 | 3+ or new patterns |
| Existing test changes | 0-1 | 2-5 | 6+ or new test infra |
| Cross-system dependencies | none | 1 system | 2+ systems |
| Ambiguity in request | none (exact fix known) | some (approach clear) | high (needs exploration) |

**Route to pipeline depth:**

```
QUICK (minutes, no plan needed):
→ /man-quick or dispatch truong-phi
- Typo, rename, single-function fix, config change
- Scope: 1-2 files, fix is obvious, no design decisions

STANDARD (30min-2hr, plan needed):
→ brainstorming → writing-plans → subagent-driven-development
- New feature within existing patterns
- Bug requiring investigation
- Scope: multiple files, clear architecture, follows existing conventions

FULL (hours-days, team needed):
→ brainstorming → writing-plans → agent-teams
- Cross-layer feature (frontend + backend + tests)
- New subsystem or architectural change
- Scope: 9+ files, new patterns, multiple systems coordinate
```

**Decision rules:**
- If ALL signals point Quick → skip brainstorming, go direct
- If ANY signal points Full → use Full (complexity is driven by the hardest dimension)
- Default to Standard when mixed signals
- User can always override: "just do it quick" or "I want a full plan for this"

**Do NOT over-engineer:**
- A 1-file bug fix does not need a brainstorming session
- A config change does not need a Task DAG
- A rename does not need agent-teams

**Do NOT under-plan:**
- A "simple feature" that touches 5 files needs at minimum Standard
- Anything crossing system boundaries (API + frontend + DB) is Full regardless of perceived simplicity

## User Instructions

Instructions say WHAT, not HOW. "Add X" or "Fix Y" doesn't mean skip workflows.
