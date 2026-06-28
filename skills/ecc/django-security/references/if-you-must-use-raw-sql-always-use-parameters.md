---
skill_id: f0e069fd0fe3
usage_count: 1
last_used: 2026-06-16
---
# If you must use raw SQL, always use parameters
User.objects.raw(
    'SELECT * FROM users WHERE email = %s AND status = %s',
    [user_input_email, status]
)
```