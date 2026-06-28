---
skill_id: 9b7200c9386f
usage_count: 1
last_used: 2026-06-16
---
# config/__init__.py
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Django Settings

```python