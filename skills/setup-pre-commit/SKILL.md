---
name: setup-pre-commit
description: Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hooks, set up Husky, configure lint-staged, or add commit-time formatting/typechecking/testing.
phase: MAINTAIN
---

# Setup Pre-Commit Hooks

## What This Sets Up
- Husky pre-commit hook
- lint-staged running Prettier on all staged files
- Prettier config (if missing)
- typecheck and test scripts in the pre-commit hook

## Steps
1. Detect package manager (npm/pnpm/yarn/bun)
2. Install husky lint-staged prettier as devDependencies
3. Run `npx husky init`
4. Create `.husky/pre-commit` with: npx lint-staged, npm run typecheck, npm run test (adapted to package manager; omit typecheck/test if scripts don't exist)
5. Create `.lintstagedrc`: `{ "*": "prettier --ignore-unknown --write" }`
6. Create `.prettierrc` if missing (with standard defaults)
7. Verify: .husky/pre-commit exists and is executable, .lintstagedrc exists, prepare script in package.json is "husky", run `npx lint-staged`
8. Commit all changed/created files with message: `Add pre-commit hooks (husky + lint-staged + prettier)`
