---
skill_id: 1f1a9d6aca16
usage_count: 1
last_used: 2026-06-16
---
# 2. Run as non-root
RUN addgroup -g 1001 -S app && adduser -S app -u 1001
USER app