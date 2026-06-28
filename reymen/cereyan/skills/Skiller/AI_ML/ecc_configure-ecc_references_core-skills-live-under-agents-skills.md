---
name: ecc_configure-ecc_references_core-skills-live-under-agents-skills
description: Core skills live under .agents/skills/
title: "Ecc Configure Ecc References Core Skills Live Under Agents Skills"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Core skills live under .agents/skills/ |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Core skills live under .agents/skills/
cp -R "$ECC_ROOT/.agents/skills/<skill-name>" "$TARGET/skills/"
