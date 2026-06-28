---
skill_id: 8f4b2b448ff6
usage_count: 1
last_used: 2026-06-16
---
# Combined worker + beat (dev only, never production)
celery -A config worker --beat --loglevel=info