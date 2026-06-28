---
skill_id: 56ea40cd0287
usage_count: 1
last_used: 2026-06-16
---
# Step 6: Complete purchase
        with patch('apps.checkout.services.process_payment') as mock_payment:
            mock_payment.return_value = True
            response = client.post(reverse('checkout:complete'))

        assert response.status_code == 302
        assert Order.objects.filter(user__email='test@example.com').exists()
```