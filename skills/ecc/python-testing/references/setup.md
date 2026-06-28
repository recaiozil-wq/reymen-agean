---
skill_id: a0f848942ce8
usage_count: 1
last_used: 2026-06-16
---
# Setup
    db = Database(":memory:")
    db.create_tables()
    db.insert_test_data()

    yield db  # Provide to test