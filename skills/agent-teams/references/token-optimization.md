## Token Optimization

### 1. Model selection per role

Lead stays Opus. Downgrade teammates:

| Role | Model | Why |
|------|-------|-----|
| Lead (coordinator) | Opus | Judgment, coordination |
| Implementer | Sonnet | Mechanical coding |
| Reviewer | Sonnet or Opus | Depends on complexity |
| Research/grep | Haiku | Read-only, simple |

Set default: `teammateDefaultModel: "sonnet"` in `~/.claude.json`.

### 2. Minimal spawn prompts

Teammates auto-load CLAUDE.md, AGENTS.md, skills. Spawn prompt = role + task reference only:

```
# ❌ 2000 tokens — redundant context
"You are an implementer. Here's the full project context, architecture, patterns..."

# ✅ 100 tokens — teammates load context themselves
"You are triệu-vân. Check TaskList for your tasks. Own files in src/api/. Mark DONE via TaskUpdate."
```

### 3. Delta-only SendMessage

Send only what changed, not full context:

```
# ❌ 5000 tokens
SendMessage("Here's everything I found: [full logs, full context]...")

# ✅ 200 tokens
SendMessage("API ready. Endpoints: GET/POST /profile. Schema: {name, email, avatar_url}")
```

### 4. Spawn on unblock, not upfront

See Lead Loop step 2 — this is the canonical rule for spawning. Don't spawn blocked teammates:

```
# ❌ Spawn all 3 upfront — B and C idle while A works
Agent A → working
Agent B → idle (blocked by A) → burning tokens
Agent C → idle (blocked by A,B) → burning tokens

# ✅ Spawn when unblocked
Agent A → working
[A done] → spawn Agent B
[B done] → spawn Agent C
```

### 5. Shutdown immediately after task completion

Idle teammates don't burn tokens per turn (no input → no inference). What they DO consume:
- A team-member slot (lead must track them, send-on-purpose discipline weakens)
- Memory + process footprint on the host
- Risk of stale context — when you finally wake them, they may have drifted from current state

```
Teammate finishes → SendMessage shutdown → clean state
❌ Leave idle "in case we need them" → drift risk + clutter, even though token cost is near zero
```

### 6. Hybrid mode — mix teams with fire-and-forget

Not everything needs a team. In the same session:

| Task type | Mode | Relative cost |
|-----------|------|---------------|
| Independent research | Fire-and-forget subagent (Haiku) | ~0.3x |
| Independent implementation | Fire-and-forget subagent (Sonnet) | ~1x |
| Coordinated cross-layer work | Native Agent Team | ~3-4x |

### Combined impact

All optimizations together reduce Agent Teams from ~4x to ~1.5-2x single session cost.
