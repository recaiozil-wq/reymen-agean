---
skill_id: f8eb1597c03e
usage_count: 1
last_used: 2026-06-16
---
# Bulk delete
Product.objects.filter(stock=0).delete()
```