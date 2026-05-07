# Python release-prep rules

Apply when `requirements.txt` or `pyproject.toml` exists at repo root.

## Checks

### 1. New `os.environ` / `os.getenv` reads without `.env.example` entry — BLOCK

Find new env reads in the diff:
```
git diff main..HEAD -- '*.py' | grep -E "os\.(environ|getenv)\([\"']([A-Z_]+)"
```
For each unique env key introduced, verify it exists in:
- `.env.example` / `.env.sample`, OR
- `settings.py` / `config.py` (declared as a setting), OR
- `pydantic_settings.BaseSettings` subclass field

If missing from all three → **BLOCK**: "New env read `<KEY>` at `<file>:<line>` undocumented."

### 2. Dependency change without lock-file update — BLOCK

If `requirements.txt`, `pyproject.toml`, or `setup.py` changed in dependency
declarations but the lock file (`requirements.lock`, `poetry.lock`, `uv.lock`)
did NOT change → **BLOCK**: "Dependency change without lock-file update."

### 3. Pydantic / dataclass schema breaking change — WARNING

For each Pydantic `BaseModel` subclass or `@dataclass` modified in the diff:
- Removed required field → **WARNING**: "Breaking schema removal."
- New required field with no default → **WARNING**: "Breaking schema — new required field."
- Type narrowed (e.g., `str | int` → `str`) → **WARNING**: "Breaking schema narrowing."

### 4. Tests pass — WARNING

If a `pytest` or `unittest` config is present, run the test suite. If it fails →
**WARNING** with failing output.

If no test config, skip.

## Skip if

- The repo has no `requirements.txt` or `pyproject.toml`.
