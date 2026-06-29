---
name: ecc_jira-integration_references_1-get-available-transitions
description: 1.
title: "Ecc Jira Integration References 1 Get Available Transitions"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_jira-integration_references_1-get-available-transitions.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# 1. Get available transitions
jira_curl \
  "$JIRA_URL/rest/api/3/issue/PROJ-1234/transitions" | jq '.transitions[] | {id, name: .name}'
