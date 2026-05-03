---
name: security
description: WebSocket security — authentication, authorization, rate limiting, input validation, CORS
---

# WebSocket Security

## Authentication

### JWT Authentication (Socket.IO)

```typescript
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) {
    return next(new Error('Authentication required'));
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    socket.data.user = decoded;
    next();
  } catch (err) {
    next(new Error('Invalid token'));
  }
});
```

### JWT Authentication (ws library)

```typescript
import { WebSocketServer } from 'ws';
import { createServer } from 'node:http';

const server = createServer();
const wss = new WebSocketServer({ noServer: true });

server.on('upgrade', (request, socket, head) => {
  // Extract token from query string or headers
  const url = new URL(request.url, `http://${request.headers.host}`);
  const token = url.searchParams.get('token');

  if (!token) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
    return;
  }

  try {
    const user = jwt.verify(token, process.env.JWT_SECRET);
    wss.handleUpgrade(request, socket, head, (ws) => {
      ws.user = user;
      wss.emit('connection', ws, request);
    });
  } catch {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
  }
});
```

### Token Refresh

```typescript
// Client sends refresh token when current token is about to expire
socket.on('auth:refresh', async ({ refreshToken }, callback) => {
  try {
    const newTokens = await refreshAccessToken(refreshToken);
    socket.data.user = jwt.verify(newTokens.accessToken, process.env.JWT_SECRET);
    callback({ status: 'ok', accessToken: newTokens.accessToken });
  } catch {
    callback({ status: 'error', message: 'Refresh failed' });
    socket.disconnect();
  }
});
```

## Authorization

Check permissions per event, not just at connection:

```typescript
function requireRole(...roles: string[]) {
  return (socket: Socket, next: (err?: Error) => void) => {
    if (!roles.includes(socket.data.user.role)) {
      return next(new Error('Insufficient permissions'));
    }
    next();
  };
}

// Per-namespace authorization
adminNsp.use(requireRole('admin'));

// Per-event authorization
socket.on('delete-message', async ({ messageId }) => {
  const message = await getMessage(messageId);
  if (message.userId !== socket.data.user.id && socket.data.user.role !== 'admin') {
    socket.emit('error', { message: 'Not authorized to delete this message' });
    return;
  }
  await deleteMessage(messageId);
});
```

### Room-Level Authorization

```typescript
socket.on('join-room', async (roomId) => {
  const hasAccess = await checkRoomAccess(socket.data.user.id, roomId);
  if (!hasAccess) {
    socket.emit('error', { message: 'Access denied to room' });
    return;
  }
  socket.join(roomId);
});
```

## Rate Limiting

### Per-Connection Rate Limiting

```typescript
function createRateLimiter(limit: number, windowMs: number) {
  const clients = new Map<string, { count: number; resetAt: number }>();

  return function checkLimit(socketId: string): boolean {
    const now = Date.now();
    let state = clients.get(socketId);

    if (!state || now > state.resetAt) {
      state = { count: 0, resetAt: now + windowMs };
      clients.set(socketId, state);
    }

    state.count++;
    return state.count <= limit;
  };
}

const messageLimit = createRateLimiter(100, 60000); // 100 messages per minute

socket.on('message', (data) => {
  if (!messageLimit(socket.id)) {
    socket.emit('error', { code: 'RATE_LIMIT', message: 'Too many messages' });
    return;
  }
  // Process message
});
```

### Per-User Rate Limiting (with Redis)

```typescript
async function checkRateLimit(userId: string, action: string, limit: number, windowSec: number): Promise<boolean> {
  const key = `ratelimit:${action}:${userId}`;
  const count = await redis.incr(key);

  if (count === 1) {
    await redis.expire(key, windowSec);
  }

  return count <= limit;
}

socket.on('message', async (data) => {
  const allowed = await checkRateLimit(socket.data.user.id, 'message', 100, 60);
  if (!allowed) {
    socket.emit('error', { code: 'RATE_LIMIT' });
    return;
  }
  // Process message
});
```

## Input Validation

Always validate incoming WebSocket messages:

```typescript
import { z } from 'zod';

const MessageSchema = z.object({
  roomId: z.string().uuid(),
  text: z.string().min(1).max(5000),
  type: z.enum(['text', 'image', 'file']).default('text'),
});

socket.on('message', (raw) => {
  const result = MessageSchema.safeParse(raw);
  if (!result.success) {
    socket.emit('error', {
      code: 'VALIDATION_ERROR',
      message: result.error.issues[0].message,
    });
    return;
  }

  const message = result.data;
  // Process validated message
});
```

## CORS Configuration

```typescript
const io = new Server(httpServer, {
  cors: {
    origin: ['https://app.example.com', 'https://admin.example.com'],
    methods: ['GET', 'POST'],
    credentials: true,
  },
});
```

## Max Payload Size

Limit message size to prevent memory abuse:

```typescript
// Socket.IO
const io = new Server(httpServer, {
  maxHttpBufferSize: 1e6, // 1MB
});

// ws library
const wss = new WebSocketServer({
  maxPayload: 1024 * 1024, // 1MB
});
```

## Connection Limits

Prevent too many connections from a single IP:

```typescript
const connectionCounts = new Map<string, number>();
const MAX_CONNECTIONS_PER_IP = 10;

io.use((socket, next) => {
  const ip = socket.handshake.address;
  const count = connectionCounts.get(ip) || 0;

  if (count >= MAX_CONNECTIONS_PER_IP) {
    return next(new Error('Too many connections'));
  }

  connectionCounts.set(ip, count + 1);
  socket.on('disconnect', () => {
    const current = connectionCounts.get(ip) || 1;
    if (current <= 1) {
      connectionCounts.delete(ip);
    } else {
      connectionCounts.set(ip, current - 1);
    }
  });

  next();
});
```

## Security Checklist

- Always use `wss://` (TLS) in production
- Authenticate on connection, not after
- Validate all incoming messages (schema validation)
- Rate limit messages per connection and per user
- Set `maxPayload` / `maxHttpBufferSize` to prevent memory abuse
- Limit connections per IP
- Use CORS to restrict origins
- Don't trust client-sent user IDs — use server-side auth data
- Sanitize messages before broadcasting (prevent XSS)
- Log security events (failed auth, rate limits, validation errors)
