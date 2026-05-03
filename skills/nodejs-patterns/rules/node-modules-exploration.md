---
name: node-modules-exploration
description: Navigating and analyzing node_modules directories
---

# Navigating node_modules

## Find Package Location

```bash
# Find where a package is installed
node -e "console.log(require.resolve('fastify'))"

# Or with ESM
node -e "import('fastify').then(m => console.log(m))"

# List all installed versions of a package
npm ls express
pnpm ls express
```

## Package Structure

```
node_modules/
  .package-lock.json    # Lockfile metadata
  package-name/
    package.json        # Entry points, dependencies, metadata
    README.md           # Documentation
    dist/               # Compiled output (most packages)
    src/                # Source (some packages include it)
    lib/                # Alternative to dist
    index.js            # Main entry point
    index.d.ts          # TypeScript declarations
```

## Reading package.json

Key fields to check:

```bash
# View main entry point
node -e "console.log(require('package-name/package.json').main)"

# View exports map
node -e "console.log(JSON.stringify(require('package-name/package.json').exports, null, 2))"

# View all scripts
node -e "console.log(require('package-name/package.json').scripts)"
```

## pnpm Structure

pnpm uses a content-addressable store with symlinks:

```
node_modules/
  .pnpm/                          # Content-addressable store
    fastify@4.28.0/
      node_modules/
        fastify/                  # Actual package files
        @fastify/error/           # Dependencies hoisted here
  fastify -> .pnpm/fastify@4.28.0/node_modules/fastify  # Symlink
```

## Debugging Module Resolution

```bash
# Show module resolution steps
NODE_DEBUG=module node app.ts

# Check which file is actually loaded
node -e "console.log(require.resolve('package-name'))"
node -e "console.log(require.resolve('package-name/subpath'))"

# For ESM
node --input-type=module -e "import { createRequire } from 'module'; const r = createRequire(import.meta.url); console.log(r.resolve('package-name'))"
```

## Dependency Tree

```bash
# Full dependency tree
npm ls --all
pnpm ls --depth=Infinity

# Find why a package is installed
npm explain package-name
pnpm why package-name

# Find duplicate packages
npm dedupe --dry-run
```

## Analyzing Package Size

```bash
# Check install size
npx package-phobia package-name

# Check bundle size (for frontend packages)
npx bundlephobia package-name
```

## Investigating Conflicts

When multiple versions of a package are installed:

```bash
# Find all versions
npm ls package-name

# See which packages require which versions
npm explain package-name

# Attempt to deduplicate
npm dedupe
```
