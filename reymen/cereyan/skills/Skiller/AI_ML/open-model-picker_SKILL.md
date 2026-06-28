---
name: open-model-picker
description: Open Model Picker skill for AI/ML operations.
title: Open Model Picker
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

deployment target.
Given a deployment target (GPU type, VRAM per GPU, number of GPUs, target context length, target p50/p99 latency, peak concurrent requests) and a task profile (chat, code, reasoning, long-context retrieval, tool use), recommend an open model plus serving stack with explicit reasoning about each of the six architectural knobs from Lesson 14.
1. Model shortlist. Three candidates, each with total params, active params (MoE-aware), architecture flags (norm / activation / position / attention / MoE / context), and the single reason it made the shortlist.
2. Memory budget check. For the top candidate: weight memory at BF16 and at the chosen quantization; KV cache at target context for the target batch size; activation headroom. Halt the recommendation if weights + KV cache + activations exceed available VRAM.
3. Quantization choice. GPTQ-4bit, AWQ-4bit, FP8, or BF16. Justify against accuracy sensitivity of the task (code / math / reasoning tasks take a bigger hit from aggressive quantization than chat or retrieval).
4. Inference stack. vLLM, TensorRT-LLM, SGLang, or llama.cpp. Justify against: continuous batching need, speculative decoding support, quantization format compatibility, and single-node vs multi-node topology.
5. Throughput sanity check. Prefill tokens/sec and decode tokens/sec estimates based on GPU memory bandwidth (decode) and TFLOPs (prefill). Reject the recommendation if decode throughput is below the target's concurrent-user floor.
6. Fallback. Second choice if the top candidate exceeds VRAM or throughput budget. Always name one.
Hard rejects:
- Dense models above 30B on a single 24GB consumer GPU without offloading or aggressive quantization.
- MoE models on a serving stack without expert-parallel support.
- Long-context (128k+) on architectures without GQA or MLA (KV cache explodes).
- Any recommendation that does not name the specific model revision (e.g., "Llama 3 8B Instruct v3.1", not "Llama 3").
