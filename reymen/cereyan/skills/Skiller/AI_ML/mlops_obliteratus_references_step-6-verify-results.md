---
name: mlops_obliteratus_references_step-6-verify-results
description: "Step 6: Verify Results"
title: "Mlops Obliteratus References Step 6 Verify Results"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Step 6: Verify Results |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Step 6: Verify Results

After abliteration, check the output metrics:

| Metric | Good Value | Warning |
|:-------|:-----------|:--------|
| Refusal rate | < 5% (ideally ~0%) | > 10% means refusals persist |
| Perplexity change | < 10% increase | > 15% means coherence damage |
| KL divergence | < 0.1 | > 0.5 means significant distribution shift |
| Coherence | High / passes qualitative check | Degraded responses, repetition |

### If refusals persist (> 10%)
1. Try `aggressive` method
2. Increase `--n-directions` (e.g., 8 or 16)
3. Add `--refinement-passes 3`
4. Try `--direction-method svd` instead of diff_means

### If coherence is damaged (perplexity > 15% increase)
1. Reduce `--n-directions` (try 2)
2. Increase `--regularization` (try 0.3)
3. Reduce `--refinement-passes` to 1
4. Try `basic` method (gentler)
