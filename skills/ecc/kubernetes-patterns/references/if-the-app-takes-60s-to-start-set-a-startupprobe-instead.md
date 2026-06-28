---
skill_id: a71caac080bf
usage_count: 1
last_used: 2026-06-16
---
# If the app takes 60s to start, set a startupProbe instead
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 60   # BAD: Arbitrary wait, race condition
```

---