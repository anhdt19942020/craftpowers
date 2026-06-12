---
id: CREDENTIALS-IN-CODE
severity: HIGH
applies_to: all
---

# Credentials In Code

## Intent

Platform credentials (username, password, API keys, TOTP seeds) hardcoded in source code or config files committed to git. Credential leak → unauthorized access to financial accounts.

## Search patterns

- `password = "..."`, `apiKey = "..."` string literals
- `.env` files committed to git (not in .gitignore)
- `storageState` JSON files with cookies committed to git
- TOTP seed as string literal in source
- `Authorization: Bearer ...` hardcoded header

## Fix

Use environment variables or secrets manager:
```typescript
const credentials = {
  username: process.env.PLATFORM_USERNAME,
  password: process.env.PLATFORM_PASSWORD,
  totpSeed: process.env.PLATFORM_TOTP_SEED,
};
```

Add to `.gitignore`: `*.storageState.json`, `.env`, `auth-state/`
