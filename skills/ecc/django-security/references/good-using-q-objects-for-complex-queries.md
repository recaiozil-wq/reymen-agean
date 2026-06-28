---
skill_id: 7ed99ddfa708
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Using Q objects for complex queries
from django.db.models import Q
def search_users_complex(query):
    return User.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query)
    )  # Safe
```

### Extra Security with raw()

```python