---
skill_id: 1f15b6283e0b
usage_count: 1
last_used: 2026-06-16
---
## Hooks Discipline

See [rules/react/hooks.md](../../rules/react/hooks.md) for the full ruleset. Highlights:

- Top-level only, never conditional
- Cleanup every subscription, interval, listener
- Functional updater (`setX(prev => prev + 1)`) when new state depends on old
- Default position: do not memoize — add `useMemo`/`useCallback` only when a profiler or a dependency chain proves it matters
- Extract a custom hook only when the same hook sequence appears in 2+ components