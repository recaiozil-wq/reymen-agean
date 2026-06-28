---
skill_id: c137515717e9
usage_count: 1
last_used: 2026-06-16
---
# Step 4: Add to cart
        response = client.post(reverse('cart:add'), {
            'product_id': product.id,
            'quantity': 1,
        })
        assert response.status_code == 302