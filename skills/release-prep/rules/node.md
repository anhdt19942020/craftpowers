# Node / TypeScript release-prep rules

Apply when `package.json` exists at repo root.

## Checks

### 1. New `process.env.X` reads without `.env.example` entry — BLOCK

Find new env reads in the diff:
```
git diff main..HEAD -- '*.ts' '*.js' '*.tsx' '*.jsx' | grep -E "process\.env\.[A-Z_]+"
```
For each unique `process.env.<KEY>` introduced by the diff, verify `<KEY>` exists
in `.env.example` (or the project's documented equivalent: `.env.sample`,
`env.template`).

If missing → **BLOCK**: "New env read `<KEY>` at `<file>:<line>`, missing from `.env.example`."

### 2. Dependency change without lock-file update — BLOCK

If `package.json` changed in `dependencies` / `devDependencies` / `peerDependencies`
but `package-lock.json` (or `pnpm-lock.yaml` / `yarn.lock`, whichever is present)
did NOT change → **BLOCK**: "Dependency change without lock-file update."

### 3. Build script does not pass — WARNING

If a `build` script is defined in `package.json`, run it. If it fails →
**WARNING**: "Build failed — fix before deploy" with the failing command output.

If no `build` script defined, skip silently.

### 4. Breaking TypeScript export — WARNING

For each removed or changed exported symbol (type, interface, function signature)
in files matching `**/index.ts` / `**/*.d.ts` / `**/types.ts`, check whether other
files in the repo import that symbol.

If consumers exist → **WARNING**: "Breaking export change at `<file>` — `<n>` consumer(s) need updates."

## Skip if

- This is a leaf application with no published types.
- The repo has no `package.json` (this rule should not have been loaded).
