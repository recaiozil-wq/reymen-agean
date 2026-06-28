
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Django Celery_References_Good Idempotent With Status Guard |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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