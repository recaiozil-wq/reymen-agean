---
skill_id: f69fbb21dc22
usage_count: 1
last_used: 2026-06-16
---
# Add labels
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels \
  -d '{"labels": ["priority:high", "bug"]}'