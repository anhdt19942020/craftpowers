# Small Review Workflow

Inline scan for small-medium repos (≤20 main-lang files AND ≤30 total).

## Steps

1. Receive inputs: `$SCOPE`, `$FILES`, `$PRIMARY_LANG`, loaded rules
2. For each file in `$FILES`, read content
3. Apply each rule in sequence:
   - Load generic rule
   - If language override exists for `$PRIMARY_LANG`, use override instead
   - Trace data flow (L1–L4) for each potential pattern match
   - Only flag if data originates from L1 and reaches sink without proper mitigation
4. Collect all findings
5. Sort by severity: CRITICAL > HIGH > MEDIUM > LOW > INFO
6. Render final report per `references/output-format.md`

## Reasoning instruction

Do NOT flag patterns where input is L3/L4. Do NOT flag where there is an intervening sanitizer/parameterizer. Trace the full data path before reporting.
