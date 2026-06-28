---
skill_id: 1662ce2c2b80
usage_count: 1
last_used: 2026-06-16
---
# Re-run a failed workflow
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun