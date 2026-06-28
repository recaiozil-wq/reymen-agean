---
skill_id: 3471eec28f4f
usage_count: 1
last_used: 2026-06-16
---
# BAD: restartPolicy: Always in a Job (causes infinite restart loop)
spec:
  restartPolicy: Always   # Use OnFailure or Never for Jobs
```

---