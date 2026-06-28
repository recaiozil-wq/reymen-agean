---
skill_id: d52cf35bd782
usage_count: 1
last_used: 2026-06-16
---
# Re-run only failed jobs
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun-failed-jobs