---
skill_id: 1dc3f3e3cd55
usage_count: 1
last_used: 2026-06-16
---
# Continuous testing
./gradlew test --continuous
```

### Best Practices

**DO:**
- Write tests FIRST (TDD)
- Use Kotest's spec styles consistently across the project
- Use MockK's `coEvery`/`coVerify` for suspend functions
- Use `runTest` for coroutine testing
- Test behavior, not implementation
- Use property-based testing for pure functions
- Use `data class` test fixtures for clarity

**DON'T:**
- Mix testing frameworks (pick Kotest and stick with it)
- Mock data classes (use real instances)
- Use `Thread.sleep()` in coroutine tests (use `advanceTimeBy`)
- Skip the RED phase in TDD
- Test private functions directly
- Ignore flaky tests

### Integration with CI/CD

```yaml