---
skill_id: 35a30d27959f
usage_count: 1
last_used: 2026-06-16
---
## Best Practices

**DO:**
- Write tests FIRST (TDD)
- Use `#[cfg(test)]` modules for unit tests
- Test behavior, not implementation
- Use descriptive test names that explain the scenario
- Prefer `assert_eq!` over `assert!` for better error messages
- Use `?` in tests that return `Result` for cleaner error output
- Keep tests independent — no shared mutable state

**DON'T:**
- Use `#[should_panic]` when you can test `Result::is_err()` instead
- Mock everything — prefer integration tests when feasible
- Ignore flaky tests — fix or quarantine them
- Use `sleep()` in tests — use channels, barriers, or `tokio::time::pause()`
- Skip error path testing