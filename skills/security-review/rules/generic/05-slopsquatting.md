---
id: SLOPSQUATTING
severity_max: CRITICAL
applies_to: all
---

# Slopsquatting (AI Hallucinated Packages)

## Intent

AI generates code importing packages that don't exist on npm/PyPI/Packagist. Attacker registers that name with malware: post-install steals credentials, env vars, crypto wallets, installs backdoor.

Specific to AI-generated code (vibe coding).

## Search patterns

1. Extract all `import`/`require`/`from ... import` statements
2. For each package, verify existence:
   - npm: `https://registry.npmjs.org/<package>`
   - PyPI: `https://pypi.org/pypi/<package>/json`
3. Flag packages returning 404 or with <100 downloads and <10 stars
4. Watch for: AI-sounding names, overly specific utility names, combinations of two existing package names

## Fix

Before `npm install` / `pip install`, verify package exists with legitimate history. Use `npm audit` and `pip-audit`. Pin exact versions + verify hash.

## Related rules

`01-hardcoded-secret` (malware scans secrets in code)
