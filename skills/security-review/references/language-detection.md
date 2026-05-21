# Language Detection

## Filter non-code paths

Exclude: `node_modules/`, `vendor/`, `dist/`, `build/`, `.next/`, `.nuxt/`, `target/`, `.venv/`, `__pycache__/`, `.git/`, `*.min.js`, `*.bundle.js`, `*.lock`, `*.lock.json`, `package-lock.json`

## Extension mapping

| Language | Extensions |
|----------|-----------|
| typescript | .ts, .tsx, .js, .jsx, .mjs, .cjs |
| python | .py |
| go | .go |
| php | .php |
| ruby | .rb |
| java | .java |
| csharp | .cs |
| rust | .rs |

## Algorithm

1. Count files by extension (after filtering)
2. Primary language = highest count (minimum threshold ~5 files)
3. For mixed repos (e.g., Laravel + Vue): pick backend language (server-side risk dominates)
4. Multi-language: can run both rule sets and merge findings
