---
skill_id: 3220d64bf18c
usage_count: 1
last_used: 2026-06-16
---
# then liveness/readiness take over
startupProbe:
  httpGet:
    path: /health
    port: 8080
  failureThreshold: 30  # 30 * 5s = 150s max startup time
  periodSeconds: 5

livenessProbe:
  httpGet:
    path: /health
    port: 8080
  periodSeconds: 30
  failureThreshold: 3   # 3 * 30s = 90s before restart

readinessProbe:
  httpGet:
    path: /ready         # Separate endpoint: checks DB, cache, etc.
    port: 8080
  periodSeconds: 10
  failureThreshold: 2
```

```yaml