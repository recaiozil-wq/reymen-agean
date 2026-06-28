---
skill_id: 88e343cd0052
usage_count: 1
last_used: 2026-06-16
---
# Metrics (if enabled)
curl http://localhost:8080/q/metrics
```

Expected responses:
```json
{
  "status": "UP",
  "checks": [
    {
      "name": "Database connection",
      "status": "UP"
    }
  ]
}
```