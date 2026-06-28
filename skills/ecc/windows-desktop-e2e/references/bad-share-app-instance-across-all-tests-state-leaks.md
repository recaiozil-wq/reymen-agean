---
skill_id: c50813be67f8
usage_count: 1
last_used: 2026-06-16
---
# BAD: share app instance across all tests (state leaks)
@pytest.fixture(scope="session")
def app(): ...