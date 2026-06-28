---
skill_id: 716f6b30598b
usage_count: 1
last_used: 2026-06-16
---
# Close
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  -d '{"state": "closed", "state_reason": "completed"}'