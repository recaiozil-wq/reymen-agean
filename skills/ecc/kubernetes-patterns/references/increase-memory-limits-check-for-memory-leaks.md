---
skill_id: 27e191eb7d5c
usage_count: 1
last_used: 2026-06-16
---
# Increase memory limits, check for memory leaks
kubectl describe pod <pod-name> -n my-namespace | grep -A5 "Last State"
```

---