---
skill_id: 43d710cec73f
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Docker secrets (Swarm mode)
secrets:
  db_password:
    file: ./secrets/db_password.txt

services:
  db:
    secrets:
      - db_password