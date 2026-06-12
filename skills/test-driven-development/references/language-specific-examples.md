## Language-Specific TDD Examples

### TypeScript / Jest

```typescript
// RED: write failing test first
describe('validateEmail', () => {
  it('returns true for valid email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });

  it('returns false for missing @', () => {
    expect(validateEmail('userexample.com')).toBe(false);
  });

  it('returns false for empty string', () => {
    expect(validateEmail('')).toBe(false);
  });
});

// Run: npx jest src/auth/validate.test.ts --forceExit
// Expected: FAIL — "validateEmail is not defined"

// GREEN: minimal implementation
export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Run again: PASS 3/3

// REFACTOR: extract constant, improve readability
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(email: string): boolean {
  if (!email) return false;
  return EMAIL_REGEX.test(email);
}
// Run again: still PASS 3/3
```

### TypeScript / React Testing Library

```typescript
// RED: component test first
import { render, screen, userEvent } from '@testing-library/react';
import { TaskItem } from './TaskItem';

describe('TaskItem', () => {
  it('calls onToggle with task id when checkbox clicked', async () => {
    const onToggle = jest.fn();
    const task = { id: '42', title: 'Write tests', done: false };

    render(<TaskItem task={task} onToggle={onToggle} onDelete={jest.fn()} />);

    await userEvent.click(screen.getByRole('checkbox'));
    expect(onToggle).toHaveBeenCalledWith('42');
  });

  it('shows strikethrough when task is done', () => {
    const task = { id: '42', title: 'Write tests', done: true };
    render(<TaskItem task={task} onToggle={jest.fn()} onDelete={jest.fn()} />);

    expect(screen.getByText('Write tests')).toHaveClass('line-through');
  });
});

// Run: npx jest src/components/TaskItem.test.tsx --forceExit
// Expected: FAIL — "Cannot find module './TaskItem'"

// GREEN: minimal component
export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <li>
      <input
        type="checkbox"
        checked={task.done}
        onChange={() => onToggle(task.id)}
      />
      <span className={task.done ? 'line-through' : ''}>{task.title}</span>
      <button onClick={() => onDelete(task.id)}>Delete</button>
    </li>
  );
}
```

### Python / pytest

```python
# RED: test first
def test_calculate_discount_standard_member():
    assert calculate_discount(price=100, member_tier="standard") == 90.0

def test_calculate_discount_premium_member():
    assert calculate_discount(price=100, member_tier="premium") == 80.0

def test_calculate_discount_no_member():
    assert calculate_discount(price=100, member_tier=None) == 100.0

def test_calculate_discount_invalid_tier():
    with pytest.raises(ValueError, match="Unknown tier"):
        calculate_discount(price=100, member_tier="vip")

# Run: pytest tests/pricing/test_discount.py -v
# Expected: FAIL — "name 'calculate_discount' is not defined"

# GREEN: minimal implementation
DISCOUNTS = {"standard": 0.10, "premium": 0.20}

def calculate_discount(price: float, member_tier: str | None) -> float:
    if member_tier is None:
        return price
    if member_tier not in DISCOUNTS:
        raise ValueError(f"Unknown tier: {member_tier}")
    return price * (1 - DISCOUNTS[member_tier])

# Run: pytest tests/pricing/test_discount.py -v → PASS 4/4
```

### Python / pytest with fixtures

```python
# RED: database test with fixture
@pytest.fixture
def db_session():
    """Isolated test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()

def test_create_user_stores_hashed_password(db_session):
    user = create_user(db_session, email="test@example.com", password="secret123")
    assert user.id is not None
    assert user.password_hash != "secret123"
    assert verify_password("secret123", user.password_hash)

# Run: pytest tests/users/test_create.py -v
# Expected: FAIL — "name 'create_user' is not defined"
```

### Bug Fix TDD Pattern

```typescript
// Bug: validateEmail accepts emails without TLD
// Step 1: Write test that reproduces the bug
it('returns false for email without TLD', () => {
  expect(validateEmail('user@example')).toBe(false);  // currently returns true — bug!
});

// Run: FAIL (confirms bug exists)

// Step 2: Fix implementation
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;  // requires dot after @domain

// Step 3: Run all tests — original 3 + new bug test
// Expected: PASS 4/4

// The new test is permanent — it documents the bug and prevents regression
```

### Integration Test Pattern (API endpoint)

```typescript
// RED: full request/response test
describe('POST /api/users', () => {
  it('creates user and returns 201 with id', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'new@example.com', name: 'Alice' });

    expect(response.status).toBe(201);
    expect(response.body).toMatchObject({
      id: expect.any(String),
      email: 'new@example.com',
      name: 'Alice',
    });
  });

  it('returns 400 for missing email', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Alice' });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.field).toBe('email');
  });
});
```
