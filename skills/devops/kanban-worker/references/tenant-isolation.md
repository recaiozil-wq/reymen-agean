---
skill_id: 9b0f9ba3837b
usage_count: 1
last_used: 2026-06-16
---
## Tenant isolation

If `$HERMES_TENANT` is set, the task belongs to a tenant namespace. When reading or writing persistent memory, prefix memory entries with the tenant so context doesn't leak across tenants:

- Good: `business-a: Acme is our biggest customer`
- Bad (leaks): `Acme is our biggest customer`