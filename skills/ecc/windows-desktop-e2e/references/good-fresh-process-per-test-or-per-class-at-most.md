---
skill_id: 8026cbbc486b
usage_count: 1
last_used: 2026-06-16
---
# GOOD: fresh process per test (or per class at most)
@pytest.fixture(scope="function")
def app(): ...
```