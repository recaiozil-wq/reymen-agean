---
skill_id: 3ce2abacd0a6
usage_count: 1
last_used: 2026-06-16
---
## Project Structure

### Recommended Layout

```
myproject/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # Base settings
│   │   ├── development.py   # Dev settings
│   │   ├── production.py    # Production settings
│   │   └── test.py          # Test settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
└── apps/
    ├── __init__.py
    ├── users/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   ├── urls.py
    │   ├── permissions.py
    │   ├── filters.py
    │   ├── services.py
    │   └── tests/
    └── products/
        └── ...
```

### Split Settings Pattern

```python