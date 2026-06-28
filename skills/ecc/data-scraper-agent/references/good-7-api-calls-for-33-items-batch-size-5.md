---
skill_id: de6708f3f76e
usage_count: 1
last_used: 2026-06-16
---
# GOOD: 7 API calls for 33 items (batch size 5)
for batch in chunks(items, size=5):
    results = call_ai(batch)  # 7 calls → stays within free tier
```

---