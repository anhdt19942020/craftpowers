---
name: automation-review
description: "Review web automation code for financial operations (topup, payment, transactions). Detects double-spend, race conditions, credential leaks, flaky selectors, missing audit trails. Use when: reviewing Playwright/Puppeteer automation, topup bots, payment flows."
phase: REVIEW
---

# Automation Review

Review browser automation code that performs financial operations on third-party web platforms — topup, balance transfers, payments, account management.

## When to use

- Code uses Playwright, Puppeteer, or Selenium for financial operations
- Automation interacts with third-party payment/topup platforms
- Code handles credentials, sessions, or financial transactions programmatically
- User says "review automation", "check topup code", "review bot"

## Workflow

### Step 1 — Detect automation stack

| Signal | Stack |
|--------|-------|
| `playwright` import | Playwright (Node/Python) |
| `puppeteer` import | Puppeteer |
| `selenium` import | Selenium |
| `page.goto`, `page.click`, `page.fill` | Browser automation |
| `storageState`, `context.cookies` | Session management |

### Step 2 — Classify operation type

| Pattern | Type | Risk tier |
|---------|------|-----------|
| topup, recharge, deposit, add funds | Financial — topup | CRITICAL |
| transfer, withdraw, send money | Financial — transfer | CRITICAL |
| login, authenticate, session | Auth management | HIGH |
| scrape, extract, monitor | Data collection | MEDIUM |

### Step 3 — Load and apply rules

Load all rules from `rules/`. Apply each rule against the codebase, prioritizing CRITICAL rules for financial operations.

### Step 4 — Render report

Group findings by severity. For each finding: quote code, explain the financial risk, provide concrete fix.

## Reference Guide — Rules

### CRITICAL (financial loss / duplication)

| # | Rule | File |
|---|------|------|
| 01 | Missing Idempotency Key | `rules/01-missing-idempotency.md` |
| 02 | Retry Without Status Query | `rules/02-retry-without-status-check.md` |
| 03 | No Concurrent Lock | `rules/03-no-concurrent-lock.md` |
| 04 | No Balance Verification | `rules/04-no-balance-verification.md` |

### HIGH (reliability / security)

| # | Rule | File |
|---|------|------|
| 05 | Credentials In Code | `rules/05-credentials-in-code.md` |
| 06 | Sleep Instead of Proper Waits | `rules/06-sleep-instead-of-waits.md` |
| 07 | No Screenshot On Failure | `rules/07-no-screenshot-on-failure.md` |
| 08 | No Stale Session Detection | `rules/08-no-stale-session-detection.md` |
| 09 | No Structured Audit Log | `rules/09-no-audit-log.md` |
| 10 | Session Cookies In Logs | `rules/10-session-cookies-in-logs.md` |
| 11 | Shared Session Across Workers | `rules/11-shared-session-across-workers.md` |

### MEDIUM (resilience / maintainability)

| # | Rule | File |
|---|------|------|
| 12 | Hardcoded CSS/XPath Selectors | `rules/12-hardcoded-selectors.md` |
| 13 | No Stealth Plugin | `rules/13-no-stealth-plugin.md` |
| 14 | No Circuit Breaker | `rules/14-no-circuit-breaker.md` |
| 15 | No Operation ID Propagation | `rules/15-no-operation-id.md` |
| 16 | Hardcoded Navigation Waits | `rules/16-hardcoded-navigation-waits.md` |

### LOW (maintenance)

| # | Rule | File |
|---|------|------|
| 17 | No Session TTL / Rotation | `rules/17-no-session-ttl.md` |
| 18 | No TOTP Dynamic Generation | `rules/18-no-totp-dynamic.md` |

## Output format

```
## Automation Review Report

| Stack | [Playwright/Puppeteer/Selenium] |
| Operation type | [topup/transfer/scrape] |
| Files scanned | N |
| Scan date | YYYY-MM-DD |

**VERDICT: PASS / WARN / FAIL**

### CRITICAL — fix before deploy
[Findings with financial loss risk]

### HIGH — fix soon
[Reliability and security findings]

### MEDIUM — improve
[Resilience findings]

### LOW — nice to have
[Maintenance improvements]

### Summary
| Severity | Count |
|----------|-------|
| Critical | N |
| High | N |
| Medium | N |
| Low | N |
```

## Hard refusals

- Never edit source code. Report only.
- If asked to fix: "Out of scope — automation-review audits, it does not edit. Dispatch an implementer agent for fixes."
