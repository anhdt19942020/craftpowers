---
id: NO-TOTP-DYNAMIC
severity: LOW
applies_to: all
---

# No TOTP Dynamic Generation

## Intent

Automation uses pre-generated OTP codes or requires manual 2FA input. Pre-generated codes expire quickly (30s), manual input blocks automation. Both approaches are unreliable for 24/7 operation.

## Search patterns

- Hardcoded OTP values: `otp = "123456"`
- `readline` or `prompt` for OTP input in automation flow
- No `otplib`, `speakeasy`, or `pyotp` import
- TOTP seed stored outside secrets manager

## Fix

Store TOTP seed in vault, generate dynamically:
```typescript
import { authenticator } from 'otplib';

const totpSeed = process.env.PLATFORM_TOTP_SEED;
const otp = authenticator.generate(totpSeed);
await page.getByLabel('OTP').fill(otp);
```

Python:
```python
import pyotp
totp = pyotp.TOTP(os.environ['PLATFORM_TOTP_SEED'])
await page.get_by_label('OTP').fill(totp.now())
```
