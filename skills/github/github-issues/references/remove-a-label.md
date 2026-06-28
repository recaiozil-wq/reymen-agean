---
skill_id: c22e1c2a4305
usage_count: 1
last_used: 2026-06-16
---
# Remove a label
curl -s -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels/needs-triage