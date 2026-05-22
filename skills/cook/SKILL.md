---
name: cook
description: "End-to-end feature implementation pipeline: scout → plan → implement → review → test → finalize. Unified orchestrator wiring existing mankit skills with hard gates."
phase: IMPLEMENT
---

# Cook — Smart Feature Implementation

End-to-end pipeline with hard gates. One command, full workflow.

**Announce at start:** "I'm using the cook skill for end-to-end implementation."

## Usage

```
/man-cook <task description OR plan path> [--fast|--auto|--parallel|--tdd|--no-test]
```

## Modes

| Flag | Research | Review Gates | Testing | Notes |
|------|----------|-------------|---------|-------|
| (default) | ✓ | User approval each step | ✓ | Interactive |
| `--fast` | ✗ | User approval each step | ✓ | Skip research |
| `--auto` | ✓ | Auto-approve | ✓ | Hands-off |
| `--parallel` | ✓ | User approval each step | ✓ | Multi-agent |
| `--tdd` | ✓ | User approval each step | ✓ | Tests-first per phase |
| `--no-test` | ✓ | User approval each step | ✗ | Risk acknowledged |

Composable: `--tdd` combines with any mode. `--no-test` downgrades test gate to warning.

## Hard Gates

<HARD-GATE-SCOUT-FIRST>
Before planning OR asking questions, scout the codebase. Use `codebase-explorer` agent or inline Grep/Glob.

Mandatory outputs:
1. Project type, language(s), framework(s)
2. Existing files relevant to task
3. Current patterns/conventions for similar features
4. In-flight plans in `./plans/` covering this area
5. Public APIs, schemas, contracts affected

Present 3-6 bullet summary to user before proceeding.

Skip ONLY when input is a plan path (plan already encodes scout).
</HARD-GATE-SCOUT-FIRST>

<HARD-GATE-EXACT-REQUIREMENTS>
Before producing a plan, answer ALL of these concretely (use `AskUserQuestion` to pin down):

1. **Expected output**: concrete artifacts user will see (file paths, feature behavior, API endpoint)
2. **Acceptance criteria**: specific input → output behaviors that MUST work
3. **Scope boundary**: what is explicitly OUT of scope
4. **Constraints**: stack, naming, backward compat, performance
5. **Touchpoints**: existing files to modify (from scout), contracts that must stay stable

Ground every `AskUserQuestion` option in scout findings.
Skip ONLY when input is a plan path.
</HARD-GATE-EXACT-REQUIREMENTS>

<HARD-GATE-NO-CODE-WITHOUT-PLAN>
Do NOT write implementation code until a plan exists and has been reviewed.

Anti-rationalization:
| Thought | Reality |
|---------|---------|
| "Too simple to plan" | Simple tasks have hidden complexity. Plan takes 30 seconds. |
| "I already know how" | Knowing ≠ planning. Write it down. |
| "Let me just start coding" | Undisciplined action wastes tokens. Plan first. |
| "User wants speed" | Fastest path = plan → implement → done. Not: implement → debug → rewrite. |

Exception: user explicitly says "skip planning" or "just code it".
</HARD-GATE-NO-CODE-WITHOUT-PLAN>

<HARD-GATE-NO-SIDE-EFFECTS>
Implementation NOT done until verified side-effect-free:
1. New behavior matches every acceptance criterion
2. All tests pass (including adjacent modules)
3. No business logic regression in touchpoints
4. No new lint/type/build errors
5. Public contracts unchanged unless intentional

If review reveals side effect → STOP. Present options via `AskUserQuestion`:
- Revert and re-plan with stricter scope
- Keep and update dependents to match
- Add compatibility shim
- Accept regression (old behavior was wrong)

Let user decide. Never silently patch around regressions.
</HARD-GATE-NO-SIDE-EFFECTS>

## Pipeline

```
[1. Scout] → [2. Requirements] → [3. Plan] → [4. Implement] → [5. Review] → [6. Test] → [7. Finalize]
```

### Step 1: Scout (MANDATORY unless plan path)
- Dispatch `codebase-explorer` agent or inline scan
- Output: codebase context summary (3-6 bullets)

### Step 2: Requirements (MANDATORY unless plan path)
- Use `AskUserQuestion` to capture 5 requirement dimensions
- Output: concrete requirement block

### Step 3: Plan
- Invoke `writing-plans` skill with scout + requirements context
- Save to `plans/` directory
- **Review gate**: user approves plan before implementation
- For `--fast`: generate minimal inline plan (no full skill invocation)

### Step 4: Implement
- Dispatch `implementer` agent(s) per plan tasks
- For `--parallel`: dispatch independent tasks simultaneously via `dispatching-parallel-agents`
- For `--tdd`: invoke `test-driven-development` skill per phase (tests first, then implement)
- Track progress via TaskCreate/TaskUpdate

### Step 5: Review (MANDATORY)
- Dispatch `code-reviewer` agent with:
  - Scout summary + acceptance criteria as context
  - Explicit checks: (a) criteria met, (b) no regression, (c) no broken contracts, (d) follows patterns, (e) no build errors
- Dispatch `secure-reviewer` if security-sensitive changes detected
- **Review gate**: user approves or requests changes

### Step 6: Test (skip with --no-test)
- Dispatch `test-engineer` agent
- Run existing test suite + new tests
- 100% pass required to proceed
- If failures: dispatch `debugger` agent, fix, re-test (max 3 cycles)

### Step 7: Finalize (MANDATORY — never skip)
1. Update plan files: mark completed tasks, update progress
2. Update `docs/` if changes warrant (dispatch `doc-writer` if major)
3. Ask user: "Commit?" → if yes, stage + commit with conventional message
4. Invoke `man-journal` to log session if non-trivial
5. Suggest next step: `/man-ship` if ready, or next phase if multi-phase

## Subagent Dispatch Table

| Phase | Agent/Skill | Required? |
|-------|------------|-----------|
| Scout | `codebase-explorer` | Yes (unless plan path) |
| Plan | `writing-plans` skill | Yes (unless --fast) |
| Implement | `implementer` | Yes |
| Review | `code-reviewer` | **MUST spawn** |
| Security | `secure-reviewer` | If security-sensitive |
| Test | `test-engineer` | Yes (unless --no-test) |
| Debug | `debugger` | If tests fail |
| Docs | `doc-writer` | If major changes |
| Journal | `journal-writer` | If non-trivial |

**CRITICAL:** Review and test MUST use subagents. Do NOT implement testing or review yourself — DELEGATE.

## Smart Intent Detection

| Input Pattern | Detected Mode |
|---------------|---------------|
| Path to `plan.md` / `phase-*.md` | Execute existing plan (skip scout + requirements) |
| Contains "fast" / "quick" | `--fast` |
| Contains "auto" / "trust me" | `--auto` |
| Contains "parallel" / lists 3+ features | `--parallel` |
| Contains "tdd" / "test first" | `--tdd` |
| Contains "no test" / "skip test" | `--no-test` |
| Default | Interactive |

## Workflow Position

**Typically follows:** `/man-brainstorm`, `/man-plan`, `/man-explore`
**Typically precedes:** `/man-ship`, `/man-journal`
**For bugs use:** `/man-debug` instead
**For tiny edits use:** `/man-quick` instead
