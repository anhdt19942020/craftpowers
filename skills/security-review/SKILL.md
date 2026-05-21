---
name: security-review
description: "Security vulnerability scanner with 21+ rules, L1-L4 data flow analysis, framework-aware detection. Use when: code review, security audit, pre-merge check."
phase: REVIEW
---

# Security Review

Scan code for exploitable vulnerabilities using data-flow analysis (L1–L4 trust levels) and 21+ detection rules covering OWASP Top 10 and supply-chain attacks.

Adapted from [vbsec](https://github.com/tanviet12/vbsec) methodology.

## When to use

- Security-focused code review
- Pre-merge security audit
- User says "scan security", "security audit", "review security", "kiểm tra bảo mật"
- Implementation touches: auth, user input, file uploads, API integrations, data storage, shell commands

## Workflow

### Step 0 — Parse scope

Determine scan scope from user request:
- `uncommitted` — unstaged + staged changes
- `staged` — staged changes only
- `commit` — specific commit(s)
- `pr` — PR diff vs base branch
- `all` — entire codebase (default for "scan security")

### Step 1 — Gather files

```bash
# Scope: uncommitted
git diff --name-only && git diff --cached --name-only
# Scope: staged
git diff --cached --name-only
# Scope: commit
git diff <commit>^..<commit> --name-only
# Scope: pr
git diff main..HEAD --name-only
# Scope: all
git ls-files
```

Filter out non-code: `node_modules/`, `vendor/`, `dist/`, `build/`, `.next/`, `target/`, `.venv/`, `__pycache__/`, `*.min.js`, `*.bundle.js`, `*.lock`, `package-lock.json`

### Step 2 — Detect primary language

Count files by extension (see `references/language-detection.md`). Primary = highest count (min 5 files). For mixed repos, prefer backend language.

### Step 3 — Route by size

| Condition | Mode |
|-----------|------|
| ≤20 main-lang files AND ≤30 total | SMALL — scan inline |
| >20 main-lang OR >30 total | LARGE — delegate to sub-agents per `workflows/large-review.md` |

### Step 4 — Load rules

1. Load ALL generic rules from `rules/generic/`
2. If primary language has overrides in `rules/languages/<lang>/`, those **replace** the generic rule with matching `id`
3. Rule matching is by frontmatter `id`, not filename

### Step 5 — Apply data-flow analysis

For every potential pattern match, trace data flow using L1–L4 classification (see `references/data-flow-classification.md`):

- **Only flag** if data flows L1 → sink without proper sanitization
- **L2 → sink**: flag only if original L1 input was not validated before storage
- **L3/L4 → sink**: NOT a finding (false positive — suppress)

### Step 6 — Render report

Use output format from `references/output-format.md`. Severity order: CRITICAL > HIGH > MEDIUM > LOW > INFO.

## Reference Guide

| Topic | File |
|-------|------|
| Data flow trust levels | `references/data-flow-classification.md` |
| Language detection | `references/language-detection.md` |
| Output format | `references/output-format.md` |
| Small repo workflow | `workflows/small-review.md` |
| Large repo workflow | `workflows/large-review.md` |

### Rules — Generic (all languages)

| ID | Rule | Severity | File |
|----|------|----------|------|
| 01 | Hardcoded Secret | CRITICAL | `rules/generic/01-hardcoded-secret.md` |
| 02 | SQL Injection | CRITICAL | `rules/generic/02-sql-injection.md` |
| 03 | XSS | HIGH | `rules/generic/03-xss.md` |
| 04 | IDOR | HIGH | `rules/generic/04-idor.md` |
| 05 | Slopsquatting | CRITICAL | `rules/generic/05-slopsquatting.md` |
| 06 | Brute Force | HIGH | `rules/generic/06-brute-force.md` |
| 07 | Mass Assignment | CRITICAL | `rules/generic/07-mass-assignment.md` |
| 08 | Insecure Deserialization | CRITICAL | `rules/generic/08-insecure-deserialization.md` |
| 09 | SSRF | HIGH | `rules/generic/09-ssrf.md` |
| 10 | Path Traversal | HIGH | `rules/generic/10-path-traversal.md` |
| 11 | CSRF | HIGH | `rules/generic/11-csrf.md` |
| 15 | CORS Misconfiguration | HIGH | `rules/generic/15-cors-misconfig.md` |
| 16 | Unrestricted File Upload | CRITICAL | `rules/generic/16-unrestricted-file-upload.md` |
| 17 | Verbose Error / Debug Mode | HIGH | `rules/generic/17-verbose-error-debug-mode.md` |
| 18 | Missing Rate Limit | HIGH | `rules/generic/18-missing-rate-limit.md` |
| 19 | Race Condition | HIGH | `rules/generic/19-race-condition.md` |
| 21 | Command Injection | CRITICAL | `rules/generic/21-command-injection.md` |

### Rules — Language overrides

| Language | Override IDs |
|----------|-------------|
| Go | 02, 08, 09, 17, 21 |
| PHP | 02, 08, 11, 17, 21 |
| Python | 02, 07, 08, 09, 11, 21 |
| TypeScript | 02, 03, 07, 08, 09, 11, 14, 15, 17, 21 |

## Hard refusals

- Never edit source code. Report only.
- Never run exploit code or proof-of-concept attacks.
- If asked to fix: "Out of scope — security-review audits, it does not edit. Dispatch an implementer agent for fixes."

## Constraints

- Report only what you actually find — never fabricate issues
- Trace full data path before reporting — no pattern-matching without flow analysis
- L3/L4 sources are NOT findings — suppress false positives
- Hardcoded secrets (Rule 01) are an exception: flag even though literals are L4
