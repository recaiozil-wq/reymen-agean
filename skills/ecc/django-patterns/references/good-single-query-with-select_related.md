---
skill_id: f737bd0a586c
usage_count: 1
last_used: 2026-06-16
---
# Good - Single query with select_related
products = Product.objects.select_related('category').all()
for product in products:
    print(product.category.name)