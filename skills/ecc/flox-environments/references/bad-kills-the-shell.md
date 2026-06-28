---
skill_id: b11b5f4cdd84
usage_count: 1
last_used: 2026-06-16
---
# BAD — kills the shell
[hook]
on-activate = """
  if [ ! -f config.json ]; then
    echo "Missing config"
    exit 1
  fi
"""