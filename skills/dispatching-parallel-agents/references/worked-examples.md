## Worked Examples and Alternative Patterns

### Real Example from Session

Parallel research dispatch — 4 independent file searches:

```
Agent(description="Search auth patterns", prompt="Find all files in src/ that handle JWT validation. List file paths and the validation approach used. Work context: /path/to/project")
Agent(description="Search test patterns", prompt="Find all test files in tests/ that mock the database. List file paths and mock approaches. Work context: /path/to/project")
Agent(description="Search error patterns", prompt="Find all error handling patterns in src/. List where AppError is thrown and how it's caught. Work context: /path/to/project")
Agent(description="Search config patterns", prompt="Find all configuration loading in src/. List files and what env vars they read. Work context: /path/to/project")
```

All 4 dispatched in one message → parallel execution → results arrive independently.

### Parallel Implementation with Worktrees

```
# Spawn 3 independent implementers in separate worktrees

Agent(
  description="Implement user validation module",
  prompt="""
  Task: Add email validation to src/auth/validate.ts
  Files to modify: src/auth/validate.ts, tests/auth/validate.test.ts
  Acceptance: npx jest tests/auth/validate.test.ts → all pass
  Your worktree: /path/to/.worktrees/task-validate
  All file operations MUST happen in your worktree.
  """
)

Agent(
  description="Implement rate limiting middleware",
  prompt="""
  Task: Add rate limiting to src/middleware/rate-limit.ts
  Files to modify: src/middleware/rate-limit.ts, tests/middleware/rate-limit.test.ts
  Acceptance: npx jest tests/middleware/ → all pass
  Your worktree: /path/to/.worktrees/task-ratelimit
  All file operations MUST happen in your worktree.
  """
)

Agent(
  description="Implement audit logging",
  prompt="""
  Task: Add audit logging to src/audit/logger.ts
  Files to modify: src/audit/logger.ts, tests/audit/logger.test.ts
  Acceptance: npx jest tests/audit/ → all pass
  Your worktree: /path/to/.worktrees/task-audit
  All file operations MUST happen in your worktree.
  """
)
```

### CI / Long-Task Monitoring During Dispatch

```
# Trigger CI, then immediately dispatch agents while CI runs

# 1. Push branch to trigger CI
git push origin feature/auth-refactor

# 2. While CI runs, dispatch parallel agents for next wave of work
Agent(description="Write migration guide", prompt="...")
Agent(description="Update API docs", prompt="...")
Agent(description="Add changelog entry", prompt="...")

# 3. Monitor CI in background
Monitor("gh run watch --exit-status")

# 4. If CI fails, dispatch fix agent immediately
Agent(description="Fix CI failure", prompt="CI failed with: [error]. Fix and push.")
```

### Foreground vs Background Mode

```
# Foreground — use when you need results before proceeding
results = Agent(description="Audit security", prompt="...")
# Script blocks here until agent returns
# Then use results to decide next dispatch

# Background — use for fire-and-forget or independent work  
Agent(description="Generate docs", prompt="...", run_in_background=true)
Agent(description="Run full test suite", prompt="...", run_in_background=true)
# Script continues immediately; notifications arrive when agents complete
```

### Alternative: Sequential Dispatch (when tasks chain)

When tasks are NOT independent (Task B needs Task A's output):

```
# Do NOT dispatch in parallel
result_a = Agent(description="Extract API schema", prompt="Read src/api/routes.ts and output the complete OpenAPI schema.")

# Use result_a to inform Task B
Agent(
  description="Generate TypeScript client",
  prompt=f"""
  Generate a TypeScript API client from this OpenAPI schema:
  
  {result_a}
  
  Output to: src/client/api.ts
  """
)
```
