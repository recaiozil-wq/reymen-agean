---
skill_id: 3c48c98130ae
usage_count: 1
last_used: 2026-06-16
---
# Run tests marked as unit but not slow
pytest -m "unit and not slow"
```

### Configure Markers in pytest.ini

```ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    django: marks tests as requiring Django
```