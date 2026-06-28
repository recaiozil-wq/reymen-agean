---
skill_id: cb121dbbdce2
usage_count: 1
last_used: 2026-06-16
---
# 1. ServiceAccount — enable token for this SA
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
automountServiceAccountToken: true    # Token required: app calls K8s API
```

```yaml