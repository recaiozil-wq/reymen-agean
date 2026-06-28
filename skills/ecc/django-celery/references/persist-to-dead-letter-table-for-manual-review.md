---
skill_id: de8867f404ea
usage_count: 1
last_used: 2026-06-16
---
# Persist to dead-letter table for manual review
            FailedCharge.objects.create(
                order_id=order_id,
                error=str(exc),
                task_id=self.request.id,
            )
            return  # Don't raise — task is permanently failed
        raise self.retry(exc=exc)
```