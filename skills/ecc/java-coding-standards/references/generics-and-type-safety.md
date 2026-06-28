---
skill_id: 5bd7707ef156
usage_count: 1
last_used: 2026-06-16
---
## Generics and Type Safety

- Avoid raw types; declare generic parameters
- Prefer bounded generics for reusable utilities

```java
public <T extends Identifiable> Map<Long, T> indexById(Collection<T> items) { ... }
```