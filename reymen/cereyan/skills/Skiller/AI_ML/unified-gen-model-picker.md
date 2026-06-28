---
name: unified-gen-model-picker
description: Unified Gen Model Picker skill for AI/ML operations.
title: Unified Gen Model Picker
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

that needs both multimodal understanding and generation with open weights.
Given a product that needs unified understanding + generation (VQA, captioning, T2I, optionally inpainting) with an open-weights constraint and a latency budget, pick a model family and emit a reference configuration.
1. Family verdict. Show-o (masked discrete diffusion), Transfusion / MMDiT (continuous diffusion), Emu3 / Chameleon (autoregressive discrete), or Janus-Pro (decoupled encoders).
2. Inference-step budget. 16 steps for Show-o, 20 for Transfusion, 1024+ for Emu3. Justify the pick with user's latency budget.
3. Inpainting support. Show-o is free; Transfusion adds a mask channel; Emu3 needs a separate fine-tune. Flag this for the user.
4. Tokenizer pick. For discrete families, recommend IBQ / MAGVIT-v2 / SBER; for continuous, recommend SD3's VAE.
5. Training stability. Two-loss (Transfusion) needs weight tuning; Show-o's single loss is cleaner.
6. Migration path if user grows. From Show-o to Transfusion when quality becomes the limit.
Hard rejects:
- Proposing Emu3 / Chameleon when inference latency is <10s per image. Autoregressive over ~1024 tokens is too slow.
- Claiming Show-o matches Transfusion on frontier image quality. It does not. The tokenizer is the ceiling.
- Recommending Stable Diffusion for a product that needs VQA. SD cannot reason about images.
Refusal rules:
- If the user wants <2s per image generation, refuse Show-o and recommend Stable Diffusion + a separate VLM for understanding. Accept the multi-model complexity.
- If user wants "best-in-class quality" with open weights, refuse Show-o / Emu3 and recommend Transfusion-family (MMDiT) or JanusFlow.
- If user cannot commit to a tokenizer (fears licensing, quality ceiling), refuse discrete-only families and recommend Transfusion.
