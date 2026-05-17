---
name: research-playbook
description: Self-routing hints for agents to choose the right mode — research, implementation, exploration, or quick-action — before starting work
phase: META
---

# Research Playbook

## Overview

Agents waste context by jumping into implementation when they should research first, or researching when the answer is already in the codebase. This playbook provides routing logic so agents (and the controller) self-select the correct mode before starting.

**Core principle:** Spend 10 seconds routing to save 10 minutes of wasted work.

## The Four Modes

### 🔍 Research Mode
**When:** The answer is NOT in the codebase. Requires external sources.

Signals:
- "How does X work?" (library, protocol, service)
- "What's the best practice for...?"
- "Compare A vs B"
- User mentions unfamiliar domain/tool/API
- Task requires understanding something you haven't seen in repo

**Agent:** `lu-tuc` (deep-researcher)
**Output:** Cited report with recommendations + trade-offs

---

### 🗺️ Exploration Mode
**When:** The answer IS in the codebase but location/pattern is unknown.

Signals:
- "Where do we handle X?"
- "What's the convention for...?"
- "Is there already a utility for...?"
- Planning a feature that touches unknown parts of repo
- Need to understand existing architecture before changing it

**Agent:** `gia-cat-luong` (codebase-explorer)
**Output:** File:line table with patterns and conventions found

---

### 🔨 Implementation Mode
**When:** You know WHAT to build and WHERE. Research/exploration already done.

Signals:
- Plan exists with specific tasks
- Files and patterns are identified
- User says "do it", "implement", "build this"
- Requirements are clear and scoped

**Agent:** `trieu-van` (implementer) or self
**Output:** Working code + tests

---

### ⚡ Quick-Action Mode
**When:** Scope is obvious and bounded. No research needed.

Signals:
- Typo fix, rename, format change
- Single function rewrite with clear spec
- User points to exact location and says what to change
- 1-2 files max

**Agent:** `truong-phi` (quick-fix)
**Output:** Minimal diff + verify

---

## Routing Decision Tree

```
START
│
├─ Do I know WHERE in the codebase to act?
│  ├─ NO → Do I need external info?
│  │       ├─ YES → 🔍 RESEARCH (lu-tuc)
│  │       └─ NO  → 🗺️ EXPLORATION (gia-cat-luong)
│  └─ YES → Is scope ≤ 2 files and obvious?
│           ├─ YES → ⚡ QUICK-ACTION (truong-phi)
│           └─ NO  → 🔨 IMPLEMENTATION (trieu-van)
│
└─ Am I uncertain about the approach?
   ├─ YES → Do I need external validation?
   │        ├─ YES → 🔍 RESEARCH first, then re-route
   │        └─ NO  → 🗺️ EXPLORATION first, then re-route
   └─ NO  → Proceed with current mode
```

## Compound Routing

Some tasks need multiple modes sequentially:

| Pattern | Flow |
|---------|------|
| New feature (unfamiliar domain) | 🔍 Research → 🗺️ Explore → 🔨 Implement |
| New feature (known domain) | 🗺️ Explore → 🔨 Implement |
| Bug in unknown area | 🗺️ Explore → 🔨 Implement |
| Bug with unclear cause | 🔍 Research (if external) OR systematic-debugging (if internal) |
| Library upgrade | 🔍 Research (breaking changes) → 🗺️ Explore (usage) → 🔨 Implement |
| Quick fix | ⚡ Direct |

## When to Re-Route

Switch modes when:
- **Research → Explore:** External research complete, now need to find where to apply it in repo
- **Explore → Research:** Found the code but don't understand the underlying concept
- **Explore → Implement:** Patterns mapped, ready to build
- **Any → Quick-Action:** Realized scope is smaller than expected
- **Quick-Action → Implement:** Realized scope exceeds 2 files

## Anti-Patterns

| Don't | Do instead |
|-------|-----------|
| Research when the answer is in the repo | Explore first — grep before googling |
| Implement without knowing the codebase pattern | Explore first — find conventions |
| Explore externally when you need internal state | Use gia-cat-luong, not lu-tuc |
| Skip routing on ambiguous tasks | Spend 10 seconds classifying before diving in |
| Stay in research mode forever | Set a source limit (3-5), then synthesize and move on |
| Route to implementation without a clear "what" | If you can't state the task in one sentence, you're not ready |

## Integration with Existing Skills

This playbook ROUTES to other skills — it doesn't replace them:

| After routing to... | Invoke... |
|---------------------|-----------|
| 🔍 Research | `lu-tuc` agent |
| 🗺️ Exploration | `gia-cat-luong` agent or `/man-explore` |
| 🔨 Implementation | `writing-plans` → `executing-plans` or `subagent-driven-development` |
| ⚡ Quick-Action | `/man-quick` |
