---
name: hook-profile
description: View and switch the active hook profile (minimal/standard/strict) to control which quality gates run this session.
---

# Hook Profile

Controls which hooks are active. Three profiles trade off speed vs. quality gates.

## Usage

```
/man-hook-profile                     # Show current profile and active gates
/man-hook-profile minimal             # Switch to minimal (speed)
/man-hook-profile standard            # Switch to standard (default)
/man-hook-profile strict              # Switch to strict (max quality)
```

## Profiles

| Gate | minimal | standard | strict |
|------|---------|----------|--------|
| security_gate | ✅ | ✅ | ✅ |
| privacy_gate | ✅ | ✅ | ✅ |
| credential_scanner | ✅ | ✅ | ✅ |
| naming_gate | ❌ | ✅ | ✅ |
| simplify_gate | ❌ | ✅ | ✅ |
| suggest_compact | ❌ | ✅ | ✅ |
| cost_tracker | ❌ | ✅ | ✅ |
| write_quality | ❌ | ❌ | ✅ |

## When to use each profile

| Profile | Use when |
|---------|---------|
| **minimal** | Debug sessions, rapid prototyping, troubleshooting hook overhead |
| **standard** | Normal development (default) |
| **strict** | Pre-PR, code review, final polish before shipping |

## How to switch

**This session only (env var):**
```bash
MAN_HOOK_PROFILE=minimal claude  # start new session with minimal profile
```

**Persist for this project (`.man.json`):**
```json
{
  "hook_profile": "strict"
}
```

## Behavior when skill is invoked

1. Read current profile via `get_active_profile()` from `hooks/lib/hook_profiles.py`
2. Display: active profile name, source (env var / .man.json / default), gate table with ✅/❌
3. If argument given (`minimal` / `standard` / `strict`):
   - Offer to write `hook_profile` to `.man.json` for persistence
   - Show `export MAN_HOOK_PROFILE=<profile>` for current-session override
4. Note: profile takes effect on NEXT tool call (current hook invocation already dispatched)
