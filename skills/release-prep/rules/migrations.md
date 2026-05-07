# Database migration release-prep rules

Apply when any of these directories exist:
`prisma/`, `drizzle/`, `migrations/`, `alembic/`, `db/migrate/`.

## Checks

### 1. New migration without down/reversible — WARNING

For each migration file added in the diff:
- **Prisma**: warn if SQL contains `DROP COLUMN`, `DROP TABLE`, `ALTER COLUMN ... NOT NULL` (Prisma migrations are forward-only).
- **Drizzle / raw SQL**: warn if no corresponding `down.sql` or reversible block.
- **Alembic**: warn if `def downgrade()` body is empty or `pass`.
- **Django**: warn if `RunPython` has no `reverse_code`.

If destructive without reverse → **WARNING**: "Irreversible migration `<file>` — confirm rollback plan."

### 2. Destructive change — WARNING

In every new migration, scan SQL for these keywords:
- `DROP TABLE`
- `DROP COLUMN`
- `ALTER COLUMN ... NOT NULL` (without default)
- `RENAME COLUMN` / `RENAME TO`

For each → **WARNING**: "Destructive: `<keyword>` in `<file>:<line>` — confirm no client reads the dropped/renamed entity."

### 3. Migration order conflict — BLOCK

Compare the highest migration timestamp / sequence in this branch vs `origin/main`:
- If `origin/main` has a migration with a higher number than this branch's last,
  but this branch added new migrations, the merge will produce an out-of-order
  history → **BLOCK**: "Rebase on main before merging — migration `<branch-mig>` precedes `<main-mig>`."

### 4. Schema change without ORM model update — BLOCK

For raw SQL migrations (Alembic, Drizzle SQL, Django RunSQL):
- If the migration adds/removes columns that don't appear in the corresponding
  ORM model file → **BLOCK**: "Schema-model drift — migration changes `<column>` but `<model_file>` does not."

## Skip if

- No migration directory exists.
