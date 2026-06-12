## Extended Debugging Techniques

### Multi-Component Diagnostic Instrumentation

**WHEN system has multiple components (CI → build → signing, API → service → database):**

**BEFORE proposing fixes, add diagnostic instrumentation at each boundary:**

```
For EACH component boundary:
  - Log what data enters component
  - Log what data exits component
  - Verify environment/config propagation
  - Check state at each layer

Run once to gather evidence showing WHERE it breaks
THEN analyze evidence to identify failing component
THEN investigate that specific component
```

**Example (multi-layer CI/signing system):**
```bash
# Layer 1: Workflow
echo "=== Secrets available in workflow: ==="
echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

# Layer 2: Build script
echo "=== Env vars in build script: ==="
env | grep IDENTITY || echo "IDENTITY not in environment"

# Layer 3: Signing script
echo "=== Keychain state: ==="
security list-keychains
security find-identity -v

# Layer 4: Actual signing
codesign --sign "$IDENTITY" --verbose=4 "$APP"
```

**This reveals:** Which layer fails (secrets → workflow ✓, workflow → build ✗)

### Root Cause Tracing

See `root-cause-tracing.md` in this directory for the complete backward tracing technique.

**Quick version:**
1. Where does the bad value originate?
2. What called this with bad value?
3. Keep tracing up until you find the source
4. Fix at source, not at symptom

### Common Rationalizations (and counters)

| Rationalization | Why it's wrong | Counter |
|-----------------|----------------|---------|
| "Quick fix for now, investigate later" | Later never comes; symptoms recur | Root cause first, then fix |
| "Just try changing X and see if it works" | Trial-and-error without understanding adds complexity | Reproduce first, then hypothesize |
| "I don't fully understand but this might work" | Unknown fix = unknown side effects | Only fix what you understand |
| "Pattern says X but I'll adapt it differently" | Pattern deviations introduce subtle bugs | Follow the pattern exactly first, deviate only with reason |
| "Here are the main problems: [lists fixes without investigation]" | Skips Phase 1-3 entirely | No fixes until root cause confirmed |
| "One more fix attempt" (already tried 2+) | Indicates wrong layer; time to question architecture | Return to Phase 1 |

### Architecture Challenge (Phase 4.5)

If 3+ fixes all failed in the same area:

```
STOP. Ask:
1. Is this the right layer to fix?
   - Symptom in UI? Root cause might be in API contract.
   - Symptom in test? Root cause might be in test setup.
   - Symptom in service? Root cause might be in data model.

2. Is the approach fundamentally wrong?
   - "What would have to be true for this approach to work?"
   - If those conditions don't hold, change the approach.

3. What would the simplest possible fix look like?
   - Sometimes 3 failed complex fixes = 1 obvious simple fix overlooked.
```

### Companion File Reference

This skill has detailed companion files for specific techniques:

| File | Technique |
|------|-----------|
| `root-cause-tracing.md` | Backward tracing through call stacks |
| `condition-based-waiting.md` | Async/timing issues in tests |
| `condition-based-waiting-example.ts` | TypeScript example for condition-based waiting |
| `defense-in-depth.md` | Layered validation and error handling |
| `find-polluter.sh` | Script to find test pollution source |
| `frontend-verification.md` | Browser/React debugging workflow |
| `log-and-ci-analysis.md` | Reading CI logs and build output |
| `performance-diagnostics.md` | Profiling and performance root cause |
| `test-academic.md` | Testing theory and principles |
| `test-pressure-1.md` | Pressure test scenarios (set 1) |
| `test-pressure-2.md` | Pressure test scenarios (set 2) |
| `test-pressure-3.md` | Pressure test scenarios (set 3) |

### Quick Reference Table

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare differences | Identify the delta |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or refined hypothesis |
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |

### When Process Reveals "No Root Cause"

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.

### your human partner's Signals You're Doing It Wrong

If your human partner says any of these, return to Phase 1:
- "You've tried that already"
- "That's a different problem"
- "You're going in circles"
- "Can you explain why that would fix it?"
- "What's the actual root cause?"
