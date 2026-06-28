---
skill_id: 055fb8a19563
usage_count: 1
last_used: 2026-06-16
---
# Reference in Deployment — no token, no API access
spec:
  template:
    spec:
      serviceAccountName: my-app-sa
      automountServiceAccountToken: false   # Belt-and-suspenders: also set at pod level
```

#### Pattern B — App DOES need the Kubernetes API (operators, controllers, config watchers)

Enable the token and grant only the permissions actually required.

```yaml