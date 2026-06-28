
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Django Celery_References_Route Failed Tasks To Dead Letter Queue After Max Retries |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Route failed tasks to dead-letter queue after max retries
@shared_task(
    bind=True,
    max_retries=3,
    name='payments.charge_card',
)
def charge_card(self, order_id: int) -> None:
    from apps.payments.models import Order, FailedCharge

    try:
        _do_charge(order_id)
    except Exception as exc:
        if self.request.retries >= self.max_retries: