
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Django Tdd_References_Step 6 Complete Purchase |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Step 6: Complete purchase
        with patch('apps.checkout.services.process_payment') as mock_payment:
            mock_payment.return_value = True
            response = client.post(reverse('checkout:complete'))

        assert response.status_code == 302
        assert Order.objects.filter(user__email='test@example.com').exists()
```