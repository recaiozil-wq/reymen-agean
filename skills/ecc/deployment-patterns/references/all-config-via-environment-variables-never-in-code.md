---
skill_id: 160e2b09af1c
usage_count: 1
last_used: 2026-06-16
---
# All config via environment variables — never in code
DATABASE_URL=postgres://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
API_KEY=${API_KEY}           # injected by secrets manager
LOG_LEVEL=info
PORT=3000