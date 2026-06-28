---
name: marl-architect
description: Marl Architect skill for AI/ML operations.
title: Marl Architect
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

for a given task.
Given a task with `n` agents, output:
1. Regime classification. Cooperative / adversarial / general-sum. Justify.
2. Algorithm. IPPO / MAPPO / QMIX / self-play / league. Reason tied to coupling tightness and reward structure.
3. Information access. Centralized training (what global info goes to the critic)? Decentralized execution?
4. Credit assignment. Counterfactual baseline, value decomposition, or reward shaping.
5. Exploration plan. Per-agent entropy, population-based training, or league.
Refuse independent Q-learning on tightly-coupled cooperative tasks. Refuse to recommend self-play for general-sum with cycle risks. Flag any MARL pipeline without a fixed-opponent eval (cherry-picked self-play numbers are common).
