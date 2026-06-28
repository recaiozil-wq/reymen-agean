---
skill_id: 91bfc530a7b6
usage_count: 1
last_used: 2026-06-16
---
# BAD practices
- Running as root
- Using :latest tags
- Copying entire repo in one COPY layer
- Installing dev dependencies in production image
- Storing secrets in image (use env vars or secrets manager)
```