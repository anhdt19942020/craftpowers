# Performance Diagnostics

## When to Use

- API response times degraded
- Database queries slow
- Memory/CPU spikes
- Page load times increased
- Resource exhaustion (connections, file handles, threads)

## Investigation Framework

### Step 1: Establish Baseline

Before diagnosing, know what "normal" looks like:

```
Metric          | Normal    | Current   | Delta
Response time   | 200ms p95 | 1200ms    | 6x slower
DB queries/req  | 3         | 47        | N+1 detected
Memory          | 512MB     | 2.1GB     | Leak candidate
CPU             | 15%       | 95%       | Compute-bound
```

### Step 2: Narrow the Layer

```
Client → CDN → Load Balancer → App Server → DB/Cache → External API
                                    ↑
                              Usually here
```

Add timing at each boundary:

```python
# Python example
import time

start = time.perf_counter()
result = db.query(sql)
db_time = time.perf_counter() - start

start = time.perf_counter()
transformed = process(result)
compute_time = time.perf_counter() - start

log.info(f"db={db_time:.3f}s compute={compute_time:.3f}s")
```

### Step 3: Diagnose by Type

## Database Performance

### N+1 Query Detection

```sql
-- PostgreSQL: find slow queries
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Check for sequential scans on large tables
SELECT relname, seq_scan, seq_tup_read, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > 100
ORDER BY seq_tup_read DESC;
```

### Query optimization

```sql
-- Always EXPLAIN ANALYZE, not just EXPLAIN
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;

-- Look for:
--   Seq Scan on large table → needs index
--   Nested Loop with high rows → JOIN optimization
--   Sort with high memory → needs index or LIMIT
--   Hash Join with large build → partition or filter earlier
```

### Connection pool issues

```sql
-- PostgreSQL: check connections
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;

-- Find long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```

## Memory Issues

### Leak detection patterns

1. **Growing over time** — true leak, object not GC'd
2. **Spike on specific request** — large allocation, check payload size
3. **Gradual growth + periodic drop** — cache without eviction policy

### Node.js memory

```javascript
// Snapshot heap usage
const used = process.memoryUsage();
console.log(`Heap: ${Math.round(used.heapUsed / 1024 / 1024)}MB`);

// Track growth over time
setInterval(() => {
  const { heapUsed } = process.memoryUsage();
  console.log(`Heap: ${Math.round(heapUsed / 1024 / 1024)}MB`);
}, 10000);
```

### Python memory

```python
import tracemalloc
tracemalloc.start()

# ... run code ...

snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:10]:
    print(stat)
```

## API Latency

### Waterfall analysis

```bash
# curl with timing breakdown
curl -w "\n  DNS:    %{time_namelookup}s\n  TCP:    %{time_connect}s\n  TLS:    %{time_appconnect}s\n  TTFB:   %{time_starttransfer}s\n  Total:  %{time_total}s\n" -o /dev/null -s https://api.example.com/endpoint
```

### Common bottlenecks

| Symptom | Likely cause | Fix direction |
|---------|-------------|---------------|
| High TTFB, low transfer | Server processing slow | Profile app code |
| Low TTFB, high transfer | Response too large | Pagination, compression |
| Inconsistent latency | GC pauses or cold cache | Warm cache, tune GC |
| Latency grows with load | Missing index or lock contention | Add index, reduce lock scope |
| Sudden spike | External dependency timeout | Circuit breaker, timeout config |

## Reporting Template

```
## Performance Issue: [title]

**Impact:** [what users experience]
**Baseline:** [normal metrics]
**Current:** [degraded metrics]

### Root Cause
[What specific component/query/code path causes slowness]

### Evidence
[EXPLAIN output, timing logs, profiler data]

### Fix
[What was changed]

### Verification
[Before/after metrics proving fix worked]
```
