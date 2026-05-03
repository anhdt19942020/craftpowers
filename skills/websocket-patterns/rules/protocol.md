---
name: protocol
description: WebSocket protocol fundamentals — handshake, frames, opcodes, close codes, ping/pong
---

# WebSocket Protocol

## The Handshake

WebSocket connections begin with an HTTP/1.1 Upgrade request:

```
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

Server responds with:

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

After the handshake, the connection switches to the WebSocket protocol — a persistent, full-duplex TCP connection.

## Frame Structure

WebSocket data is sent in frames. Each frame has:

| Field | Size | Description |
|-------|------|-------------|
| FIN | 1 bit | 1 = final fragment |
| RSV1-3 | 3 bits | Reserved for extensions |
| Opcode | 4 bits | Frame type |
| MASK | 1 bit | 1 = payload is masked |
| Payload length | 7/16/64 bits | Length of payload |
| Masking key | 0/32 bits | XOR mask (client->server only) |
| Payload | variable | The actual data |

## Opcodes

| Opcode | Type | Description |
|--------|------|-------------|
| 0x0 | Continuation | Fragment continuation |
| 0x1 | Text | UTF-8 text data |
| 0x2 | Binary | Binary data |
| 0x8 | Close | Connection close |
| 0x9 | Ping | Heartbeat request |
| 0xA | Pong | Heartbeat response |

## Close Codes

| Code | Name | Meaning |
|------|------|---------|
| 1000 | Normal Closure | Clean close |
| 1001 | Going Away | Server shutting down or client navigating away |
| 1002 | Protocol Error | Protocol violation |
| 1003 | Unsupported Data | Received data type not supported |
| 1006 | Abnormal Closure | No close frame received (connection dropped) |
| 1008 | Policy Violation | Message violates server policy |
| 1009 | Too Large | Message too big |
| 1011 | Internal Error | Server encountered an error |
| 1012 | Service Restart | Server is restarting |
| 1013 | Try Again Later | Temporary server condition |
| 1014 | Bad Gateway | Server acting as gateway received invalid response |
| 4000-4999 | Private Use | Application-specific codes |

## Ping/Pong

WebSocket has built-in heartbeat via ping/pong frames:

```typescript
// Server sends ping
ws.ping();

// Client automatically responds with pong (browser handles this)
// Node.js ws library also auto-responds

// Listen for pong to detect alive connections
ws.on('pong', () => {
  isAlive = true;
});
```

### Heartbeat Pattern

```typescript
const HEARTBEAT_INTERVAL = 30000;

const interval = setInterval(() => {
  for (const ws of wss.clients) {
    if (!ws.isAlive) {
      ws.terminate();
      continue;
    }
    ws.isAlive = false;
    ws.ping();
  }
}, HEARTBEAT_INTERVAL);

wss.on('connection', (ws) => {
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });
});

wss.on('close', () => {
  clearInterval(interval);
});
```

## Binary Data

WebSocket supports both text and binary frames:

```typescript
// Sending text
ws.send(JSON.stringify({ type: 'message', text: 'hello' }));

// Sending binary
const buffer = Buffer.from([0x01, 0x02, 0x03]);
ws.send(buffer);

// Receiving — check type
ws.on('message', (data, isBinary) => {
  if (isBinary) {
    // Handle binary data
    const buffer = Buffer.from(data);
  } else {
    // Handle text
    const text = data.toString();
  }
});
```

## Compression (Per-Message Deflate)

WebSocket supports per-message compression via the `permessage-deflate` extension:

```typescript
import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({
  port: 8080,
  perMessageDeflate: {
    zlibDeflateOptions: {
      chunkSize: 1024,
      memLevel: 7,
      level: 3,
    },
    zlibInflateOptions: {
      chunkSize: 10 * 1024,
    },
    threshold: 1024, // Only compress messages > 1KB
  },
});
```

Compression trades CPU for bandwidth. Enable it when:
- Messages are large (> 1KB)
- Bandwidth is constrained
- CPU is not the bottleneck

## Message Fragmentation

Large messages can be split across multiple frames:

```typescript
// The ws library handles fragmentation automatically
// Configure max payload size to prevent memory issues
const wss = new WebSocketServer({
  maxPayload: 1024 * 1024, // 1MB max message size
});
```

## URL Schemes

| Scheme | Default Port | Description |
|--------|-------------|-------------|
| `ws://` | 80 | Unencrypted WebSocket |
| `wss://` | 443 | TLS-encrypted WebSocket (always use in production) |
