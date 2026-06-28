---
skill_id: b42f5b8b3997
usage_count: 1
last_used: 2026-06-16
---
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --reuse-db
    --nomigrations
    --cov=apps
    --cov-report=html
    --cov-report=term-missing
    --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### Test Settings

```python