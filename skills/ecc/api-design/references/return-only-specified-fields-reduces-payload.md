---
skill_id: a1ddc3c14d17
usage_count: 1
last_used: 2026-06-16
---
# Return only specified fields (reduces payload)
GET /api/v1/users?fields=id,name,email
GET /api/v1/orders?fields=id,total,status&include=customer.name
```