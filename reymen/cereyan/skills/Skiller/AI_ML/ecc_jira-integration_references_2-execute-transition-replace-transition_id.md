---
name: ecc_jira-integration_references_2-execute-transition-replace-transition_id
description: 2.
title: "Ecc Jira Integration References 2 Execute Transition Replace Transition Id"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_jira-integration_references_2-execute-transition-replace-transition_id.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

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
