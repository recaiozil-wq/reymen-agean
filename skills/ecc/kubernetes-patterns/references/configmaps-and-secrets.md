---
skill_id: 872fefc9aeab
usage_count: 1
last_used: 2026-06-16
---
## ConfigMaps and Secrets

### ConfigMap — Non-sensitive configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
  namespace: my-namespace
data:
  LOG_LEVEL: "info"
  APP_ENV: "production"
  MAX_CONNECTIONS: "100"