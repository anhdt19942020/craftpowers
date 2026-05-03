---
name: alternatives
description: When to use WebSockets vs SSE vs long polling vs HTTP
---

# WebSocket Alternatives

## Decision Matrix

| Feature | WebSocket | SSE | Long Polling | HTTP |
|---------|-----------|-----|-------------|------|
| Direction | Bidirectional | Server > Client | Server > Client | Request/Response |
| Protocol | ws:// / wss:// | HTTP | HTTP | HTTP |
| Reconnection | Manual | Automatic | Manual | N/A |
| Binary data | Yes | No (text only) | Yes | Yes |
| HTTP/2 multiplexing | No (HTTP/1.1 upgrade) | Yes | Yes | Yes |
| Browser support | All modern | All modern | All | All |
| Proxy friendly | Sometimes problematic | Yes | Yes | Yes |
| Connection overhead | 1 persistent connection | 1 persistent connection | Repeated connections | Per request |

## When to Use WebSockets

**Use WebSockets when you need:**
- Bidirectional real-time communication (chat, gaming, collaboration)
- Low latency (< 100ms) bidirectional messaging
- Binary data streaming
- High-frequency messages in both directions

**Common WebSocket use cases:**
- Chat applications
- Multiplayer games
- Collaborative editing
- Live trading/financial data
- Real-time dashboards with user interaction

## When to Use Server-Sent Events (SSE)

**Use SSE when:**
- Server pushes data to client (one-way)
- You want automatic reconnection (built into EventSource API)
- You need HTTP/2 multiplexing
- Your infrastructure has WebSocket issues (proxies, firewalls)
- Simple notification/event streams

```typescript
// Server (Fastify)
app.get('/events', async (request, reply) => {
  reply.raw.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  });

  const send = (event: string, data: unknown) => {
    reply.raw.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
  };

  send('connected', { timestamp: Date.now() });

  const interval = setInterval(() => {
    send('heartbeat', { timestamp: Date.now() });
  }, 30000);

  request.raw.on('close', () => {
    clearInterval(interval);
  });
});

// Client
const source = new EventSource('/events');

source.addEventListener('connected', (e) => {
  console.log('Connected:', JSON.parse(e.data));
});

source.addEventListener('heartbeat', (e) => {
  console.log('Heartbeat:', JSON.parse(e.data));
});

source.onerror = () => {
  // EventSource automatically reconnects
  console.log('Connection lost, reconnecting...');
};
```

**Common SSE use cases:**
- Live feeds (news, social media)
- Notifications
- Progress updates
- Log streaming
- Stock tickers (read-only)

## When to Use Long Polling

**Use long polling when:**
- WebSocket and SSE aren't available
- You need broad compatibility
- Message frequency is low

```typescript
// Server
app.get('/poll', async (request, reply) => {
  const lastEventId = request.query.lastEventId;

  // Wait for new events (up to 30 seconds)
  const events = await waitForEvents(lastEventId, 30000);

  return { events, lastEventId: events[events.length - 1]?.id };
});

// Client
async function poll(lastEventId?: string) {
  try {
    const response = await fetch(`/poll?lastEventId=${lastEventId || ''}`);
    const { events, lastEventId: newId } = await response.json();

    for (const event of events) {
      handleEvent(event);
    }

    // Immediately start next poll
    poll(newId);
  } catch {
    // Retry after delay
    setTimeout(() => poll(lastEventId), 5000);
  }
}
```

## When to Use Plain HTTP

**Use HTTP when:**
- Data changes infrequently
- Client-initiated requests only
- Caching is beneficial
- Simple request/response is sufficient

## Hybrid Approach

Many applications combine approaches:

```typescript
// WebSocket for real-time chat
const chatSocket = io('/chat');

// SSE for notifications
const notifications = new EventSource('/api/notifications');

// HTTP for CRUD operations
async function createMessage(roomId: string, text: string) {
  // Use HTTP for the write (reliable, retryable)
  await fetch(`/api/rooms/${roomId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
  // WebSocket delivers the message to other clients in real-time
}
```

## Migration Path

If starting simple and scaling:

1. **Start with HTTP polling** (simplest, works everywhere)
2. **Upgrade to SSE** when you need real-time server push
3. **Upgrade to WebSocket** when you need bidirectional real-time

Each step is a superset of the previous, so the migration is incremental.
