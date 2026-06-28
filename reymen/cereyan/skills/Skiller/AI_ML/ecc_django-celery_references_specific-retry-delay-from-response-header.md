
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Django Celery_References_Specific Retry Delay From Response Header |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Specific retry delay from response header
        raise self.retry(exc=exc, countdown=int(exc.retry_after))
```

### Idempotent Task Pattern

Design tasks so they can safely run multiple times with the same inputs:

```python
@shared_task(name='orders.mark_shipped')
def mark_order_shipped(order_id: int, tracking_number: str) -> None:
    """Mark order as shipped — safe to run multiple times."""
    from apps.orders.models import Order

    updated = Order.objects.filter(
        pk=order_id,
        status=Order.Status.PROCESSING,    # Guard: only update if not already shipped
    ).update(
        status=Order.Status.SHIPPED,
        tracking_number=tracking_number,
    )

    if not updated:
        logger.info('mark_order_shipped: order %s already shipped or not found', order_id)
```

### Task with Soft Time Limit

```python
from celery.exceptions import SoftTimeLimitExceeded

@shared_task(
    bind=True,
    name='reports.generate_pdf',
    soft_time_limit=120,
    time_limit=150,
)
def generate_pdf_report(self, report_id: int) -> str:
    """Generate PDF report with graceful timeout handling."""
    from apps.reports.services import PDFGenerator

    try:
        path = PDFGenerator.build(report_id)
        return path
    except SoftTimeLimitExceeded: