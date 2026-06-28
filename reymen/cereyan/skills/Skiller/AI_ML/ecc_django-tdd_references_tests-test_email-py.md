
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Django Tdd_References_Tests Test_Email Py |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# tests/test_email.py
from django.core import mail
from django.test import override_settings

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_order_confirmation_email(db, order):
    """Test order confirmation email."""
    order.send_confirmation_email()

    assert len(mail.outbox) == 1
    assert order.user.email in mail.outbox[0].to
    assert 'Order Confirmation' in mail.outbox[0].subject
```