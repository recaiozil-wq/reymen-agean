---
skill_id: 7c24d02accc2
usage_count: 1
last_used: 2026-06-16
---
# --- Port-forward for local debugging ---
kubectl port-forward pod/<pod-name> 8080:8080 -n my-namespace
kubectl port-forward svc/my-app 8080:80 -n my-namespace