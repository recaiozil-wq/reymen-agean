---
skill_id: 2652338d54dd
usage_count: 1
last_used: 2026-06-16
---
# Module scope - runs once per module
@pytest.fixture(scope="module")
def module_db():
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()