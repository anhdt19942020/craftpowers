---
name: debug-flight-recorder
description: Instrument code with temporary console.logs, run repro, collect logs, then auto-cleanup. Saves 20 min of manual add/remove. Use when bug location is unclear and you need to trace execution flow.
phase: INVESTIGATE
---

# Debug Flight Recorder

Automated instrument → repro → collect → cleanup cycle for tracing bugs through code.

## When to Use

- Bug location unclear, need to trace execution flow
- Multi-component system, need to find which layer fails
- "It works locally but fails in X" scenarios
- Complement to `systematic-debugging` Phase 1 evidence gathering

**Don't use when:**
- Bug location is obvious (just fix it)
- You have a debugger attached (use breakpoints instead)
- Issue is in third-party code you can't instrument

## The Marker

All logs use this exact marker for safe cleanup:

```
[FLIGHT-RECORDER]
```

Every instrumented line ends with a comment containing this marker.

## Step 0: Preflight

```bash
git status --porcelain
```

**If dirty:** "You have uncommitted changes. Stash or commit first so I can safely revert the debug logs later."

Capture snapshot:
```bash
git rev-parse HEAD > .flight-recorder-sha
```

## Step 1: Understand the Bug

Ask:
1. Steps to reproduce?
2. What should happen?
3. What actually happens?
4. Any error message?

## Step 2: Identify Instrument Points

From description, find 3-8 strategic points (never more):

| Site Type | Why |
|-----------|-----|
| Entry point | Route handler, form submit, CLI entry |
| Key branching | `if` that decides success vs error path |
| External calls | `fetch`, database, third-party APIs |
| State mutations | `setState`, `dispatch`, store updates |
| Before/after crash | Lines around the error |

```bash
git grep -n --files-with-matches '<keyword>' src/ lib/ app/
```

Present candidates:
```
I'll add logs at 5 suspected points:
  1. app/checkout/page.tsx:34     — form submit handler
  2. app/api/checkout/route.ts:12 — entry route handler
  3. lib/cart.ts:56               — calcTotal
  4. lib/stripe.ts:23             — session create
  5. lib/db.ts:89                 — save order

Options:
  y           — add logs and run repro
  skip 3      — remove point #3
  add <path>:<line> — add another point
  cancel      — abort
```

## Step 3: Instrument

### Pattern by Site Type

**Function entry:**
```ts
export function calcTotal(items: Item[]) {
  console.log('[FLIGHT-RECORDER] lib/cart.ts:calcTotal entry', { items_count: items.length, items_sample: items.slice(0,2) }); // [FLIGHT-RECORDER]
  // ... existing body
}
```

**Before/after external call:**
```ts
console.log('[FLIGHT-RECORDER] pre-db', { user_id: user?.id, payload }); // [FLIGHT-RECORDER]
const { data, error } = await db.from('orders').insert(payload);
console.log('[FLIGHT-RECORDER] post-db', { data, error }); // [FLIGHT-RECORDER]
```

**Conditional branch:**
```ts
if (user.isPremium) {
  console.log('[FLIGHT-RECORDER] branch:premium', { user_id: user.id }); // [FLIGHT-RECORDER]
  // premium path
} else {
  console.log('[FLIGHT-RECORDER] branch:standard', { user_id: user.id }); // [FLIGHT-RECORDER]
  // standard path
}
```

**State mutation:**
```ts
console.log('[FLIGHT-RECORDER] pre-setState', { prev: state, next: newState }); // [FLIGHT-RECORDER]
setState(newState);
```

### What to Log

| Do Log | Don't Log |
|--------|-----------|
| Counts, lengths | Full arrays/objects (sample instead) |
| IDs, keys | Passwords, tokens, secrets |
| Error objects | PII (emails, names, addresses) |
| Boolean flags | Credit card numbers |
| Enum values | Session data |

## Step 4: Run Repro

```
Logs added. Now reproduce the bug:

1. Start the app: <dev command>
2. Follow your repro steps
3. Watch console output
4. When done, paste the [FLIGHT-RECORDER] lines here
   (or I'll read from terminal output)
```

## Step 5: Analyze Logs

Build timeline from collected logs:

```
Timeline:
  1. [FLIGHT-RECORDER] form submit     — { items: 3 }     ✓
  2. [FLIGHT-RECORDER] pre-db          — { user_id: 42 }  ✓
  3. [FLIGHT-RECORDER] post-db         — { error: "..." } ← FAILURE HERE
  4. [FLIGHT-RECORDER] calcTotal       — (never reached)
```

**Analysis:** Last log that fired + first that didn't = root cause lives between them.

## Step 6: Propose Fix or Drill Deeper

Based on analysis:

**If root cause found:**
- Propose specific fix
- Proceed to cleanup (Step 7)
- Then apply fix on clean tree

**If need more detail:**
- Add 2-3 more logs around suspected area
- Re-run repro
- Repeat until root cause is clear

## Step 7: Cleanup (MANDATORY)

**This step ALWAYS runs, even if user cancels or something fails.**

```bash
git grep -l '\[FLIGHT-RECORDER\]' | xargs -I {} sed -i '' '/\[FLIGHT-RECORDER\]/d' {}
```

Or on Windows:
```powershell
Get-ChildItem -Recurse -Include *.ts,*.tsx,*.js,*.jsx | ForEach-Object {
  (Get-Content $_.FullName) | Where-Object { $_ -notmatch '\[FLIGHT-RECORDER\]' } | Set-Content $_.FullName
}
```

Verify cleanup:
```bash
git grep '\[FLIGHT-RECORDER\]'
```

**If cleanup fails or build breaks:**
```bash
git checkout -- .
# or hard reset to snapshot
git reset --hard $(cat .flight-recorder-sha)
rm .flight-recorder-sha
```

## Hard Rules

- **Max 8 instrument points** — more = cognitive overload, worse signal
- **Clean working tree required** — revert path must stay safe
- **NEVER commit marker comments** — cleanup is mandatory
- **NEVER log secrets** — passwords, tokens, PII
- **Cleanup runs even on Ctrl-C** — non-negotiable

## Integration with systematic-debugging

This skill is a **tool** for Phase 1 (Root Cause Investigation) of `systematic-debugging`:

```
systematic-debugging Phase 1
  └── "Gather Evidence in Multi-Component Systems"
      └── debug-flight-recorder (this skill)
          └── instrument → repro → analyze → cleanup
```

After flight recorder identifies the failing component, return to systematic-debugging Phase 2 (Pattern Analysis).

## Quick Reference

| Step | Action | Output |
|------|--------|--------|
| 0 | Preflight | Clean tree, snapshot SHA |
| 1 | Understand | Bug description |
| 2 | Identify | 3-8 instrument points |
| 3 | Instrument | Logs with markers |
| 4 | Repro | User triggers bug |
| 5 | Analyze | Timeline, failure point |
| 6 | Propose | Fix or drill deeper |
| 7 | Cleanup | Remove all markers |
