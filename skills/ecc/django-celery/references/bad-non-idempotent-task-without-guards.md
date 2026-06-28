---
skill_id: 82148432fecc
usage_count: 1
last_used: 2026-06-16
---
# BAD: Non-idempotent task without guards
@shared_task
def charge_and_fulfill(order_id):
    order.charge()     # May charge twice if task retries!
    order.fulfill()