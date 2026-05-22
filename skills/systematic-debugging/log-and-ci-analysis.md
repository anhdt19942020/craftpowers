# Log & CI/CD Analysis

## When to Use

- CI/CD pipeline failures (GitHub Actions, GitLab CI, Jenkins)
- Server errors visible only in logs
- Deployment issues
- Flaky CI that passes locally but fails remotely

## GitHub Actions Analysis

### Collect logs via `gh` CLI

```bash
# List recent workflow runs
gh run list --limit 10

# View specific run
gh run view <run-id>

# Download logs
gh run view <run-id> --log

# View failed jobs only
gh run view <run-id> --log-failed

# Re-run failed jobs
gh run rerun <run-id> --failed
```

### Common failure patterns

| Pattern | Likely cause | Investigation |
|---------|-------------|---------------|
| "Resource not accessible" | Permission/token scope | Check `permissions:` in workflow YAML |
| Timeout on install | Registry outage or lockfile drift | Check npm/yarn status, compare lockfile |
| Test passes locally, fails CI | Env diff, parallelism, OS | Compare env vars, check matrix config |
| Intermittent failures | Race condition, external dep | Run 3x, correlate timestamps |
| "No space left on device" | Artifact/cache bloat | Check `actions/cache` size, prune artifacts |

## Server Log Analysis

### Structured approach

1. **Identify timeframe** — when did problem start? `git log --since="2h ago"`
2. **Collect logs** — filter by error level and timeframe
3. **Correlate** — match request IDs across services
4. **Timeline** — order events chronologically

### Log query patterns

```bash
# Errors in last hour
grep -E "ERROR|FATAL|CRITICAL" app.log | tail -50

# Filter by request ID
grep "req-abc123" app.log

# Count error types
grep ERROR app.log | awk '{print $4}' | sort | uniq -c | sort -rn

# Timestamp range
awk '$1 >= "2025-01-15T10:00" && $1 <= "2025-01-15T11:00"' app.log
```

### Docker/container logs

```bash
# Recent logs with timestamps
docker logs --since 1h --timestamps <container>

# Follow + filter
docker logs -f <container> 2>&1 | grep ERROR

# Multi-container correlation
docker compose logs --since 1h | sort -k1
```

## Cross-Source Correlation

When problem spans multiple systems:

1. Pick anchor event (user report timestamp, error ID)
2. Query each source within ±5 minutes of anchor
3. Build unified timeline
4. Gap in timeline = where problem lives

```
T+0s    User reports error
T-2s    API log: 500 on /api/checkout
T-2.1s  API log: DB query timeout after 30s
T-32s   DB log: lock wait timeout on orders table
T-35s   Cron log: bulk update on orders started
        ← ROOT CAUSE: cron job locks table during checkout
```

## CI-Specific Debugging

### Environment parity checklist

- [ ] Same Node/Python/Ruby version?
- [ ] Same OS (ubuntu vs macos vs windows)?
- [ ] Same env vars set?
- [ ] Same file permissions?
- [ ] Same timezone?
- [ ] Cache stale? Try `actions/cache` with new key
- [ ] Secrets accessible? Check `${{ secrets.X }}` vs empty string

### Reproduce CI locally

```bash
# GitHub Actions via act (if available)
act -j <job-name> --secret-file .env

# Manual reproduction
export CI=true
export GITHUB_ACTIONS=true
# Run same commands as workflow
```
