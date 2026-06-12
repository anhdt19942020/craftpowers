## Technique Catalog

### Core Exploration Techniques

**1. The Five Whys**
Keep asking "why" to reach root cause before proposing solutions:
- "The user can't log in" → Why? → "Auth token expires" → Why does that matter? → "No refresh mechanism" → Why wasn't it built? → Root cause found.
- Use when: problem statement feels like a symptom, not a cause.

**2. Inversion**
Instead of "how do we make X succeed?", ask "how would we guarantee X fails?"
- Forces exploration of failure modes before committing to design
- Example: "How would we guarantee users abandon the checkout flow?" → reveals friction points to eliminate
- Use when: feeling stuck or over-optimistic about a design

**3. Analogical Reasoning**
Find a solved version of your problem in a different domain:
- "How does air traffic control handle conflicting priorities?" → maps to task scheduling
- "How do banks prevent double-spend?" → maps to distributed writes
- Use when: problem seems novel but likely has prior art in another field

**4. Constraints as Generators**
Add extreme constraints to force creative solutions:
- "What if we couldn't use a database?"
- "What if it had to work for 1 million users on day one?"
- "What if the user had no internet connection?"
- Use when: design space feels narrow and obvious solutions are all unsatisfying

**5. Outside-In Design**
Start from the user-facing output and work backward:
- Write the success message first: "Your order has shipped — track it here"
- Then ask: what data does that require? What systems produce that data?
- Use when: implementation-first thinking is causing over-engineering

**6. Pre-Mortem**
Assume the project failed 6 months from now. Ask: what went wrong?
- Forces identification of risks before commitment
- "We shipped but nobody used it because..." → uncovers adoption assumptions
- Use when: about to finalize a design or commit to an approach

### Anti-Pattern Detection Prompts

Use these during the session to surface hidden assumptions:

| Trigger phrase | Anti-pattern it signals | Probe question |
|----------------|------------------------|----------------|
| "It's simple, we just..." | Complexity blindspot | "What's the hardest part of just doing that?" |
| "Users will obviously..." | Assumption about behavior | "What evidence do we have for that?" |
| "We can always add that later" | Deferred decision debt | "What would change if we had to add it now?" |
| "That's out of scope" | Premature scope closure | "What's the risk if we don't address it?" |
| "The API handles that" | Third-party dependency risk | "What happens if the API changes or goes down?" |

### Named Design Approaches

**YAGNI-first:** Build the minimal thing that solves today's problem. Validate before extending.

**Strangler Fig:** Incrementally replace a legacy system by routing new traffic to new code, keeping old code alive until fully replaced.

**Event Sourcing:** Store events (what happened) instead of state (current value). Enables replay, audit trail, temporal queries.

**CQRS:** Separate read models from write models. Use when read patterns differ significantly from write patterns (e.g., reporting vs. transactions).

**Saga Pattern:** Manage distributed transactions through a sequence of local transactions with compensating actions on failure.

**Circuit Breaker:** Detect failing dependencies and stop calling them temporarily, returning a fallback response instead. Prevents cascade failures.
