---
skill_id: bb0a88fb3083
usage_count: 1
last_used: 2026-06-16
---
## Common Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Testing implementation details | Test behavior and outcomes |
| Shared mutable test state | Fresh instance per test (xUnit does this via constructors) |
| `Thread.Sleep` in async tests | Use `Task.Delay` with timeout, or polling helpers |
| Asserting on `ToString()` output | Assert on typed properties |
| One giant assertion per test | One logical assertion per test |
| Test names describing implementation | Name by behavior: `Method_ExpectedResult_WhenCondition` |
| Ignoring `CancellationToken` | Always pass and verify cancellation |