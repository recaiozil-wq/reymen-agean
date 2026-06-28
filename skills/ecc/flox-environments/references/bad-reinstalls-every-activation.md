---
skill_id: 7c8b5bc54f59
usage_count: 1
last_used: 2026-06-16
---
# BAD — reinstalls every activation
[hook]
on-activate = """
  pip install -r requirements.txt
"""