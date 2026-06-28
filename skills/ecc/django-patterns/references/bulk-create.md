---
skill_id: 25661917c31d
usage_count: 1
last_used: 2026-06-16
---
# Bulk create
Product.objects.bulk_create([
    Product(name=f'Product {i}', price=10.00)
    for i in range(1000)
])