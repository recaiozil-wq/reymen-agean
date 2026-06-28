---
skill_id: 2a7280c6aa14
usage_count: 1
last_used: 2026-06-16
---
# View current protection
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection