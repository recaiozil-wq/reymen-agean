---
skill_id: 422277e9e068
usage_count: 1
last_used: 2026-06-16
---
# Teardown happens automatically (CLEANUP => 1)
};
```

### Shared Test Helpers

Place reusable helpers in `t/lib/TestHelper.pm` and load with `use lib 't/lib'`. Export factory functions like `create_test_db()`, `create_temp_dir()`, and `fixture_path()` via `Exporter`.