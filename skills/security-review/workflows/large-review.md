# Large Review Workflow

Sub-agent delegation for large repos (>20 main-lang files OR >30 total).

## Steps

1. Compute chunks per `references/chunking-strategy.md` — group by top-level folder, target 3–7 chunks
2. For each chunk, spawn sub-agent (general-purpose) with:
   - File list for chunk
   - Rules to apply (generic + language overlay)
   - Output: findings in EN canonical with rule ID, file:line, severity, description, fix
3. Wait for all sub-agents
4. Aggregate findings from all chunks
5. Deduplicate (same rule ID + same file:line = one finding)
6. If any chunk failed → downgrade verdict one level (PASS→WARN, WARN→FAIL)
7. Sort by severity, render report per `references/output-format.md`

## Sub-agent prompt template

```
You are a security scanner sub-agent.
Scan the following files for security vulnerabilities.
Files: [list]
Rules to apply: [rule IDs with file paths]
Report findings as: rule ID, file:line, severity, confidence, data flow (L1-L4), description, fix.
Use data-flow-classification.md L1-L4 methodology — only flag L1 → sink without mitigation.
```
