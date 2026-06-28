---
skill_id: 44b043c39d52
usage_count: 1
last_used: 2026-06-16
---
# Step 5: Checkout
        response = client.get(reverse('checkout:review'))
        assert response.status_code == 200
        assert product.name in response.content.decode()