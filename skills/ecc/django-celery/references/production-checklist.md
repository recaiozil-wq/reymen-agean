---
skill_id: 35b147cc9c8f
usage_count: 1
last_used: 2026-06-16
---
## Production Checklist

| Check | Setting |
|-------|---------|
| Worker restarts on crash | `supervisord` or `systemd` unit |
| `CELERY_TASK_ACKS_LATE = True` | Re-queue tasks on worker crash |
| `CELERY_WORKER_PREFETCH_MULTIPLIER = 1` | Fair distribution of long tasks |
| Separate queues per priority | `-Q default,high_priority,low_priority` |
| `CELERY_TASK_SOFT_TIME_LIMIT` set | Graceful timeout before hard kill |
| Sentry integration | Capture all `task_failure` signals |
| Flower or other monitor | Visibility into queue depths |
| Beat runs on single node only | Prevents duplicate scheduled task execution |