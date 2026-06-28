---
skill_id: f38f7a0058d6
usage_count: 1
last_used: 2026-06-16
---
## Direct REST API Reference

### Fetch a Ticket

```bash
jira_curl \
  -H "Content-Type: application/json" \
  "$JIRA_URL/rest/api/3/issue/PROJ-1234" | jq '{
    key: .key,
    summary: .fields.summary,
    status: .fields.status.name,
    priority: .fields.priority.name,
    type: .fields.issuetype.name,
    assignee: .fields.assignee.displayName,
    labels: .fields.labels,
    description: .fields.description
  }'
```

### Fetch Comments

```bash
jira_curl \
  -H "Content-Type: application/json" \
  "$JIRA_URL/rest/api/3/issue/PROJ-1234?fields=comment" | jq '.fields.comment.comments[] | {
    author: .author.displayName,
    created: .created[:10],
    body: .body
  }'
```

### Add a Comment

```bash
jira_curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "version": 1,
      "type": "doc",
      "content": [{
        "type": "paragraph",
        "content": [{"type": "text", "text": "Your comment here"}]
      }]
    }
  }' \
  "$JIRA_URL/rest/api/3/issue/PROJ-1234/comment"
```

### Transition a Ticket

```bash