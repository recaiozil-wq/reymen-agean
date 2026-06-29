---
name: mlops_rl-agent-optimization_references_log-and-return
description: Log and return
title: "Mlops Rl Agent Optimization References Log And Return"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Log and return |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Log and return
    log_decision(query, mab_action, rule_based=False)
    return mab_action, False
```

**Threshold tuning rule of thumb:**
- Above 0.80: MAB starves (<10% decisions), learns too slowly
- 0.70-0.80: balanced (15-25% MAB), good for initial learning
- Below 0.65: MAB dominates, rules become irrelevant
- Start high (0.80), lower after 50+ MAB decisions show >60% accuracy
- Never set below 0.55 — rules are the safety net

### Phase 4.5 — Skill Seed (v2.3 — 14 June 2026, staged deployment)

**Problem (v2.1):** MAB only knew skills that had been used before. A never-used skill could never be chosen, creating a cold-start trap per skill rather than per system.

**Initial approach (v2.1, abandoned):** Pre-seed all 622 skills into the MAB engine with neutral priors. Shadow test showed 4.3% accuracy — all arms equal meant Thompson Sampling was a random selector.

**Actual approach (v2.3, deployed per user instruction):** Staged seeding. Seed one category at a time (windows-shortcuts, ~10-15 skills) as a pilot, shadow-test for 50+ queries, then expand to the next category. A narrow but proven set beats a wide but flat one.

**Current seed (14 June 2026):** 44 skills in `skill_seed.json`:
- 29 active skills (with usage data from log, total>0)
- 15 windows-shortcuts seeded as pilot (total=0, neutral alpha=1/beta=1)

**Mechanism:**
```python
