---
name: patterns
description: WebSocket application patterns — rooms, namespaces, broadcasting, acknowledgments, presence
---

# WebSocket Application Patterns

## Rooms

Rooms are server-side groupings of connections. A socket can join multiple rooms.

```typescript
io.on('connection', (socket) => {
  // Join a room
  socket.on('join-room', (roomId) => {
    socket.join(roomId);
    socket.to(roomId).emit('user-joined', { userId: socket.data.user.id });
  });

  // Leave a room
  socket.on('leave-room', (roomId) => {
    socket.leave(roomId);
    socket.to(roomId).emit('user-left', { userId: socket.data.user.id });
  });

  // Send to room (excludes sender)
  socket.on('message', ({ roomId, text }) => {
    socket.to(roomId).emit('message', {
      userId: socket.data.user.id,
      text,
      ts: Date.now(),
    });
  });

  // Send to room (includes sender)
  socket.on('announcement', ({ roomId, text }) => {
    io.to(roomId).emit('announcement', { text, ts: Date.now() });
  });
});
```

### Room Best Practices

- Use descriptive room names: `project:123`, `chat:general`, `user:456`
- Clean up rooms on disconnect (Socket.IO does this automatically)
- Don't store state in rooms — they're just connection groupings
- For room metadata (name, settings), use an external store

## Namespaces

Namespaces provide separate communication channels on the same connection:

```typescript
// Main namespace
const mainNsp = io.of('/');

// Chat namespace with its own middleware
const chatNsp = io.of('/chat');
chatNsp.use(authMiddleware);

chatNsp.on('connection', (socket) => {
  socket.on('message', (msg) => {
    chatNsp.emit('message', msg); // Only reaches /chat clients
  });
});

// Admin namespace with stricter auth
const adminNsp = io.of('/admin');
adminNsp.use(adminAuthMiddleware);

adminNsp.on('connection', (socket) => {
  socket.on('broadcast', (msg) => {
    // Broadcast to all namespaces
    io.of('/chat').emit('system-message', msg);
  });
});
```

### When to Use Namespaces vs Rooms

| Feature | Namespaces | Rooms |
|---------|-----------|-------|
| Created by | Server code | Dynamically at runtime |
| Auth | Separate middleware per namespace | Shared auth, room-level checks in handlers |
| Use case | Separate features (chat, notifications, admin) | Dynamic groups (chat rooms, game lobbies) |
| Connection | Client chooses which to connect to | Server manages membership |

## Broadcasting

```typescript
// To all connected clients
io.emit('event', data);

// To all in a room (includes sender)
io.to('room1').emit('event', data);

// To all in a room (excludes sender)
socket.to('room1').emit('event', data);

// To multiple rooms
io.to('room1').to('room2').emit('event', data);

// To all except certain rooms
io.except('room1').emit('event', data);

// To a specific client
io.to(socketId).emit('event', data);
```

## Acknowledgments

Request-response pattern over WebSocket:

```typescript
// Server
socket.on('create-item', async (data, callback) => {
  try {
    const item = await createItem(data);
    callback({ status: 'ok', item });
  } catch (error) {
    callback({ status: 'error', message: error.message });
  }
});

// Client
socket.emit('create-item', { name: 'Test' }, (response) => {
  if (response.status === 'ok') {
    console.log('Created:', response.item);
  } else {
    console.error('Failed:', response.message);
  }
});
```

### With Timeout

```typescript
// Client with timeout
socket.timeout(5000).emit('create-item', { name: 'Test' }, (err, response) => {
  if (err) {
    // Timeout or server disconnected
    console.error('Request timed out');
  } else {
    console.log('Response:', response);
  }
});
```

## Presence Tracking

Track which users are online:

```typescript
const presence = new Map<string, { socketId: string; joinedAt: number }>();

io.on('connection', (socket) => {
  const userId = socket.data.user.id;

  // Mark online
  presence.set(userId, { socketId: socket.id, joinedAt: Date.now() });
  io.emit('presence:join', { userId });

  // Send current presence to new connection
  socket.emit('presence:list', Array.from(presence.keys()));

  socket.on('disconnect', () => {
    presence.delete(userId);
    io.emit('presence:leave', { userId });
  });
});
```

### Presence with Redis (multi-server)

```typescript
async function setPresence(userId: string, serverId: string): Promise<void> {
  await redis.hSet('presence', userId, JSON.stringify({
    serverId,
    timestamp: Date.now(),
  }));
}

async function removePresence(userId: string): Promise<void> {
  await redis.hDel('presence', userId);
}

async function getOnlineUsers(): Promise<string[]> {
  const all = await redis.hGetAll('presence');
  return Object.keys(all);
}

// Periodic cleanup of stale entries
setInterval(async () => {
  const all = await redis.hGetAll('presence');
  const now = Date.now();
  for (const [userId, data] of Object.entries(all)) {
    const { timestamp } = JSON.parse(data);
    if (now - timestamp > 60000) {
      await redis.hDel('presence', userId);
    }
  }
}, 30000);
```

## Message Queuing During Disconnection

Buffer messages when client is offline:

```typescript
// Server-side message queue
const messageQueue = new Map<string, Array<{ event: string; data: any }>>();

function queueMessage(userId: string, event: string, data: any): void {
  if (!messageQueue.has(userId)) {
    messageQueue.set(userId, []);
  }
  const queue = messageQueue.get(userId)!;
  queue.push({ event, data });

  // Limit queue size
  if (queue.length > 100) {
    queue.shift();
  }
}

function flushQueue(userId: string, socket: Socket): void {
  const queue = messageQueue.get(userId);
  if (queue) {
    for (const { event, data } of queue) {
      socket.emit(event, data);
    }
    messageQueue.delete(userId);
  }
}

io.on('connection', (socket) => {
  const userId = socket.data.user.id;
  flushQueue(userId, socket);

  // When sending to a user who might be offline
  socket.on('send-to-user', ({ targetUserId, message }) => {
    const targetSocket = findSocketByUserId(targetUserId);
    if (targetSocket) {
      targetSocket.emit('message', message);
    } else {
      queueMessage(targetUserId, 'message', message);
    }
  });
});
```

## Structured Message Protocol

Define a consistent message format:

```typescript
interface WSMessage {
  type: string;
  payload?: unknown;
  id?: string;       // For request/response correlation
  timestamp?: number;
}

// Server handler
socket.on('message', (raw: string) => {
  let msg: WSMessage;
  try {
    msg = JSON.parse(raw);
  } catch {
    socket.emit('error', { message: 'Invalid JSON' });
    return;
  }

  switch (msg.type) {
    case 'chat:send':
      handleChatSend(socket, msg);
      break;
    case 'typing:start':
      handleTypingStart(socket, msg);
      break;
    case 'typing:stop':
      handleTypingStop(socket, msg);
      break;
    default:
      socket.emit('error', { message: `Unknown type: ${msg.type}` });
  }
});
```

## Typing Indicators

```typescript
socket.on('typing:start', ({ roomId }) => {
  socket.to(roomId).emit('typing:start', {
    userId: socket.data.user.id,
  });
});

socket.on('typing:stop', ({ roomId }) => {
  socket.to(roomId).emit('typing:stop', {
    userId: socket.data.user.id,
  });
});

// Client: debounce typing events
let typingTimeout: NodeJS.Timeout;

function onInput() {
  socket.emit('typing:start', { roomId });
  clearTimeout(typingTimeout);
  typingTimeout = setTimeout(() => {
    socket.emit('typing:stop', { roomId });
  }, 2000);
}
```
