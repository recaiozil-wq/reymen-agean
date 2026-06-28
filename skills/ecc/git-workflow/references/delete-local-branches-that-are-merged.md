---
skill_id: 23cb5b3d792e
usage_count: 1
last_used: 2026-06-16
---
# Delete local branches that are merged
git branch --merged main | grep -v "^\*\|main" | xargs -n 1 git branch -d