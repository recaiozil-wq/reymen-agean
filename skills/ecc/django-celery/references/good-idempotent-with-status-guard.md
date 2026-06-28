---
skill_id: 80f7530a31ec
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Idempotent with status guard
@shared_task
def charge_and_fulfill(order_id):
    order = Order.objects.select_for_update().get(pk=order_id)
    if order.status != Order.Status.PENDING:
        return  # Already processed
    order.charge()
    order.fulfill()
```