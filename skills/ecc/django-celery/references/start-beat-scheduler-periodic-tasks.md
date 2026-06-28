---
skill_id: 47cb61ddb14a
usage_count: 1
last_used: 2026-06-16
---
# Start beat scheduler (periodic tasks)
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler