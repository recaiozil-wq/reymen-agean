---
skill_id: 5d1013b06cae
usage_count: 1
last_used: 2026-06-16
---
## Performance Best Practices

### Memoization

```typescript
import { useMemo, useCallback } from 'react'

// PASS: GOOD: Memoize expensive computations
// Copy before sorting - Array.prototype.sort mutates in place
const sortedMarkets = useMemo(() => {
  return [...markets].sort((a, b) => b.volume - a.volume)
}, [markets])

// PASS: GOOD: Memoize callbacks
const handleSearch = useCallback((query: string) => {
  setSearchQuery(query)
}, [])
```

### Lazy Loading

```typescript
import { lazy, Suspense } from 'react'

// PASS: GOOD: Lazy load heavy components
const HeavyChart = lazy(() => import('./HeavyChart'))

export function Dashboard() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyChart />
    </Suspense>
  )
}
```

### Database Queries

```typescript
// PASS: GOOD: Select only needed columns
const { data } = await supabase
  .from('markets')
  .select('id, name, status')
  .limit(10)

// FAIL: BAD: Select everything
const { data } = await supabase
  .from('markets')
  .select('*')
```