---
name: ubiquitous-language
description: Extract a DDD-style ubiquitous language glossary from the current conversation, flagging ambiguities and proposing canonical terms. Saves to UBIQUITOUS_LANGUAGE.md. Use when user wants to define domain terms, build a glossary, harden terminology, create a ubiquitous language, or mentions "domain model" or "DDD".
phase: THINK
disable-model-invocation: true
---

# Ubiquitous Language

Extract and formalize domain terminology from the current conversation into a consistent glossary, saved to a local file.

## Process

1. **Scan the conversation** for domain-relevant nouns, verbs, and concepts
2. **Identify problems**:
   - Same word used for different concepts (ambiguity)
   - Different words used for the same concept (synonyms)
   - Vague or overloaded terms
3. **Propose a canonical glossary** with opinionated term choices
4. **Write to `UBIQUITOUS_LANGUAGE.md`** in the working directory using the format below
5. **Output a summary** inline in the conversation

## Output Format

Write a `UBIQUITOUS_LANGUAGE.md` file with this structure:

```markdown
# Ubiquitous Language

## Core Terms

| Term | Definition | Aliases to avoid |
|------|------------|-----------------|
| Order | A confirmed purchase request from a customer | Transaction, Cart |
| ...  | ...        | ...             |

## Flagged Ambiguities

- **"user"** — used to mean both `Customer` (external) and `AdminUser` (internal). Recommendation: use `Customer` and `AdminUser` explicitly.

## Example Dialogue

A short exchange demonstrating correct term usage between a developer and domain expert.

> Dev: "When a customer submits an Order..."
> Expert: "Right, and once the Order is confirmed, we send a Receipt..."
```

## Rules

- Be opinionated. When multiple words exist for the same concept, pick the best one and list others as aliases to avoid.
- Flag conflicts explicitly. If a term is used ambiguously, call it out in "Flagged ambiguities" with a clear recommendation.
- Only include terms relevant for domain experts. Skip module/class names unless they have domain meaning.
- Keep definitions tight. One sentence max. Define what it IS, not what it does.
- Show relationships. Use bold term names and express cardinality where obvious.
- Only include domain terms. Skip generic programming concepts unless domain-specific.
- Group terms into multiple tables when natural clusters emerge.
- Write an example dialogue (3-5 exchanges) between a dev and a domain expert demonstrating precise term usage.

## Re-running

When invoked again in the same conversation:
1. Read the existing `UBIQUITOUS_LANGUAGE.md`
2. Incorporate any new terms from subsequent discussion
3. Update definitions if understanding has evolved
4. Re-flag any new ambiguities
5. Rewrite the example dialogue to incorporate new terms
