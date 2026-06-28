---
name: onevision-budget-planner
description: Onevision Budget Planner skill for AI/ML operations.
title: Onevision Budget Planner
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

multi-image, and video scenarios for a target product mix.
Given a product's expected task distribution — percentages of single-image, multi-image, and video requests — and a per-sample visual-token budget, emit a per-scenario allocation plan and a training curriculum.
1. Per-scenario config. Single-image: AnyRes tile count + thumbnail + pooling factor; multi-image: images-per-sample + per-image pooling; video: frame count + per-frame pooling.
2. Token budget balance. Each scenario's total tokens should land within ±30% of the target budget; flag any scenario that falls below 70% of target (under-tokenized) or above 130% (context risk).
3. Curriculum plan. Three stages (SI → OV → TT) with data weights. For the TT stage, use the user's product mix.
4. Expected emergent skills. Given the user's product mix, predict which LLaVA-OneVision-style emergent capabilities are likely to appear (multi-camera, set-of-mark, screenshot-agent, or product-specific variants).
5. Training-data ballpark. Approximate token / image / frame counts needed per stage given 7B base LLM, citing OneVision-1.5 data scale.
Hard rejects:
- Proposing stage orders that put video or multi-image before single-image. OneVision shows this loses 2-4 MMMU.
- Allocating all budget to video when the product is 80% single-image. Waste, not balance.
- Assuming AnyRes-16 (4x4 grid) fits in a 4k token budget without aggressive pooling. It does not.
Refusal rules:
- If the per-sample token budget is below 1024, refuse for multi-image or video use cases — below that floor, the scenarios collapse.
- If the user wants 5+ frames of video at full 729-token resolution, refuse; recommend 3x pooling or fewer frames.
- If the product distribution omits single-image entirely, refuse and recommend Qwen2.5-VL-style M-RoPE instead — OneVision's curriculum assumes single-image as the perception base.
