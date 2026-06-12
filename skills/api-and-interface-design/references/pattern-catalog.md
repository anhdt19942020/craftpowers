## API Pattern Catalog

### REST Resource Design

```typescript
// Good: noun-based, plural, hierarchical where it makes sense
GET    /api/users
GET    /api/users/:id
POST   /api/users
PATCH  /api/users/:id
DELETE /api/users/:id

GET    /api/users/:id/posts      // nested resource
POST   /api/users/:id/posts

// Avoid: verb-based URLs
POST /api/getUser        // ❌
POST /api/createUser     // ❌
POST /api/deleteUser     // ❌
```

### Pagination

```typescript
// Cursor-based (preferred for large datasets, consistent ordering)
GET /api/posts?cursor=eyJpZCI6MTAwfQ&limit=20
// Response:
{
  "data": [...],
  "nextCursor": "eyJpZCI6MTIwfQ",
  "hasMore": true
}

// Offset-based (simpler, fine for small datasets)
GET /api/posts?page=2&pageSize=20
// Response:
{
  "data": [...],
  "total": 847,
  "page": 2,
  "pageSize": 20
}
```

### Filtering

```typescript
// Simple filters as query params
GET /api/posts?status=published&authorId=42

// Complex filters: use a filter object
GET /api/posts?filter[status]=published&filter[createdAt][gte]=2024-01-01

// Or POST body for complex queries (breaks REST purity but pragmatic)
POST /api/posts/search
{ "status": "published", "tags": ["typescript", "react"], "after": "2024-01-01" }
```

### Partial Updates (PATCH)

```typescript
// PATCH replaces only provided fields
PATCH /api/users/42
{ "email": "new@example.com" }
// Only email is updated; other fields unchanged

// vs PUT replaces entire resource
PUT /api/users/42
{ "name": "Alice", "email": "new@example.com", "role": "admin" }
// All fields must be included

// For arrays: use explicit operations, not replacement
PATCH /api/users/42/tags
{ "add": ["typescript"], "remove": ["javascript"] }
// Not: { "tags": [...full array...] } — race condition risk
```

### Consistent Error Semantics

```typescript
// Standard error envelope — same shape for every error
interface ApiError {
  error: {
    code: string;      // machine-readable: "VALIDATION_ERROR", "NOT_FOUND"
    message: string;   // human-readable: "Email is required"
    field?: string;    // for validation errors: which field
    details?: unknown; // extra context when needed
  }
}

// HTTP status codes — use consistently
200 OK             // success with body
201 Created        // POST succeeded, resource created
204 No Content     // DELETE succeeded, no body
400 Bad Request    // client input error (validation)
401 Unauthorized   // not authenticated
403 Forbidden      // authenticated but not allowed
404 Not Found      // resource doesn't exist
409 Conflict       // state conflict (duplicate, version mismatch)
422 Unprocessable  // valid syntax but semantic error
429 Too Many Reqs  // rate limited
500 Internal       // server error (never expose internals)
```

### TypeScript Interface Patterns

**Discriminated Unions for Variants:**

```typescript
// Good: exhaustive type-checking, clear variants
type ApiResponse<T> =
  | { status: 'success'; data: T }
  | { status: 'error'; error: ApiError }
  | { status: 'loading' };

function handleResponse<T>(response: ApiResponse<T>) {
  switch (response.status) {
    case 'success': return response.data;   // T — fully typed
    case 'error':   return response.error;  // ApiError — fully typed
    case 'loading': return null;
    // TypeScript errors if a case is missing
  }
}

// Avoid: optional fields that hide the variant
interface BadResponse<T> {
  data?: T;
  error?: ApiError;
  loading?: boolean;
}
// ^ All combinations are valid — including data + error simultaneously
```

**Input/Output Separation:**

```typescript
// Input type (from client): IDs for relations, no server-generated fields
interface CreatePostInput {
  title: string;
  content: string;
  authorId: UserId;  // reference by ID
  tags: string[];
}

// Output type (to client): includes server-generated fields
interface Post {
  id: PostId;
  title: string;
  content: string;
  author: User;      // expanded relation
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}
```

**Branded Types for IDs:**

```typescript
// Prevents passing wrong ID type to wrong parameter
declare const __brand: unique symbol;
type Brand<T, B> = T & { [__brand]: B };

type UserId  = Brand<string, 'UserId'>;
type PostId  = Brand<string, 'PostId'>;
type OrderId = Brand<string, 'OrderId'>;

// Now this is a compile error:
function getPost(id: PostId): Promise<Post> { ... }
const userId = "user-123" as UserId;
getPost(userId); // ❌ Type 'UserId' is not assignable to type 'PostId'
```

### Hyrum's Law in Practice

> "With a sufficient number of users of an API, it does not matter what you promise in the contract — all observable behaviors of your system will be depended on by somebody."

Practical implications:

```typescript
// Any behavior you expose becomes a contract — even bugs
// Example: accidentally returning users sorted by createdAt
// → clients start depending on that order
// → you can never change it without breaking someone

// Defensive design: be explicit about what is guaranteed
interface UserListResponse {
  users: User[];
  // Note: order is not guaranteed. Sort client-side if needed.
}

// Use explicit versioning for breaking changes
GET /api/v2/users  // v1 still works for existing clients

// Add deprecation warnings before removing
// Response header: Deprecation: true, Sunset: Sat, 01 Jan 2025 00:00:00 GMT
```
