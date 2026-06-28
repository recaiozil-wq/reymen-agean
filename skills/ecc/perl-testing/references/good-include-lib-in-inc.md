---
skill_id: 5948fb492c7d
usage_count: 1
last_used: 2026-06-16
---
# Good: Include lib/ in @INC
prove -l t/unit/user.t
```

### Over-Mocking

Mock the *dependency*, not the code under test. If your test only verifies that a mock returns what you told it to, it tests nothing.

### Test Pollution

Use `my` variables inside subtests — never `our` — to prevent state leaking between tests.

**Remember**: Tests are your safety net. Keep them fast, focused, and independent. Use Test2::V0 for new projects, prove for running, and Devel::Cover for accountability.