---
skill_id: 23cd85106e02
usage_count: 1
last_used: 2026-06-16
---
# 1. Get available transitions
jira_curl \
  "$JIRA_URL/rest/api/3/issue/PROJ-1234/transitions" | jq '.transitions[] | {id, name: .name}'