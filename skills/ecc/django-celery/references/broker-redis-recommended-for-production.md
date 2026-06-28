---
skill_id: 2191e4131f9d
usage_count: 1
last_used: 2026-06-16
---
# Broker (Redis recommended for production)
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='django-db')