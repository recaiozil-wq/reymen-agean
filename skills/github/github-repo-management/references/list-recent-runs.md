---
skill_id: 288f05e3a739
usage_count: 1
last_used: 2026-06-16
---
# List recent runs
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin)['workflow_runs']:
    print(f\"  Run {r['id']}  {r['name']:30}  {r['conclusion'] or r['status']}\")"