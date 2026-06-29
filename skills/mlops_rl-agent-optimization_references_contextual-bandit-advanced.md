---
name: mlops_rl-agent-optimization_references_contextual-bandit-advanced
description: Contextual Bandit (Advanced)
title: "Mlops Rl Agent Optimization References Contextual Bandit Advanced"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Contextual Bandit (Advanced) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Contextual Bandit (Advanced)

When basic MAB plateaus, add context features to differentiate decisions:

**Context features for agent decisions:**
- Query length (short/medium/long)
- Query category (code/security/search/analysis/general)
- Time of day
- Current active mode
- Previous 3 queries' categories

Each context gets its own set of bandit arms — the system learns "for long code queries, skill X is best" separately from "for short general queries, no skill is best."
