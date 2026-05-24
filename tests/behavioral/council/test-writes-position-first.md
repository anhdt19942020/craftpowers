---
scenario: writes-position-first
skill: council
prompt: "Should we use PostgreSQL or MongoDB for our user data?"
timeout: 120
---

## Expected Behavior
1. Agent writes its own position BEFORE spawning any subagent
2. At least 2 subagents spawned after position is written
3. Subagent prompts do NOT contain the main agent's position text

## Compliance Checks
- [ ] Write or Edit tool called before any Agent tool call
- [ ] Agent tool called at least 2 times
- [ ] Agent tool prompts do not quote phrases from the Write output verbatim
