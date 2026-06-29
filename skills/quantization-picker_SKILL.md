---
name: quantization-picker
description: Quantization Picker skill for AI/ML operations.
title: Quantization Picker
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

quality tolerance, and produce a calibration + validation plan.
Given hardware (CPU / H100 / H200 / B200 / GB200, with count), engine (llama.cpp / vLLM / TRT-LLM / SGLang), model (size + task type — routine chat / reasoning / code / multi-LoRA), and quality tolerance (can absorb N-point drop on HumanEval / MATH / MMLU), pick a quantization format and produce a validation plan.
1. Format recommendation. One of: GGUF Q4_K_M, GGUF Q5_K_M, GPTQ-Int4 + Marlin, AWQ-Int4 + Marlin, FP8, NVFP4 + FP8 KV, or a stacked combo. Justify by the decision tree: CPU → GGUF; reasoning → FP8; multi-LoRA on vLLM → GPTQ; routine GPU chat → AWQ; Blackwell validated → NVFP4.
2. Memory budget. Report weights + KV cache (at reported concurrency × context) + activations. Confirm it fits on the target GPU or call out multi-GPU requirement.
3. Calibration plan. Dataset source (domain-matched for AWQ/GPTQ; generic C4/WikiText as a last resort). Sample count (500-2000 for domain). Validation set (10% held out from calibration pool).
4. Validation plan. Eval set matched to task: HumanEval for code, MATH/MMLU for reasoning, MT-Bench for chat. Baseline BF16 vs quantized. Ship if drop ≤ quality tolerance.
5. KV cache decision. Separate from weight quantization. Recommend FP8 KV for reasoning; BF16 KV if attention accuracy is marginal; INT8 KV only after validation.
6. Rollback path. Keep BF16/FP8 weights on disk; flag to switch back if production quality degrades.
Hard rejects:
- Recommending NVFP4 weights on reasoning-heavy workloads without eval-set validation.
- Calibrating on generic web data for domain models. Always use in-domain.
- Forgetting the KV cache in HBM budget. Always itemize.
- Claiming throughput numbers without naming the kernels (Marlin-AWQ vs plain AWQ is 10x).
Refusal rules:
- If the workload is inherently quality-marginal (open-ended creative generation, edge-case reasoning), refuse aggressive INT4. Stay FP8 or BF16.
- If the engine is llama.cpp, refuse any format other than GGUF. Matching format to engine is table stakes.
- If the user cannot run a 1,000-sample eval, refuse. No blind quantization in production.
