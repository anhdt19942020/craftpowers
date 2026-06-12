## Component Patterns and Examples

### Composition over Configuration

```tsx
// Good: Composable
<Card>
  <CardHeader>
    <CardTitle>Tasks</CardTitle>
  </CardHeader>
  <CardBody>
    <TaskList tasks={tasks} />
  </CardBody>
</Card>

// Avoid: Over-configured
<Card
  title="Tasks"
  headerVariant="large"
  bodyPadding="md"
  content={<TaskList tasks={tasks} />}
/>
```

### Focused Components

```tsx
// Good: Does one thing
export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <li className="flex items-center gap-3 p-3">
      <Checkbox checked={task.done} onChange={() => onToggle(task.id)} />
      <span className={task.done ? 'line-through text-muted' : ''}>{task.title}</span>
      <Button variant="ghost" size="sm" onClick={() => onDelete(task.id)}>
        <TrashIcon />
      </Button>
    </li>
  );
}
```

### Container / Presentation Split

```tsx
// Container: handles data
export function TaskListContainer() {
  const { tasks, isLoading, error, refetch } = useTasks();

  if (isLoading) return <TaskListSkeleton />;
  if (error) return <ErrorState message="Failed to load tasks" retry={refetch} />;
  if (tasks.length === 0) return <EmptyState message="No tasks yet" />;

  return <TaskList tasks={tasks} />;
}

// Presentation: handles rendering
export function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <ul role="list" className="divide-y">
      {tasks.map(task => <TaskItem key={task.id} task={task} />)}
    </ul>
  );
}
```

### Loading States

```tsx
// Skeleton for list items
export function TaskListSkeleton() {
  return (
    <ul role="list" className="divide-y">
      {Array.from({ length: 3 }).map((_, i) => (
        <li key={i} className="flex items-center gap-3 p-3 animate-pulse">
          <div className="h-4 w-4 rounded bg-muted" />
          <div className="h-4 w-48 rounded bg-muted" />
        </li>
      ))}
    </ul>
  );
}
```

### Accessible Error States

```tsx
export function ErrorState({ message, retry }: { message: string; retry?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-center gap-3 p-6 text-center">
      <AlertCircleIcon className="h-8 w-8 text-destructive" aria-hidden="true" />
      <p className="text-sm text-muted-foreground">{message}</p>
      {retry && (
        <Button variant="outline" size="sm" onClick={retry}>
          Try again
        </Button>
      )}
    </div>
  );
}
```

### Accessible Form Inputs

```tsx
// Good: explicit label association
<div className="flex flex-col gap-1.5">
  <label htmlFor="email" className="text-sm font-medium">
    Email address
  </label>
  <input
    id="email"
    type="email"
    aria-required="true"
    aria-describedby={error ? "email-error" : undefined}
    className="..."
  />
  {error && (
    <p id="email-error" role="alert" className="text-sm text-destructive">
      {error}
    </p>
  )}
</div>
```

### Responsive Patterns

```tsx
// Mobile-first with breakpoint overrides
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
  {items.map(item => <ItemCard key={item.id} item={item} />)}
</div>

// Stack on mobile, side-by-side on desktop
<div className="flex flex-col gap-4 md:flex-row">
  <aside className="w-full md:w-64 shrink-0">...</aside>
  <main className="flex-1 min-w-0">...</main>
</div>
```

### Transitions

```tsx
// Subtle, purposeful transitions only
<button
  className="transition-colors duration-150 hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring"
>
  Click me
</button>

// Respect prefers-reduced-motion
<div className="motion-safe:transition-transform motion-safe:duration-200">
  ...
</div>
```

### Design System: Avoid AI Aesthetic

Common AI-generated UI mistakes to avoid:

```tsx
// ❌ AI aesthetic: gradient hero, glass morphism, excessive shadows
<div className="bg-gradient-to-br from-purple-500 to-pink-500 backdrop-blur-lg shadow-2xl">

// ✅ Product-quality: purposeful color, clear hierarchy
<div className="bg-card border rounded-lg shadow-sm">

// ❌ Decorative icons on every list item
<li><SparklesIcon /> <CheckIcon /> Task completed <StarIcon /></li>

// ✅ Functional icons only, with meaning
<li>
  <CheckIcon aria-label="Completed" className="text-green-600" />
  Task completed
</li>
```
