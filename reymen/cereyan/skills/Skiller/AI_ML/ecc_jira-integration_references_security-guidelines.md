---
name: ecc_jira-integration_references_security-guidelines
description: Security Guidelines
title: "Ecc Jira Integration References Security Guidelines"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_jira-integration_references_security-guidelines.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Security Guidelines

- **Never hardcode** Jira API tokens in source code or skill files
- **Always use** environment variables or a secrets manager
- **Add `.env`** to `.gitignore` in every project
- **Rotate tokens** immediately if exposed in git history
- **Use least-privilege** API tokens scoped to required projects
- **Validate** that credentials are set before making API calls — fail fast with a clear message
