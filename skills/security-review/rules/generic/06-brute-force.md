---
id: BRUTE-FORCE
severity_max: HIGH
applies_to: all
---

# Brute Force (Missing Auth Rate Limit)

## Intent

Login/signup/password-reset/OTP endpoints with no rate limit. Attacker runs 1M requests to crack passwords or OTP (6-digit = 1M combinations = 100% hit rate).

## Search patterns

- Login route handlers with no rate-limit middleware
- `/api/auth/login`, `/api/auth/reset`, `/api/otp/verify` without `rateLimit()`
- Express routes without `express-rate-limit`
- Flask routes without `@limiter.limit()`
- No `X-RateLimit-*` headers in response

## L1-L4 reasoning

Auth endpoints inherently process L1 input (credentials). Flag if no rate limiting middleware is applied before the handler.

## Fix

- Express: `const limiter = rateLimit({ windowMs: 15*60*1000, max: 10 }); app.use('/api/auth', limiter)`
- Flask: `@limiter.limit("5 per minute")`
- Also: progressive delays, account lockout after N failures, CAPTCHA

## Related rules

`18-missing-rate-limit` (expensive non-auth endpoints)
