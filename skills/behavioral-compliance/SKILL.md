---
name: behavioral-compliance
description: Test whether agents follow skill instructions. Runs automated sessions via `claude -p` and checks tool traces for expected behavior patterns. MUST BE USED when: verifying a new skill works, regression testing after skill changes.
---

# Behavioral Compliance Testing

Automated verification that agents follow their skill instructions. Uses `claude -p` (headless mode) to run test scenarios, then analyzes the tool trace for compliance.

## Usage

```
/man-compliance <skill-name> [--scenario <name>]
```

## How It Works

### Step 1: Define Test Scenarios

Create test scenarios in `tests/behavioral/<skill-name>/`:

```markdown
# tests/behavioral/council/test-writes-position-first.md
---
scenario: writes-position-first
skill: council
prompt: "Should we use PostgreSQL or MongoDB for our user data?"
---

## Expected Behavior
1. Agent writes its own position BEFORE spawning any subagent
2. At least 2 subagents spawned after position is written
3. Subagent prompts do NOT contain the main agent's position

## Compliance Checks
- [ ] Write/Edit tool called before any Agent tool call
- [ ] Agent tool called at least 2 times
- [ ] Agent tool prompts do not contain phrases from the Write output
```

### Step 2: Run Scenario

```bash
claude -p "You have the council skill. Use it to answer: Should we use PostgreSQL or MongoDB?" --output-format json 2>trace.json
```

### Step 3: Analyze Tool Trace

Parse the JSON trace and check each compliance criterion:

```python
trace = load_trace("trace.json")
tool_calls = extract_tool_calls(trace)

# Check: Write before Agent
write_index = first_index(tool_calls, "Write")
agent_index = first_index(tool_calls, "Agent")
assert write_index < agent_index, "Position must be written before spawning agents"

# Check: Agent spawned 2+ times
agent_count = count(tool_calls, "Agent")
assert agent_count >= 2, "Must spawn at least 2 perspectives"
```

### Step 4: Report

```markdown
## Compliance Report: council/writes-position-first

| Check | Status | Evidence |
|-------|--------|----------|
| Write before Agent | ✅ PASS | Write at call #3, Agent at call #5 |
| 2+ agents spawned | ✅ PASS | 3 Agent calls found |
| No position leak | ❌ FAIL | Agent #2 prompt contains "PostgreSQL is better" |

**Overall: FAIL** — 1 compliance violation detected
```

## File Structure

```
tests/behavioral/
├── README.md
├── council/
│   ├── test-writes-position-first.md
│   └── test-no-position-leak.md
├── santa-method/
│   ├── test-two-reviewers.md
│   └── test-fresh-context-on-retry.md
└── writing-plans/
    ├── test-cold-execution.md
    └── test-no-placeholders.md
```

## Scenario Template

```markdown
---
scenario: <kebab-case-name>
skill: <skill-name>
prompt: "<the prompt to send to claude -p>"
timeout: 120
---

## Expected Behavior
[describe what SHOULD happen]

## Compliance Checks
- [ ] [specific, observable check on tool trace]
- [ ] [another check]
```

## Limitations

- Requires `claude` CLI with `-p` flag (piped mode)
- Each test scenario costs API tokens
- Cannot test interactive flows (AskUserQuestion)
- Tool trace format may change between Claude Code versions

## When to Use

- After modifying a skill's instructions
- Before shipping a new skill
- Periodic regression testing
- After reports of agents not following instructions
