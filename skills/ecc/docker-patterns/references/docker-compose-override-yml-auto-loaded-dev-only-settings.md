---
skill_id: ae67d5a1bf02
usage_count: 1
last_used: 2026-06-16
---
# docker-compose.override.yml (auto-loaded, dev-only settings)
services:
  app:
    environment:
      - DEBUG=app:*
      - LOG_LEVEL=debug
    ports:
      - "9229:9229"                   # Node.js debugger