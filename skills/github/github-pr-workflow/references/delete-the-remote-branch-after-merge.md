---
skill_id: 29f1b08d221c
usage_count: 1
last_used: 2026-06-16
---
# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH