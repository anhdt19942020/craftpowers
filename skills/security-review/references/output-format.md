# Output Format

## Report structure

```
1. Header block (metadata)
2. Verdict line (PASS/WARN/FAIL)
3. CRITICAL findings — table + details
4. HIGH findings — table + details
5. MEDIUM findings — table + details
6. LOW findings — table + details
7. INFO findings — table only
8. Summary stats
```

## Header

```markdown
## Security Scan Report

| Scope | [scope value] |
| Files | N |
| Primary language | [lang] |
| Mode | SMALL (inline) / LARGE (sub-agent) |
| Scan date | YYYY-MM-DD |
```

## Verdict

```
VERDICT: PASS — No critical/high findings. N medium, N low, N info.
VERDICT: WARN — N high severity findings require attention.
VERDICT: FAIL — N critical findings detected. Immediate remediation required.
```

## Finding entry

```markdown
### [RULE-ID] Rule Name — `path/to/file.ext:line`

**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Confidence:** HIGH | MEDIUM | LOW
**Data flow:** L[1-4] → [sink description]

**Issue:**
[What it is, what attacker can do]

**Code:**
[relevant snippet, max 10 lines]

**Fix:**
[Specific fix with code example]

**References:** [CVE or OWASP link if applicable]
```

## Summary

```markdown
## Summary

| Metric | Count |
|--------|-------|
| Total findings | N |
| Critical | N |
| High | N |
| Medium | N |
| Low | N |
| Info | N |
| Files scanned | N |

Note: Findings filtered by L1-L4 data flow. False positives suppressed when data originates from trusted sources (L3/L4).
```
