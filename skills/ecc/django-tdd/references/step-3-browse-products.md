---
skill_id: a2d7dbdb3cf8
usage_count: 1
last_used: 2026-06-16
---
# Step 3: Browse products
        product = ProductFactory(price=100)
        response = client.get(reverse('products:detail', kwargs={'slug': product.slug}))
        assert response.status_code == 200