---
skill_id: 5dc6e73d8d1b
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Always set requests and limits
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"