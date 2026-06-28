---
skill_id: f93b16bc44c6
usage_count: 1
last_used: 2026-06-16
---
# Teardown
    db.close()

def test_database_query(database):
    """Test database operations."""
    result = database.query("SELECT * FROM users")
    assert len(result) > 0
```

### Fixture Scopes

```python