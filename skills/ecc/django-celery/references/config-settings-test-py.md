---
skill_id: 123173dac51a
usage_count: 1
last_used: 2026-06-16
---
# config/settings/test.py
CELERY_TASK_ALWAYS_EAGER = True      # Run tasks synchronously in tests
CELERY_TASK_EAGER_PROPAGATES = True  # Re-raise exceptions from tasks