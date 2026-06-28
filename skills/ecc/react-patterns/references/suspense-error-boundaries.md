---
skill_id: 6682b697572a
usage_count: 1
last_used: 2026-06-16
---
## Suspense + Error Boundaries

```tsx
<ErrorBoundary fallback={<ErrorView />}>
  <Suspense fallback={<UserSkeleton />}>
    <UserDetail id={id} />
  </Suspense>
</ErrorBoundary>
```

- Place Suspense boundaries close to the data, not at the route root — progressively reveal content
- Error Boundary remains a class API; use `react-error-boundary` for a hook-friendly wrapper
- A boundary catches errors thrown during render, lifecycle, and constructors of its children — NOT in event handlers or async code