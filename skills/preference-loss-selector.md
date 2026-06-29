---
name: preference-loss-selector
description: Preference Loss Selector skill for AI/ML operations.
title: Preference Loss Selector
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

stage.
Given a preference dataset description (paired vs unpaired, preference-strength distribution, length distribution, size) and a training target (one-stage from base, two-stage after SFT, on-policy continuation), recommend a loss from the DPO family and name the single failure mode it protects against.
1. Dataset fingerprint. Paired? Unpaired? Length-balanced? Preference-strength variance? Mostly in-distribution or open-domain? Pick the most informative 4 fields for this dataset.
2. Loss recommendation. From {DPO, IPO, KTO, SimPO, ORPO, BPO}. One primary and one fallback. For each, name the specific failure mode it protects against on this dataset.
3. Hyperparameter defaults. `beta` for anchored methods, `gamma` margin for SimPO, `lambda` for ORPO. Always cite these as starting points for a sweep, never as final values.
4. Red flags in the data. If preference strengths are perfectly uniform, DPO-family methods lose their pairwise signal — recommend collecting calibrated preferences. If average `|y_w| / |y_l|` deviates > 1.5, flag length bias and push toward SimPO.
Hard rejects:
- Any claim that DPO (or any family member) "escapes Goodhart." Rafailov et al. (NeurIPS 2024) prove direct alignment algorithms over-optimize on the same gold-reward curve shape as explicit-RM RLHF.
- Any recommendation that does not specify held-out capability evaluation alongside preference evaluation. Direct alignment algorithms still need gold-signal benchmarks.
- Any claim that reference-policy-free methods (SimPO, ORPO) "don't need regularization." The SFT-like term or length penalty is the regularizer.
Refusal rules:
- If the dataset is smaller than 5k pairs and the user targets a frontier-scale model, refuse and recommend expanding the dataset or using an SFT-first approach.
- If the user requests "the best" loss, refuse and explain no closed-form winner exists — the right method depends on dataset shape and task.
