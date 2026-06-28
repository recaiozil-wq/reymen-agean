---
skill_id: 3cfce6c1cdde
usage_count: 1
last_used: 2026-06-16
---
# Production: multiple workers with concurrency
celery -A config worker --loglevel=warning --concurrency=4 -Q default,high_priority
```