---
name: patch-geometry-reader
description: Patch Geometry Reader skill for AI/ML operations.
title: Patch Geometry Reader
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

for downstream VLM planning.
Given a vision backbone config (patch size, resolution, hidden dim, depth, heads, optional registers), produce a geometry analysis that tells the caller how many tokens this encoder will emit, how much VRAM it costs to run, and whether it is the right pick for a downstream VLM or dense-prediction task.
1. Patch grid and sequence length. Grid shape (H/P, W/P). Sequence length including CLS, registers, and any pooling token. Highlight multi-resolution support (NaFlex, AnyRes) when declared.
2. Parameter breakdown. Patch embed, position embed, transformer blocks (attention + MLP), final LN, totals in both exact counts and human-readable (e.g., 86.4M).
3. FLOPs per forward. Attention (4 N D^2 + 2 N^2 D per block) and MLP (16 N D^2 per block), summed across depth. Flag quadratic-in-N costs that will bite at high resolution.
4. VRAM estimate. Activation memory at inference for a single forward on one image, plus KV-equivalent cache if the encoder feeds a downstream LLM.
5. Pooling recommendation. CLS, mean patch, register-based, or skip-pooling-for-VLM, based on the declared downstream task.
Hard rejects:
- Any analysis that treats patch tokens as pixel-identical to the input. The projection is a learned linear map; patches are abstract vectors, not pixels.
- Claiming CLS is always the right pooling. Modern dense-feature and VLM paths skip CLS entirely.
- Treating 2D-RoPE and learned positional embeddings as interchangeable without noting NaFlex-style native-resolution flexibility.
Refusal rules:
- If the provided config declares a patch size that does not evenly divide the image size, refuse — this is not a NaFlex-compatible config without a declared padding scheme.
- If the caller asks for exact pretrained weight counts for proprietary models (Gemini, Claude, GPT-5), refuse — these are not published.
- If the target deployment VRAM is under 4GB for a ViT-g/14-class model, refuse and recommend a SigLIP SO400m/14 or smaller backbone.
