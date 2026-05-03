---
name: flaky-tests
description: Identifying and diagnosing flaky tests with node:test
---

# Identifying and Diagnosing Flaky Tests

Flaky tests are tests that pass or fail intermittently without code changes. They erode trust in the test suite and waste debugging time.

## Identifying Which Test is Timing Out

### 1. Use --test-reporter for Detailed Output

```bash
# Show each test as it runs (tap format shows test file and name)
node --test --test-reporter=tap

# Use spec reporter for hierarchical view
node --test --test-reporter=spec
```

### 2. Run Tests with Timeout Tracking

```bash
# Set a global timeout and see which test exceeds it
node --test --test-timeout=5000

# The error message will include the test name and file
```

### 3. Run Individual Test Files

```bash
# Isolate by running files one at a time
for f in src/**/*.test.ts; do
  echo "Running: $f"
  timeout 30s node --test "$f" || echo "TIMEOUT or FAIL: $f"
done
```

### 4. Check for Hanging Async Operations

```bash
# Use --inspect to debug hanging tests
node --inspect --test src/hanging.test.ts
# Then connect Chrome DevTools to chrome://inspect
```

### 5. Use wtfnode to Find Open Handles

```typescript
import { describe, it, after } from 'node:test';
import wtfnode from 'wtfnode';

describe('Debug hanging tests', () => {
  after(() => {
    wtfnode.dump();
  });

  it('might hang', async () => {
    // Your test
  });
});
```

## Common Causes of Flaky Tests

### 1. Timing and Race Conditions

```typescript
// BAD - Race condition with setTimeout
it('should process after delay', async (t) => {
  let processed = false;
  processAsync(() => { processed = true; });

  await new Promise(resolve => setTimeout(resolve, 100));
  t.assert.equal(processed, true); // May fail if processing takes > 100ms
});

// GOOD - Wait for the actual condition
it('should process after delay', async (t) => {
  const result = await processAsync();
  t.assert.equal(result.processed, true);
});
```

### 2. Uncontrolled Time Dependencies

```typescript
// BAD - Depends on current time
it('should format today', (t) => {
  const result = formatDate(new Date());
  t.assert.equal(result, '2024-01-15'); // Fails tomorrow
});

// GOOD - Use fixed dates or mock time
it('should format date', (t) => {
  const fixedDate = new Date('2024-01-15T12:00:00Z');
  const result = formatDate(fixedDate);
  t.assert.equal(result, '2024-01-15');
});

// GOOD - Mock Date with node:test
it('should format today', (t) => {
  t.mock.timers.enable({ apis: ['Date'] });
  t.mock.timers.setTime(new Date('2024-01-15T12:00:00Z').getTime());

  const result = formatDate(new Date());
  t.assert.equal(result, '2024-01-15');
});
```

### 3. Port Conflicts

```typescript
// BAD - Hardcoded port
it('should start server', async (t) => {
  const server = await startServer({ port: 3000 }); // Conflicts with other tests
});

// GOOD - Use dynamic port (port 0)
it('should start server', async (t) => {
  const server = await startServer({ port: 0 });
  const address = server.address();
  const port = address.port; // OS assigns available port
});
```

### 4. Shared State Between Tests

```typescript
// BAD - Module-level state persists between tests
let cache = new Map();

it('test 1', (t) => {
  cache.set('key', 'value1');
  t.assert.equal(cache.get('key'), 'value1');
});

it('test 2', (t) => {
  t.assert.equal(cache.get('key'), undefined); // FAILS - still has 'value1'
});

// GOOD - Reset state in beforeEach
describe('cache tests', () => {
  let cache;
  beforeEach(() => { cache = new Map(); });

  it('test 1', (t) => {
    cache.set('key', 'value1');
    t.assert.equal(cache.get('key'), 'value1');
  });

  it('test 2', (t) => {
    t.assert.equal(cache.get('key'), undefined); // PASSES
  });
});
```

### 5. Test Order Dependencies

```typescript
// BAD - Test 2 depends on side effect from Test 1
it('test 1: create user', async (t) => {
  await db.insert({ id: 1, name: 'John' });
});

it('test 2: find user', async (t) => {
  const user = await db.findById(1); // Fails if test 1 didn't run first
  t.assert.equal(user.name, 'John');
});

// GOOD - Each test sets up its own data
it('test 2: find user', async (t) => {
  await db.insert({ id: 1, name: 'John' });
  const user = await db.findById(1);
  t.assert.equal(user.name, 'John');
});
```

### 6. Unhandled Promise Rejections

```typescript
// BAD - Fire-and-forget async operation
it('should send notification', async (t) => {
  sendNotification(user); // Not awaited - may reject after test ends
  t.assert.ok(true);
});

// GOOD - Await all async operations
it('should send notification', async (t) => {
  await sendNotification(user);
  t.assert.ok(true);
});
```

### 7. Resource Cleanup Failures

```typescript
// BAD - Resources not cleaned up
it('should read file', async (t) => {
  const handle = await fs.open('test.txt');
  const content = await handle.read();
  t.assert.ok(content);
  // handle never closed!
});

// GOOD - Always clean up resources
it('should read file', async (t) => {
  const handle = await fs.open('test.txt');
  t.after(() => handle.close());

  const content = await handle.read();
  t.assert.ok(content);
});
```

## Debugging Strategies

### Run Tests in Isolation

```bash
node --test src/user.test.ts
node --test --test-name-pattern="should create user" src/user.test.ts
```

### Increase Concurrency to Expose Race Conditions

```bash
node --test --test-concurrency=10
for i in {1..50}; do node --test src/flaky.test.ts || echo "Failed on run $i"; done
```

### Use Test Retry to Identify Flaky Tests

```typescript
it('potentially flaky test', { retry: 3 }, async (t) => {
  // If this needs retries to pass, it's flaky
});
```

## CI-Specific Flakiness

### Resource Constraints

```typescript
it('heavy computation', { timeout: 30000 }, async (t) => {
  const result = await heavyOperation();
  t.assert.ok(result);
});
```

### Network Reliability

```typescript
// Always mock external HTTP calls in unit tests
t.mock.method(globalThis, 'fetch', async (url) => {
  if (url.includes('api.external.com')) {
    return { ok: true, json: async () => mockData };
  }
  throw new Error(`Unmocked URL: ${url}`);
});
```

## Prevention Best Practices

1. **Use deterministic IDs** — `const id = 'test-user-${t.name}'` instead of `crypto.randomUUID()`
2. **Mock external services** — Avoid network flakiness
3. **Use explicit waits** — Wait for conditions, not arbitrary timeouts
4. **Ensure test isolation** — Use transactions that rollback in afterEach
