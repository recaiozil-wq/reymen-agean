---
skill_id: 4015c097bd11
usage_count: 1
last_used: 2026-06-16
---
# Bad - N+1 queries
products = Product.objects.all()
for product in products:
    print(product.category.name)  # Separate query for each product