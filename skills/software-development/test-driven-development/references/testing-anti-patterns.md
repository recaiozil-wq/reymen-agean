---
skill_id: a3e4d81a7976
usage_count: 1
last_used: 2026-06-16
---
## Testing Anti-Patterns

- **Testing mock behavior instead of real behavior** — mocks should verify interactions, not replace the system under test
- **Testing implementation details** — test behavior/results, not internal method calls
- **Happy path only** — always test edge cases, errors, and boundaries
- **Brittle tests** — tests should verify behavior, not structure; refactoring shouldn't break them