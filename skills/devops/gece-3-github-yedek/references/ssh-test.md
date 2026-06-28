---
skill_id: 24188b7ca4b2
usage_count: 1
last_used: 2026-06-16
---
# SSH test
ssh -T git@github.com 2>&1 | grep -q "successfully authenticated" && echo "SSH OK"