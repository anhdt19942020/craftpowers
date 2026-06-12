# Workflow Discovery

Interactive situational recommender — helps find the right mankit workflows for your current situation. Not a knowledge quiz.

<HARD-GATE>
Do NOT skip rounds. Do NOT recommend workflows without completing all 3 rounds. Even if the answer seems obvious from Round 1, Rounds 2-3 refine the recommendation.
</HARD-GATE>

## Step 1 — What are you working on?

Ask the user one question at a time. Cover:
- Are you starting something new, fixing something broken, or maintaining/reviewing something existing?
- Do you have a clear goal or are you exploring?
- Is there a deadline or time pressure?

## Step 2 — What's blocking you?

Based on Step 1, probe with follow-up questions:

| If building new | If debugging | If shipping/reviewing | If exploring/refactoring |
|----------------|-------------|----------------------|------------------------|
| Do you have requirements defined? | Is it reproducible? | Tests passing? | Is scope clear? |
| Are there existing patterns to follow? | Do you know what changed? | PR ready? | Risk level? |
| New subsystem or extension? | How wide is blast radius? | Reviewer assigned? | Files touched? |

Ask follow-ups one at a time. Stop when you have enough to recommend.

## Step 3 — How much agent autonomy?

Ask: "How autonomous should the agent be?"
- **Low:** agent proposes, you approve each step
- **Medium:** agent executes, checks in at key decisions
- **High:** agent runs end-to-end, reports when done

## Step 4 — Generate Workflow Recommendation

Based on answers, recommend from these patterns:

### Building something new
```
Standard: brainstorming → writing-plans → subagent-driven-development
Quick: /man-quick (if scope is 1-2 files, fix is obvious)
Full: brainstorming → writing-plans → agent-teams (9+ files, new patterns)
```

### Hunting a bug
```
/man-debug → fix → requesting code review
Or: systematic-debugging skill directly
```

### Shipping or reviewing
```
verification-before-completion → finishing-a-development-branch → /man-ship
```

### Exploring or refactoring
```
codebase-explorer agent → brainstorming → writing-plans
```

### Autonomy Modifier
- Low autonomy → add explicit review gates to each step
- Medium autonomy → use subagent-driven-development with review after batches
- High autonomy → agent-teams with async check-ins

## Step 5 — Offer Follow-up

After recommendation:
- Offer to kick off the recommended workflow: "Ready to start? I'll invoke [skill] now."
- Or: "Want me to break this into tasks first?"
