---
id: MISSING-RATE-LIMIT
severity_max: HIGH
applies_to: all
---

# Missing Rate Limit (Expensive Endpoints)

## Intent

Expensive endpoints (AI inference, image processing, search, email send) without rate limiting → attacker sends 10k req/sec. AI endpoint: $50k/day bill. Email: spam blacklist. Search: DoS.

Distinct from Rule 06 (auth brute force). This covers expensive-resource endpoints.

## Search patterns

- `/api/ai/chat`, `/api/generate`, `/api/search` without rate-limit middleware
- AI SDK calls (`openai.chat.completions.create`, `anthropic.messages.create`) in route handler without throttle
- Image processing (`sharp`, `ffmpeg`) triggered by request without limit

## L1-L4 reasoning

Endpoints processing L1 input with expensive operations. Flag if no rate limiting applied.

## Fix

Rate limiting at route or API gateway level. Combine with: API key auth, user-level quotas, billing alerts.

## Related rules

`06-brute-force` (auth-specific rate limiting)
