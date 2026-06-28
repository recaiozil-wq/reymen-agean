---
skill_id: 0203d4752570
usage_count: 1
last_used: 2026-06-16
---
# BAD — hook functions aren't available in the interactive shell
[hook]
on-activate = """
  deploy() { kubectl apply -f k8s/; }
"""