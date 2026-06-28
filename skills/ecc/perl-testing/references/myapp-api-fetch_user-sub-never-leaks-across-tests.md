---
skill_id: 34e641faa516
usage_count: 1
last_used: 2026-06-16
---
# *MyApp::API::fetch_user = sub { ... };  # NEVER — leaks across tests
```

For lightweight mock objects, use `Test::MockObject` to create injectable test doubles with `->mock()` and verify calls with `->called_ok()`.