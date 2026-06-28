---
name: modality-bridge-picker
description: Modality Bridge Picker skill for AI/ML operations.
title: Modality Bridge Picker
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

configuration given token budget, quality target, and training compute.
Given a vision encoder's token count per image, the LLM's context budget, the target number of images per prompt, and the training compute budget, recommend which modality bridge to use and justify with parameter counts and token economics.
1. Token budget audit. Report raw tokens per image from the vision encoder, tokens per image after each bridge option, and the fraction of LLM context consumed at declared image-per-prompt counts.
2. Bridge comparison. For each of Q-Former (32 tokens, ~188M params), MLP projector (all patches, ~20M params), and Perceiver resampler (K learnable queries via N-layer cross-attention, variable), give parameters, quality proxies, and training cost ballpark.
3. Recommendation. Single best choice for the stated constraints, with one-line justification. Flag when the constraints are contradictory (high quality + tight token budget + low training compute).
4. Two-stage training trace. If Q-Former is picked, outline ITC + ITM + ITG losses for stage 1 and LM loss for stage 2. Name a representative dataset for each (COCO, LAION, Visual Genome).
5. Ablation checklist. Five experiments the caller should run before locking the bridge (query count, two-stage vs single-stage, projector depth, freeze schedule, finetune subset).
Hard rejects:
- Any recommendation that ignores the token budget. "Use MLP" with 576 tokens per image fails at 10 images in a 4k context.
- Claiming Q-Former strictly dominates MLP. At single-image high-quality tasks with unlimited context, MLP wins.
- Treating Perceiver resampler as equivalent to Q-Former. Flamingo applies it at every LLM layer; BLIP-2 applies it once.
Refusal rules:
- If the caller asks for a bridge that can handle video without specifying how many frames and at what frame rate, refuse — video bridges differ from single-image bridges by specification, not just scale.
- If the LLM in scope is trained from scratch with the vision tower (early-fusion, Chameleon-style), refuse — Lesson 12.11 covers that case separately.
- If no training compute is stated, refuse and ask whether the caller can afford stage 2 of BLIP-2 (~a few hundred A100-hours) or only projector-only training.
