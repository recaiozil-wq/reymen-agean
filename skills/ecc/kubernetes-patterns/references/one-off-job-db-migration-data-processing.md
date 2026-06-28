---
skill_id: efa0f83316ba
usage_count: 1
last_used: 2026-06-16
---
# One-off Job (DB migration, data processing)
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  namespace: my-namespace
spec:
  backoffLimit: 3          # Retry up to 3 times on failure
  ttlSecondsAfterFinished: 3600   # Auto-delete after 1h
  template:
    spec:
      restartPolicy: OnFailure    # Never for Jobs (not Always)
      containers:
        - name: migrate
          image: ghcr.io/org/my-app:1.0.0
          command: ["python", "manage.py", "migrate"]
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
```

```yaml