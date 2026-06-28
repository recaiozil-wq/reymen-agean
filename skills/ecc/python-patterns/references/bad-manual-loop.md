---
skill_id: 2633addc6bdb
usage_count: 1
last_used: 2026-06-16
---
# Bad: Manual loop
names = []
for user in users:
    if user.is_active:
        names.append(user.name)