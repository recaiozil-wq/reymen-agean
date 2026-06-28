---
skill_id: 35a30d27959f
usage_count: 1
last_used: 2026-06-16
---
## Best Practices

### DO

- **Follow TDD**: Write tests before implementation (red-green-refactor)
- **Use Test2::V0**: Modern assertions, better diagnostics
- **Use subtests**: Group related assertions, isolate state
- **Mock external dependencies**: Network, database, file system
- **Use `prove -l`**: Always include lib/ in `@INC`
- **Name tests clearly**: `'user login with invalid password fails'`
- **Test edge cases**: Empty strings, undef, zero, boundary values
- **Aim for 80%+ coverage**: Focus on business logic paths
- **Keep tests fast**: Mock I/O, use in-memory databases

### DON'T

- **Don't test implementation**: Test behavior and output, not internals
- **Don't share state between subtests**: Each subtest should be independent
- **Don't skip `done_testing`**: Ensures all planned tests ran
- **Don't over-mock**: Mock boundaries only, not the code under test
- **Don't use `Test::More` for new projects**: Prefer Test2::V0
- **Don't ignore test failures**: All tests must pass before merge
- **Don't test CPAN modules**: Trust libraries to work correctly
- **Don't write brittle tests**: Avoid over-specific string matching