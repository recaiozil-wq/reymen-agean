---
skill_id: 50792b9ff8ee
usage_count: 1
last_used: 2026-06-16
---
# Immediately update cache
    cache_key = f"product:{product_id}"
    r.setex(cache_key, 3600, json.dumps(data))
```

### Cache Invalidation

```python