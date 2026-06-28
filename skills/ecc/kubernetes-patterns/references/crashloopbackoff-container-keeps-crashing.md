---
skill_id: b8efe6e17530
usage_count: 1
last_used: 2026-06-16
---
# CrashLoopBackOff: container keeps crashing
kubectl logs <pod-name> --previous -n my-namespace  # Check crash logs
kubectl describe pod <pod-name> -n my-namespace     # Check exit code & OOMKilled