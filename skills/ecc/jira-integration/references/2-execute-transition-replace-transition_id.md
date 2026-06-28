---
skill_id: 712f5c05dbe2
usage_count: 1
last_used: 2026-06-16
---
# 2. Execute transition (replace TRANSITION_ID)
jira_curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"transition": {"id": "TRANSITION_ID"}}' \
  "$JIRA_URL/rest/api/3/issue/PROJ-1234/transitions"
```

### Search with JQL

```bash
jira_curl -G \
  --data-urlencode "jql=project = PROJ AND status = 'In Progress'" \
  "$JIRA_URL/rest/api/3/search"
```