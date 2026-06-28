---
name: mtp-planner
description: Mtp Planner skill for AI/ML operations.
title: Mtp Planner
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

Given a pre-training run specification (model scale, hidden size, layers, data tokens budget, GPU topology, target deployment) and a stated goal (denser training signal vs speculative-decoding draft vs both), produce an MTP integration plan.
1. Depth D. Pick 1 or 2. DeepSeek-V3 uses D=1 and reports the first-depth speculative-decoding acceptance at 80%+. D=2 is diminishing-returns territory for most runs. Justify the choice against compute budget — each extra depth adds roughly one transformer block of compute per training step.
2. Lambda schedule. Default: 0.3 for the first 10% of training, 0.1 afterward. Adjust up to 0.5 early for small models (under 7B) where the denser signal matters more; adjust down if you observe the MTP loss dominating the main loss.
3. Parameter budget. Report per-module parameter count against the main model. Confirm overhead is under 5% of main parameters (dense) or under 3% (MoE).
4. Memory and compute overhead. Quantify extra forward-pass FLOPs per step (roughly `D * transformer_block_cost`), extra backward-pass memory (activation memory for D modules), and extra peak VRAM (shared embedding and head do not count, projection and transformer block do).
5. Inference-time wiring. Describe how to consume the MTP module as a speculative-decoding draft at inference. Name the Leviathan rule integration path and the KV-rollback bookkeeping. Confirm compatibility with the target inference stack (vLLM, SGLang, TensorRT-LLM).
Hard rejects:
- Adding MTP to a dense model pre-trained without it. Cannot retrofit — the MTP modules are not trained.
- D > 2 for a first integration. Gain over D=1 is small; complexity grows quickly.
- MTP on a model under 1B active parameters. Signal is weaker than the overhead cost at that scale.
- Using parallel (Gloeckle-style) heads when the goal is speculative decoding. They do not chain causally.
Refusal rules:
- If the pre-training data is dominated by short sequences (under 2k), refuse. MTP gains assume sequences long enough for depth-2 supervision to matter.
- If the target inference stack does not support speculative decoding at all, note that MTP still buys the denser training signal and proceed, but flag the mismatch.
- If the user is continuing pre-training on an existing dense checkpoint without MTP, refuse and recommend adding MTP only at the start of a clean training run or at a clean data-boundary reset.
