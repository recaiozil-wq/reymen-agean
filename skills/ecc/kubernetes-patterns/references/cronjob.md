---
skill_id: 3d81add95b39
usage_count: 1
last_used: 2026-06-16
---
# CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup-job
  namespace: my-namespace
spec:
  schedule: "0 2 * * *"         # 2am daily
  concurrencyPolicy: Forbid      # Don't run if previous still running
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: cleanup
              image: ghcr.io/org/cleanup:1.0.0
              resources:
                requests:
                  cpu: "50m"
                  memory: "64Mi"
```

---