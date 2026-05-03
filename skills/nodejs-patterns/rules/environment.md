---
name: environment
description: Environment configuration and secrets management for Node.js
---

# Environment Configuration in Node.js

## Use --env-file Flag

Node.js 20.6+ supports loading environment variables from files:

```bash
# Load from .env file
node --env-file=.env app.ts

# Load from multiple files (later files override earlier)
node --env-file=.env --env-file=.env.local app.ts
```

## process.loadEnvFile()

Load env files programmatically (Node.js 21.7+):

```typescript
process.loadEnvFile('.env');
process.loadEnvFile('.env.local');
```

## Environment Validation with env-schema

Use [env-schema](https://github.com/fastify/env-schema) to validate and type environment variables at startup:

```typescript
import envSchema from 'env-schema';
import { Type, Static } from '@sinclair/typebox';

const schema = Type.Object({
  PORT: Type.Number({ default: 3000 }),
  HOST: Type.String({ default: '0.0.0.0' }),
  DATABASE_URL: Type.String(),
  REDIS_URL: Type.String({ default: 'redis://localhost:6379' }),
  JWT_SECRET: Type.String({ minLength: 32 }),
  LOG_LEVEL: Type.Union([
    Type.Literal('fatal'),
    Type.Literal('error'),
    Type.Literal('warn'),
    Type.Literal('info'),
    Type.Literal('debug'),
    Type.Literal('trace'),
  ], { default: 'info' }),
});

type Config = Static<typeof schema>;

const config: Config = envSchema({
  schema,
  dotenv: true,
});

export default config;
```

### With Zod

```typescript
import { z } from 'zod';

const envSchema = z.object({
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
});

const config = envSchema.parse(process.env);
export type Config = z.infer<typeof envSchema>;
export default config;
```

## The NODE_ENV Anti-Pattern

Avoid using `NODE_ENV` to branch application behavior:

```typescript
// BAD - behavior changes based on NODE_ENV
if (process.env.NODE_ENV === 'production') {
  enableCaching();
  disableStackTraces();
}

// GOOD - explicit configuration
const config = {
  caching: process.env.ENABLE_CACHING === 'true',
  stackTraces: process.env.SHOW_STACK_TRACES === 'true',
};
```

Each behavior should have its own explicit configuration flag.

## Typed Configuration Object

Create a typed config module that validates at startup:

```typescript
// config.ts
import envSchema from 'env-schema';
import { Type, Static } from '@sinclair/typebox';

const schema = Type.Object({
  server: Type.Object({
    port: Type.Number({ default: 3000 }),
    host: Type.String({ default: '0.0.0.0' }),
  }),
  database: Type.Object({
    url: Type.String(),
    poolSize: Type.Number({ default: 20 }),
  }),
  redis: Type.Object({
    url: Type.String({ default: 'redis://localhost:6379' }),
  }),
});

type Config = Static<typeof schema>;

// Map flat env vars to nested config
const config: Config = envSchema({
  schema,
  data: {
    server: {
      port: Number(process.env.PORT),
      host: process.env.HOST,
    },
    database: {
      url: process.env.DATABASE_URL,
      poolSize: Number(process.env.DB_POOL_SIZE),
    },
    redis: {
      url: process.env.REDIS_URL,
    },
  },
});

export default config;
```

## .env File Structure

```bash
# .env.example - commit this, document all required vars
PORT=3000
HOST=0.0.0.0
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
REDIS_URL=redis://localhost:6379
JWT_SECRET=change-me-in-production-minimum-32-characters
LOG_LEVEL=info

# .env - never commit this
# .env.local - never commit this
# .env.test - commit this for test defaults
```

## Secrets Management

Never store secrets in environment files for production:

```typescript
// For production, use secret management services:
// - AWS Secrets Manager
// - Google Cloud Secret Manager
// - HashiCorp Vault
// - Azure Key Vault

// Load secrets at startup, not on every access
async function loadSecrets(): Promise<Record<string, string>> {
  if (process.env.NODE_ENV === 'production') {
    return await fetchFromSecretManager();
  }
  // In development, use env vars
  return process.env as Record<string, string>;
}
```

## Feature Flags

Use explicit feature flags instead of environment detection:

```typescript
const features = {
  newCheckout: process.env.FEATURE_NEW_CHECKOUT === 'true',
  betaApi: process.env.FEATURE_BETA_API === 'true',
  debugMode: process.env.FEATURE_DEBUG === 'true',
};

if (features.newCheckout) {
  app.register(newCheckoutRoutes);
}
```
