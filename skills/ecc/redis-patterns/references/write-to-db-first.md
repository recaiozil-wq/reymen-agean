---
skill_id: a2a1eb5e4b4f
usage_count: 1
last_used: 2026-06-16
---
# Write to DB first
    db.execute("UPDATE products SET ... WHERE id = %s", product_id)