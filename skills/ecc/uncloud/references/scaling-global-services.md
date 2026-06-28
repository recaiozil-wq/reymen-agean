---
skill_id: 5705f96a41ed
usage_count: 1
last_used: 2026-06-16
---
## Scaling & Global Services

```bash
uc scale web 5    # 5 replicas (spread across machines)
uc scale web 1    # Scale down
```

```yaml
services:
  caddy:
    deploy:
      mode: global   # One container on every machine
```

---