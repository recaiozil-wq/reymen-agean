---
name: ecc_agentic-os_references_bad-routing-logic-in-code-instead-of-markdown-tables
description: BAD - Routing logic in code instead of markdown tables
title: "Ecc Agentic Os References Bad Routing Logic In Code Instead Of Markdown Tables"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | BAD - Routing logic in code instead of markdown tables |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# BAD - Routing logic in code instead of markdown tables
if (intent.includes('deploy')) { agent = opsAgent; }
```

Keep routing declarative in `CLAUDE.md` markdown tables. It is inspectable, editable, and debuggable.
