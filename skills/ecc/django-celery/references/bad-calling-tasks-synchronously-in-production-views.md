---
skill_id: 18356a45c1be
usage_count: 1
last_used: 2026-06-16
---
# BAD: Calling tasks synchronously in production views
result = generate_report.apply()      # Blocks the request thread