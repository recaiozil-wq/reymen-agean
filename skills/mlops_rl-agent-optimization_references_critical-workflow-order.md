---
name: mlops_rl-agent-optimization_references_critical-workflow-order
description: Critical Workflow Order
title: "Mlops Rl Agent Optimization References Critical Workflow Order"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Critical Workflow Order |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Critical Workflow Order

Discovered empirically 14 June 2026 after a 622-skill seed produced 4.3% accuracy.

```
CORRECT ORDER:    reward_validation → fix_reward → seed_gradually → test_shadow → deploy
WRONG ORDER:      seed_all → test → find_empty_reward → backtrack
```

The wrong order wastes days. Validate the reward function first because:
- A bad reward function corrupts every MAB update (beta values inflate from false negatives)
- You cannot tell if MAB is bad or the reward signal is bad without separate validation
- Seeding 622 skills with neutral priors sounds productive but just turns MAB into a random selector (all arms equal)
