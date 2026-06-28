---
skill_id: de7d6d760ca1
usage_count: 1
last_used: 2026-06-16
---
# Large files accidentally staged
git diff main...HEAD --stat | sort -t'|' -k2 -rn | head -10