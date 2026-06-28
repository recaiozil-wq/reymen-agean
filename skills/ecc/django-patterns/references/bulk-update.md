---
skill_id: 6f05bf9c0967
usage_count: 1
last_used: 2026-06-16
---
# Bulk update
products = Product.objects.all()[:100]
for product in products:
    product.is_active = True
Product.objects.bulk_update(products, ['is_active'])