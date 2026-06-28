---
skill_id: c9b06bd50548
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Use environment variables (injected at runtime)
services:
  app:
    env_file:
      - .env                     # Never commit .env to git
    environment:
      - API_KEY                  # Inherits from host environment