---
skill_id: 10fd7de16ee6
usage_count: 1
last_used: 2026-06-16
---
# 5. No secrets in image layers
```

### Compose Security

```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE          # Only if binding to ports < 1024
```

### Secret Management

```yaml