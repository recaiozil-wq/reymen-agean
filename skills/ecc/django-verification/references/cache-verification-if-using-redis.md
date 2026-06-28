---
skill_id: 9864ae447249
usage_count: 1
last_used: 2026-06-16
---
# Cache verification (if using Redis)
python -c "from django.core.cache import cache; cache.set('test', 'value', 10); print(cache.get('test'))"
```