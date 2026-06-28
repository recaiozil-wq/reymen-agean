---
skill_id: 35a30d27959f
usage_count: 1
last_used: 2026-06-16
---
## Best Practices

### DO

- Keep tests deterministic and isolated
- Prefer dependency injection over globals
- Use `ASSERT_*` for preconditions, `EXPECT_*` for multiple checks
- Separate unit vs integration tests in CTest labels or directories
- Run sanitizers in CI for memory and race detection

### DON'T

- Don't depend on real time or network in unit tests
- Don't use sleeps as synchronization when a condition variable can be used
- Don't over-mock simple value objects
- Don't use brittle string matching for non-critical logs

### Common Pitfalls

- **Using fixed temp paths** → Generate unique temp directories per test and clean them.
- **Relying on wall clock time** → Inject a clock or use fake time sources.
- **Flaky concurrency tests** → Use condition variables/latches and bounded waits.
- **Hidden global state** → Reset global state in fixtures or remove globals.
- **Over-mocking** → Prefer fakes for stateful behavior and only mock interactions.
- **Missing sanitizer runs** → Add ASan/UBSan/TSan builds in CI.
- **Coverage on debug-only builds** → Ensure coverage targets use consistent flags.