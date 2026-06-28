---
skill_id: c97320fd9f4a
usage_count: 1
last_used: 2026-06-16
---
## Testing Best Practices

### DO

- Use factories over manual `create()` calls
- One logical assertion per test
- Descriptive names: `test_guests_cannot_create_products`
- Test edge cases and authorization boundaries
- Mock external services with `Http::fake()`, `Mail::fake()`
- Use `RefreshDatabase` for clean state

### DON'T

- Don't test Laravel internals (trust the framework)
- Don't make tests dependent on each other
- Don't over-mock — mock only service boundaries
- Don't test private methods — test through the public interface
- Don't couple tests to HTML structure