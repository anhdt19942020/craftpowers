---
name: conversation-analyzer
description: Manually trigger conversation analysis to detect user corrections and generate instinct candidates. Usually runs automatically at session end when enabled in .man.json.
---

# Conversation Analyzer

Scans the current session for correction patterns and generates instinct candidates in `.claude/instincts/candidates/`.

## Usage

```
/man-analyze
```

## What It Does

1. Scans conversation for user corrections ("no not that", "always use X", "stop doing Y")
2. Extracts context around each correction (±3 lines)
3. Generates candidate instinct files in `.claude/instincts/candidates/`
4. Candidates require human review before promotion

## Candidate Lifecycle

```
Detected correction → candidates/ (confidence 0.5-0.6)
  → Human review → personal/ (confidence 0.7+) → Active instinct
  → Human reject → delete candidate
```

## Manual Promotion

To promote a candidate to an active instinct:
1. Read the candidate file in `.claude/instincts/candidates/`
2. Edit: write a clear Action description
3. Raise confidence to 0.7+
4. Move to `.claude/instincts/personal/`
5. Delete the candidate file

Or use `/man-instinct create` to create the instinct directly from the candidate's context.

## Auto-Run at Session End

Enable automatic analysis at session end via `.man.json`:

```json
{
  "conversation_analyzer": {
    "enabled": true
  }
}
```

When enabled, the Stop hook runs analysis automatically after every session.
