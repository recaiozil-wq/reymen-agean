---
name: ecc_agentic-os_references_bad-api-keys-in-agent-files-or-claude-md
description: BAD - API keys in agent files or CLAUDE.md
title: "Ecc Agentic Os References Bad Api Keys In Agent Files Or Claude Md"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | BAD - API keys in agent files or CLAUDE.md |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# BAD - API keys in agent files or CLAUDE.md
Your OpenAI API key is sk-xxxxxxxx
```

Use environment variables or a `.env` file loaded by scripts. Agents reference `process.env.API_KEY`.

### External Database for Simple State

```markdown
