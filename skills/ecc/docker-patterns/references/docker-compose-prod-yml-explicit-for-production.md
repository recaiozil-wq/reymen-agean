---
skill_id: ceb504563793
usage_count: 1
last_used: 2026-06-16
---
# docker-compose.prod.yml (explicit for production)
services:
  app:
    build:
      target: production
    restart: always
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
```

```bash