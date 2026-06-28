---
skill_id: 2aab61eb2a36
usage_count: 1
last_used: 2026-06-16
---
# ServiceAccount with token disabled — safest default
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
automountServiceAccountToken: false   # No K8s API token injected into pods
```

```yaml