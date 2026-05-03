---
name: scaling
description: Horizontal scaling WebSocket servers — Redis adapter, sticky sessions, load balancing
---

# Scaling WebSocket Servers

## The Challenge

WebSocket connections are stateful and long-lived. Unlike HTTP, you can't just add more servers behind a load balancer — a message sent to Server A won't reach clients connected to Server B.

## Solution: Redis Adapter (Socket.IO)

The Redis adapter uses Redis pub/sub to broadcast events across Socket.IO instances:

```typescript
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const io = new Server(httpServer);

const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();

await Promise.all([pubClient.connect(), subClient.connect()]);
io.adapter(createAdapter(pubClient, subClient));
```

### How It Works

1. Client A connects to Server 1, joins room "chat"
2. Client B connects to Server 2, joins room "chat"
3. Server 1 receives a message for room "chat"
4. Server 1 publishes to Redis
5. Server 2 receives from Redis, delivers to Client B

### Redis Adapter with Streams (higher reliability)

For cases where pub/sub message loss is unacceptable:

```typescript
import { createAdapter } from '@socket.io/redis-streams-adapter';
import { createClient } from 'redis';

const redisClient = createClient({ url: process.env.REDIS_URL });
await redisClient.connect();

io.adapter(createAdapter(redisClient));
```

Redis Streams provides at-least-once delivery (vs pub/sub's at-most-once).

## Sticky Sessions

WebSocket connections must always route to the same server instance. This requires sticky sessions at the load balancer.

### Why Sticky Sessions Are Required

Socket.IO's HTTP long-polling transport (used as fallback) makes multiple HTTP requests during the handshake. If these requests hit different servers, the connection fails.

Even with WebSocket-only transport, some load balancers need session affinity for the initial upgrade request.

### Nginx Configuration

```nginx
upstream websocket_servers {
    ip_hash;  # Sticky sessions based on client IP
    server server1:3000;
    server server2:3000;
    server server3:3000;
}

server {
    listen 80;

    location /socket.io/ {
        proxy_pass http://websocket_servers;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-lived connections
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

### Cookie-Based Sticky Sessions (more reliable)

```nginx
upstream websocket_servers {
    server server1:3000;
    server server2:3000;

    # Use cookie for session affinity
    sticky cookie srv_id expires=1h domain=.example.com path=/;
}
```

### AWS ALB

AWS Application Load Balancer supports WebSocket natively:

1. Enable stickiness on the target group
2. Use cookie-based stickiness (AWSALB cookie)
3. Set idle timeout to match your WebSocket timeout (default 60s, increase to 3600s)
4. Enable WebSocket support in the listener rules

### Kubernetes

Use a Kubernetes Ingress with session affinity:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/affinity-mode: "persistent"
    nginx.ingress.kubernetes.io/session-cookie-name: "ws-affinity"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
spec:
  rules:
    - host: ws.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: websocket-service
                port:
                  number: 3000
```

## Connection Limits

Plan connection limits per instance:

| Resource | Typical Limit | Notes |
|----------|--------------|-------|
| File descriptors | 65,535 | Each connection uses one fd |
| Memory | ~50KB per connection | Varies by message size/buffering |
| CPU | ~10K-50K connections | Depends on message throughput |

### Estimating Capacity

```
Connections per instance = min(
  file_descriptor_limit,
  available_memory / memory_per_connection,
  cpu_capacity / messages_per_second_per_connection
)
```

For a typical 4GB, 2-core server: ~20,000-40,000 idle connections.

## State Management

### Shared State in Redis

Store connection state in Redis for cross-instance access:

```typescript
// Track which server each user is connected to
await redis.hSet('user:connections', userId, serverId);

// Track room membership
await redis.sAdd(`room:${roomId}:members`, userId);

// Presence with TTL (auto-expire on disconnect)
await redis.set(`presence:${userId}`, 'online', { EX: 60 });
```

### Connection Count Monitoring

```typescript
// Emit connection metrics
setInterval(async () => {
  const localConnections = io.engine.clientsCount;
  await redis.hSet('server:connections', serverId, localConnections);

  // Total across all servers
  const all = await redis.hGetAll('server:connections');
  const total = Object.values(all).reduce((sum, n) => sum + parseInt(n), 0);
  metrics.gauge('websocket.connections.total', total);
  metrics.gauge('websocket.connections.local', localConnections);
}, 10000);
```

## Graceful Shutdown with Scaling

```typescript
import closeWithGrace from 'close-with-grace';

closeWithGrace({ delay: 10000 }, async ({ signal }) => {
  // Remove from load balancer pool
  await redis.hDel('server:connections', serverId);

  // Notify clients to reconnect (they'll hit another server)
  for (const [id, socket] of io.sockets.sockets) {
    socket.emit('server:shutdown', { reconnectIn: 1000 });
  }

  // Wait for clients to reconnect elsewhere
  await new Promise((r) => setTimeout(r, 3000));

  // Close remaining connections
  await io.close();
});
```
